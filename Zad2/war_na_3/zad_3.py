import numpy as np
import matplotlib; matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.interpolate import interp1d
from scipy.spatial import distance



# wagi - współrzędne punktu

# TODO:
#   Pokonać problem martwych neuronów
#   przeczytać uważnie całą prezentację
#   dodac animacje

class KohonenOrNeuralGas:
    # alfa - wpsolczynnik uczenia, neighbourhood_radius - to co we wzorach jest opisane lambda
    # dla kazdej metody to nieco inne jest ale generalnie uzywane w liczeniu tego G(i, x) co jest we wzorach

    def __init__(self, input_matrix, neuron_num, is_neural_gas=False,
                 is_gauss=True, alfa=0.6, neighbourhood_radius=0.3, epoch_count=1):
        # liczba neuronów i dane wejsciowe
        self.neuron_num = neuron_num
        self.input_matrix = input_matrix

        # wybór podmetody (gauss) i metody (neural_gas) jesli neural gas - true to gauss nie ma znaczenia
        self.is_gauss = is_gauss
        self.is_neural_gas = is_neural_gas

        # ile epok
        self.epoch_count = epoch_count

        # losujemy startowe pozycje neuronów
        self.map = np.random.normal(np.mean(input_matrix), np.std(input_matrix),
                                    size=(self.neuron_num, len(input_matrix[0])))
        # tutaj pozniej przechowujemy odleglosci odpowiednich neuronów od aktualnie rozpatrywanego wektoru wejściowego
        self.distance_map = np.zeros_like(self.map)

        # wspolczynnik uczenia, max, min i current - zmienia sie w trakcie
        self.alfa_max = alfa
        self.alfa_min = 0.01
        self.current_alfa = self.alfa_max

        # ten drugi wspolczynnik lambda, max, min i current - zmienia sie w trakcie
        self.neighbourhood_radius_max = neighbourhood_radius
        self.neighbourhood_radius_min = 0.01
        self.current_neighbourhood_radius = self.neighbourhood_radius_max

        # uzywamy w 2 miejscach, generalnie srednio potrzebne
        self.num_rows_input_data, self.num_cols_input_data = self.input_matrix.shape

        # aktualny krok i maksymalna liczba kroków (liczba rzędów w wejsciu razy liczba epok)
        # uzywamy maxymalny step i current step do liczenia tych current alfa i current_neighbourhood_radius
        self.current_step = 0
        self.max_step = self.num_rows_input_data * self.epoch_count

        # tutaj przechowujemy błędy liczone po każdej epoce (bardzo wolno liczy się błąd)
        self.quantization_error_list = []

        self.animation_list = []

    # jedna epoka
    def epoch(self):
        np.random.shuffle(self.input_matrix)
        if not self.is_neural_gas:
            for i in self.input_matrix:
                self.change_alpha()
                self.change_neighbourhood_radius()
                # print(self.animation_list)
                self.animation_list.append(np.copy(self.map))

                # klasyczny wariant Kohenena,
                # modyfikacja zwyciezcy oraz znajdujących się o self.current_neighbourhood_radius od niego neuronów
                if not self.is_gauss:
                    self.distance_map_fill(i)
                    smallest_index = np.argmin(self.distance_map)
                    for j in range(len(self.map)):

                        # sprawdzamy czy odległość neuronu od zwycięzcy jest mniejsza niż current_neighbourhood_radius
                        # jesli tak to modyfikujemy zgodnie ze wzorem
                        if distance.euclidean(self.map[j],
                                              self.map[smallest_index]) <= self.current_neighbourhood_radius:
                            self.map[j] = self.map[j] + self.current_alfa * (i - self.map[j])

                # wariant gaussa
                # modyfikacja zwycięzcy oraz wszystkich innych w zależności od ich odległości od zwycięzcy
                else:
                    self.distance_map_fill(i)
                    smallest_index = np.argmin(self.distance_map)
                    for j in range(len(self.map)):
                        self.map[j] = self.map[j] + self.current_alfa \
                                      * self.euclidean_func(self.map[smallest_index], self.map[j]) * (i - self.map[j])

                self.current_step += 1
                if self.current_step % 100 == 0:
                    print("Iteration in epoch nr", self.current_step)

        # metoda gazu neuronowego
        # sortujemy neurony wg odległości od aktualnego wektoru wejścia
        # liczymy zmianę pozycji w zależności od pozycji w rankingu a nie od faktycznej odległosci
        else:
            for i in self.input_matrix:
                self.change_alpha()
                self.change_neighbourhood_radius()
                self.distance_map_fill(i)
                distance_ranking = np.argsort(self.distance_map)
                self.animation_list.append(np.copy(self.map))
                for j in range(len(distance_ranking)):
                    self.map[distance_ranking[j]] = self.map[distance_ranking[j]] \
                                                    + self.current_alfa * self.neural_gass_neighbour_fun(j) * (
                                                            i - self.map[distance_ranking[j]])

                self.current_step += 1
                if self.current_step % 100 == 0:
                    print("Iteration in epoch nr", self.current_step)

    # dla gazu neuronowego zwraca współczynnik związany z rankingiem punktu
    def neural_gass_neighbour_fun(self, ranking):
        return np.exp(-ranking / self.current_neighbourhood_radius)

    # funkcja okreslajaca wspolczynnik zwiazany z odleglością punktów od zwycieskiego
    # dla metody euklidesowej w Kohonenie
    def euclidean_func(self, pos_closest, pos_checked):
        return np.exp(
            -distance.euclidean(pos_checked, pos_closest) ** 2 / (2 * (self.current_neighbourhood_radius ** 2)))

    # zmiana współczynnika lambda
    def change_neighbourhood_radius(self):
        self.current_neighbourhood_radius = self.neighbourhood_radius_max \
                                            * (self.neighbourhood_radius_min / self.neighbourhood_radius_max) \
                                            ** (self.current_step / self.max_step)

    # zmiana współczynnika alfa
    def change_alpha(self):
        self.current_alfa = self.alfa_max * (self.alfa_min / self.alfa_max) ** (self.current_step / self.max_step)

    # nauka + liczymy błędy kwantyzacji
    def train(self):
        for i in range(self.epoch_count):
            self.calculate_quantization_error()
            print("current_quant_error = ", self.quantization_error_list[i])
            self.epoch()
        self.calculate_quantization_error()
        print("current_quant_error = ", self.quantization_error_list[-1])

    # obliczanie błędu kwantyzacji ze wzoru
    def calculate_quantization_error(self):
        print("*calculating quantization error*")
        __sum = 0
        for i in self.input_matrix:
            self.distance_map_fill(i)
            smallest_index = np.argmin(self.distance_map)
            __sum += (self.distance_map[smallest_index]) ** 2
        self.quantization_error_list.append(__sum / self.num_rows_input_data)

    # wypełniamy macierz w której odpowiadające indexy w self.map
    def distance_map_fill(self, point):
        # TODO zmien nazwe zmiennej
        potezna_lista = []
        for i in self.map:
            potezna_lista.append(distance.euclidean(i, point))
        self.distance_map = np.asarray(potezna_lista)

    def animate_training(self):
        fig, ax = plt.subplots()

        ax.axis([np.min(self.animation_list[0], axis=0)[0] - 1, np.max(self.animation_list[0], axis=0)[0] + 1,
                 np.min(self.animation_list[0], axis=0)[1] - 1, np.max(self.animation_list[0], axis=0)[1] + 1])

        ax.plot(self.input_matrix[:, 0], self.input_matrix[:, 1], 'ro')
        l, = ax.plot([], [], 'bo')

        def animate(i):
            if i > len(self.animation_list) - 1:
                i = len(self.animation_list) - 1
            # print(i)
            # print(self.animation_list[i + 1] - self.animation_list[i])
            l.set_data(self.animation_list[i][:, 0], self.animation_list[i][:, 1])
            return l,

        ani = animation.FuncAnimation(fig, animate, interval=100, repeat=False)
        plt.show()
        # fig = plt.figure()
        #
        #
        # def animate(i):
        #     # graph.set_data(self.animation_list[i][:, 0], self.animation_list[i][:, 1])
        #     # graph.set_offsets(np.vstack((self.animation_list[i][:, 0], self.animation_list[i][:, 1])).T)
        #     graph = plt.plot(self.animation_list[0][:, 0], self.animation_list[0][:, 1])
        #     return graph
        #
        # ani = animation.FuncAnimation(fig, animate, repeat=False, interval=200)
        # plt.show()


def read_2d_float_array_from_file(file_name, is_comma=False):
    two_dim_list_of_return_values = []
    with open(file_name, "r") as file:
        lines = file.read().splitlines()
    for i in lines:
        one_dim_list = []
        if not is_comma:
            for j in list(map(float, i.split())):
                one_dim_list.append(j)
            two_dim_list_of_return_values.append(one_dim_list)
        else:
            for j in list(map(float, i.split(","))):
                one_dim_list.append(j)
            two_dim_list_of_return_values.append(one_dim_list)
    return np.asarray(two_dim_list_of_return_values)


def plot(list2d, list2d2=None):
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    if list2d2 is not None:
        for i in list2d2:
            list3.append(i[0])
            list4.append(i[1])
        plt.plot(list3, list4, 'bo', color='red')
    for i in list2d:
        list1.append(i[0])
        list2.append(i[1])
    plt.plot(list1, list2, 'bo')
    plt.show()


def main():
    # kohonen = KohonenOrNeuralGas(input_matrix=read_2d_float_array_from_file("Danetestowe.txt", is_comma=True),
    #                                 neuron_num=200, is_neural_gas=True, epoch_count=1)
    # plot(kohonen.map, read_2d_float_array_from_file("Danetestowe.txt", is_comma=True))
    # kohonen.train()
    # plot(kohonen.map, read_2d_float_array_from_file("Danetestowe.txt", is_comma=True))
    kohonen = KohonenOrNeuralGas(input_matrix=read_2d_float_array_from_file("punkty.txt"), neuron_num=300,
                                 is_gauss=True, is_neural_gas=False, epoch_count=1, neighbourhood_radius=1)
    plot(kohonen.map, read_2d_float_array_from_file("punkty.txt", is_comma=False))
    kohonen.train()
    plot(kohonen.map, read_2d_float_array_from_file("punkty.txt", is_comma=False))
    kohonen.animate_training()


if __name__ == '__main__':
    main()
