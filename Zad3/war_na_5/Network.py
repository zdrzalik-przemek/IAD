import math

import numpy

import K_means as K_means
from scipy.spatial import distance

import matplotlib.pyplot as plt

# wspolczynnik uczenia
eta = 0.1
# momentum
alfa = 0

CLASSYFICATION_ERROR_MARGIN = 0.5


class NeuralNetwork:
    def __repr__(self):
        return "Instance of NeuralNetwork"

    def __str__(self):
        # todo: zaktualizuj to_string()
        if self.is_bias:
            return "hidden_layer (wiersze - neurony) :\n" + str(
                self.hidden_layer) + "\noutput_layer (wiersze - neurony) :\n" + str(
                self.output_layer) + "\nbiashiddenlayer\n" + str(
                self.bias_hidden_layer) + "\nbiasoutputlayer\n" + str(self.bias_output_layer)
        return "hidden_layer (wiersze - neurony) :\n" + str(
            self.hidden_layer) + "\noutput_layer (wiersze - neurony) :\n" + str(self.output_layer)

    def __init__(self, number_of_neurons_hidden_layer, number_of_neurons_output,
                 is_bias, input_data, expected_outputs, is_aproximation=True):
        # czy uruchomilismy bias, bias aktualnie nie jest zaimplementowany dla warstwy radialnej
        self.is_aproximation = is_aproximation
        self.is_bias = is_bias

        # dane wejsciowe
        self.input_data = input_data
        self.expected_outputs = expected_outputs

        if not self.is_aproximation:
            self.amount_of_class = []
            self.num_class = int(max(self.expected_outputs))
            self.correct_list = []
            self.correct_class_vector = []
            for i in range(self.num_class):
                self.correct_class_vector.append([])
                self.amount_of_class.append([0])
            for i in self.expected_outputs:
                self.amount_of_class[int(i - 1)][0] += 1

        # Pozycja centrów ma być losowana z wektórów wejściowych
        # Laczymy dane wejsciowe i expected outputs żeby móc je razem przelosować i zachować łączność danych
        input_data_random_order = numpy.vstack((self.input_data.T, self.expected_outputs.T)).T
        numpy.random.shuffle(input_data_random_order)

        # wtworzymy wagi dla warstwy wejsciowej, najpierw tworzymy macierz o jakim chcemy rozmiarze

        self.hidden_layer = numpy.zeros((len(input_data_random_order[0, :-1]), number_of_neurons_hidden_layer)).T

        # ustawiamy n neuronom ich centra jako n pierwszych danych wejściowych (po przelosowaniu danych wejsciowych)

        # for i in range(numpy.size(self.hidden_layer, 0)):
        #     self.hidden_layer[i] = input_data_random_order[i, :-1]
        # print(self.hidden_layer)

        # Ustawiamy sigmy początkowo na 1
        self.scale_coefficient = numpy.ones(numpy.size(self.hidden_layer, 0))
        self.delta_scale_coefficient = numpy.zeros_like(self.scale_coefficient)

        self.hidden_layer = K_means.kmeans(input_data, number_of_neurons_hidden_layer, 1000)

        # TODO: dirty fix
        self.num_of_neurons_hid_layer = len(self.hidden_layer)

        # Szukamy sigm ze wzoru
        self.find_sigma()
        # print(self.scale_coefficient)

        # delty dla momentum, aktualnie nie uczymy wsteczną propagacją warstwy ukrytej więc nie używamy
        self.delta_weights_hidden_layer = numpy.zeros((len(input_data_random_order[0][:-1]),
                                                       self.num_of_neurons_hid_layer)).T

        # tworzymy warstwę wyjściową z losowymi wagami od -1 do 1, jak w zad 1
        self.output_layer = 2 * numpy.random.random((self.num_of_neurons_hid_layer, number_of_neurons_output)).T - 1
        # print(self.output_layer)
        self.delta_weights_output_layer = numpy.zeros((self.num_of_neurons_hid_layer, number_of_neurons_output)).T

        # jesli wybralismy że bias ma byc to tworzymy dla każdej warstwy wektor wag biasu
        if is_bias:
            self.bias_hidden_layer = (2 * numpy.random.random(self.num_of_neurons_hid_layer) - 1)
            self.bias_output_layer = (2 * numpy.random.random(number_of_neurons_output) - 1)
        # jesli nie ma byc biasu to tworzymy takie same warstwy ale zer. Nie ingerują one potem w obliczenia w żaden sposób
        else:
            self.bias_hidden_layer = numpy.zeros(self.num_of_neurons_hid_layer)
            self.bias_output_layer = numpy.zeros(number_of_neurons_output)
        # taka sama warstwa delty jak dla layerów
        self.bias_output_layer_delta = numpy.zeros(number_of_neurons_output)
        self.bias_hidden_layer_delta = numpy.zeros(self.num_of_neurons_hid_layer)

    # Wzór funkcji
    # def sigmoid_fun(self, inputcik):
    #     return 1 / (1 + numpy.exp(-inputcik))

    # interesujące jest to, że według mojej wiedzy te wzory są równe sobie a dają dość bardzo różne wyniki w niektórych przypadkach
    # z wolfram alpha
    # def sigmoid_fun_deriative(self, inputcik):
    #     return numpy.exp(-inputcik) /  ((numpy.exp(-inputcik) + 1) ** 2)

    # def sigmoid_fun_deriative(self, inputcik):
    #     return inputcik * (1 - inputcik)

    # szukamy sigm ze wzorów dla każdego neuronu radialnego
    def find_sigma(self):
        pass
        for i in range(numpy.size(self.hidden_layer, 0)):
            max_dist = 0
            for j in range(numpy.size(self.hidden_layer, 0)):
                dist = distance.euclidean(self.hidden_layer[i], self.hidden_layer[j])
                if dist > max_dist:
                    max_dist = dist
            self.scale_coefficient[i] = \
                max_dist / (numpy.sqrt(2 * numpy.size(self.hidden_layer, 0)))

    # najpierw liczymy wynik z warstwy ukrytej i potem korzystając z niego liczymy wynik dla neuronów wyjścia
    # Jak wiadomo bias to przesunięcie wyniku o stałą więc jeżeli wybraliśmy
    # że bias istnieje to on jest po prostu dodawany do odpowiedniego wyniku iloczynu skalarnego
    # bias istnieje tylko dla output layer aktualnie
    def gauss_func(self, inputs, radial_weight, coefficient):
        return numpy.exp(-1 * (((distance.euclidean(inputs, radial_weight))) ** 2) / (2 * coefficient ** 2))

    def calculate_outputs(self, inputs):
        hidden_layer_output = []
        # todo bias
        for i in range(numpy.size(self.hidden_layer, 0)):
            # ze wzoru, prezentacja 6, koło 20 strony, wynik dla warstwy radialnej
            hidden_layer_output.append(self.gauss_func(inputs, self.hidden_layer[i], self.scale_coefficient[i]))
        # wynik dla warstwy wyjsciowej
        # print(hidden_layer_output)
        output_layer_output = numpy.dot(hidden_layer_output, self.output_layer.T) + self.bias_output_layer
        return hidden_layer_output, output_layer_output

    # TODO: To jest !CHYBA! różniczka zupełna
    def hidden_layer_deriative(self, inputs):
        derivatives = []
        for i in range(len(inputs[0])):
            derivatives.append(inputs[:, i] / numpy.power(self.scale_coefficient, 2))
        return numpy.asarray(derivatives)

    def hidden_layer_deriative_sigma(self, inputs):
        derivatives = []
        for i in range(len(inputs[0])):
            derivatives.append(numpy.power(inputs[:, i], 2) / numpy.power(self.scale_coefficient, 3))
        return numpy.asarray(derivatives).sum(axis=0)


    # trening, tyle razy ile podamy epochów
    # dla każdego epochu shufflujemy nasze macierze i przechodzimy przez nie po każdym wierszu z osobna
    def train(self, epoch_count):
        error_list = []
        for it in range(epoch_count):

            # Shuffle once each iteration
            joined_arrays = numpy.vstack((self.input_data.T, self.expected_outputs.T)).T
            numpy.random.shuffle(joined_arrays)
            joined_arrays_left = joined_arrays[:, :-1]
            joined_arrays_right = joined_arrays[:, -1:]
            mean_squared_error = 0
            ite = 0
            if not self.is_aproximation:
                for i in self.correct_class_vector:
                    i.append(0)
            for k, j in zip(joined_arrays_left, joined_arrays_right):
                ite += 1
                # epoka zwraca błąd
                # TODO to jest bezsensu ten if
                if self.is_aproximation:
                    mean_squared_error_from_epoch = self.epoch(k, j)
                else:
                    mean_squared_error_from_epoch, class_of_object, is_classified = self.epoch(k, j)
                    if is_classified:
                        self.correct_class_vector[class_of_object][it] += 1

                mean_squared_error += mean_squared_error_from_epoch

            mean_squared_error = mean_squared_error / ite
            error_list.append(mean_squared_error)
        print("OSTATNI BLAD", error_list[-1])
        # po przejściu przez wszystkie epoki zapisujemy błędy średniokwadratowe do pliku
        # with open("mean_squared_error.txt", "w") as file:
        with open("mean_squared_error.txt", "w") as file:
            for i in error_list:
                file.write(str(i) + "\n")

    def epoch(self, k, j):
        # print(join_k_j)
        # TODO: BRZYDKIE
        if not self.is_aproximation:
            class_of_object = int(j[0]) - 1
            if len(self.output_layer) == 3:
                possible_outputs = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                j = possible_outputs[int(j) - 1]
            else:
                pass
        hidden_layer_output, output_layer_output = self.calculate_outputs(k)
        hidden_layer_output = numpy.asarray(hidden_layer_output)

        # błąd dla wyjścia to różnica pomiędzy oczekiwanym wynikiem a otrzymanym
        output_error = output_layer_output - j

        if not self.is_aproximation:
            is_classified = False
            if len(self.output_layer) == 3:
                if (numpy.argmax(output_layer_output)) == numpy.argmax(j):
                    is_classified = True
            else:
                if abs(output_error) <= CLASSYFICATION_ERROR_MARGIN:
                    is_classified = True

        mean_squared_error = output_error.dot(output_error) / 2

        # output_delta - współczynnik zmiany wagi dla warstwy wyjściowej. Otrzymujemy jeden współczynnik dla każdego neronu.
        # aby potem wyznaczyć zmianę wag przemnażamy go przez input odpowiadający wadze neuronu
        # Pochodna funkcji liniowej = 1
        output_delta = output_error * 1

        hidden_layer_error = output_delta.T.dot(self.output_layer)

        hidden_layer_adjustment = (hidden_layer_output * hidden_layer_error *
                                   self.hidden_layer_deriative(k - self.hidden_layer)).T

        sigma_adjustment = (hidden_layer_output * hidden_layer_error *
                                   self.hidden_layer_deriative_sigma(k - self.hidden_layer)).T


        output_layer_adjustment = []
        for i in output_delta:
            value = [i * j for j in hidden_layer_output]
            output_layer_adjustment.append(value)
        output_layer_adjustment = numpy.asarray(output_layer_adjustment)

        # jeżeli wybraliśmy żeby istniał bias to teraz go modyfikujemy
        if self.is_bias:
            output_bias_adjustment = eta * output_delta + alfa * self.bias_output_layer_delta
            self.bias_output_layer -= output_bias_adjustment
            self.bias_output_layer_delta = output_bias_adjustment

        # wyliczamy zmianę korzystając z współczynnika uczenia i momentum

        output_layer_adjustment = eta * output_layer_adjustment + alfa * self.delta_weights_output_layer
        hidden_layer_adjustment = eta * hidden_layer_adjustment + alfa * self.delta_weights_hidden_layer
        sigma_adjustment = eta * sigma_adjustment + alfa * self.delta_scale_coefficient


        # modyfikujemy wagi w warstwach
        self.hidden_layer -= hidden_layer_adjustment
        self.scale_coefficient -= sigma_adjustment
        self.output_layer -= output_layer_adjustment

        # zapisujemy zmianę wag by użyć ją w momentum
        self.delta_weights_hidden_layer = hidden_layer_adjustment
        self.delta_weights_output_layer = output_layer_adjustment
        self.delta_scale_coefficient = sigma_adjustment

        if not self.is_aproximation:
            return mean_squared_error, class_of_object, is_classified
        return mean_squared_error

    def plot_classification(self):
        values1 = []
        for i in self.correct_class_vector[0]:
            values1.append(i / self.amount_of_class[0][0])
        values2 = []
        for i in self.correct_class_vector[1]:
            values2.append(i / self.amount_of_class[1][0])
        values3 = []
        for i in self.correct_class_vector[2]:
            values3.append(i / self.amount_of_class[2][0])
        values = []
        for i, j, k in zip(self.correct_class_vector[0], self.correct_class_vector[1], self.correct_class_vector[2]):
            values.append(
                (i + j + k) / (self.amount_of_class[0][0] + self.amount_of_class[1][0] + self.amount_of_class[2][0]))
        plt.xlabel('Epoka')
        plt.ylabel('Ilość popranych przyporządkowań')
        plt.plot(values, 'o', markersize=2, label="Wszystkie obiekty")
        plt.plot(values1, 'o', markersize=2, label="Obiekt 1")
        plt.plot(values2, 'o', markersize=2, label="Obiekt 2")
        plt.plot(values3, 'o', markersize=2, label="Obiekt 3")
        plt.legend()
        plt.show()


# otwieramy plik errorów i go plotujemy
def plot_file():
    # with open(mean_squared_error.txt", "r") as file:
    # inna sciezka
    with open("mean_squared_error.txt", "r") as file:
        lines = file.read().splitlines()
    values = []
    for i in lines:
        values.append(float(i))
    plt.plot(values, markersize=1)
    plt.xlabel('Iteracja')
    plt.ylabel('Wartość błędu')
    plt.title("Zmiana Błędu Średniokwadratowego, wsp. uczenia = " + str(eta) + " momentum = " + str(alfa))
    plt.show()


def plot_function(siec, title, neurons, points=None):
    if points is not None:
        values = []
        for i in points:
            values.append(siec.calculate_outputs(i[0])[1])
            # print(values[-1])
        plt.plot(points[:, 0], points[:, 1])
        points = points[:, 0]
        plt.plot(points, values, 'o', markersize=1)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title("Plik: " + title[:-4] + ", liczba neuronów = " + str(neurons))
        plt.tight_layout()
        plt.show()


# funkcja zwraca 2d array floatów w postaci arraya z paczki numpy.
def read_2d_float_array_from_file(file_name):
    two_dim_list_of_return_values = []
    with open(file_name, "r") as file:
        lines = file.read().splitlines()
    for i in lines:
        one_dim_list = []
        for j in list(map(float, i.split())):
            one_dim_list.append(j)
        two_dim_list_of_return_values.append(one_dim_list)
    return numpy.asarray(two_dim_list_of_return_values)


def main():
    numpy.random.seed(0)
    neurons = 20
    train_file = "classification_train.txt"
    test_file = "classification_test.txt"
    # ilość neuronów, ilość wyjść, czy_bias
    # numpy.delete(read_2d_float_array_from_file(train_file), [0, 1, 3], 1)
    siec = NeuralNetwork(neurons, 3, False, read_2d_float_array_from_file(train_file)[:, :-1],
                         read_2d_float_array_from_file(train_file)[:, -1], is_aproximation=False)
    iterations = 100
    siec.train(iterations)
    plot_file()
    if not siec.is_aproximation:
        siec.plot_classification()
        correct_amount = 0
        all_1 = [0, 0, 0]
        all_2 = [0, 0, 0]
        all_3 = [0, 0, 0]
        it = 0
        if len(siec.output_layer) == 3:
            for i in read_2d_float_array_from_file(train_file)[:, :]:
                obliczone = siec.calculate_outputs(i[:-1])[1]
                if i[-1] == 1:
                    all_1[numpy.argmax(obliczone)] += 1
                elif i[-1] == 2:
                    all_2[numpy.argmax(obliczone)] += 1
                elif i[-1] == 3:
                    all_3[numpy.argmax(obliczone)] += 1
                it += 1
        else:
            for i in read_2d_float_array_from_file(test_file)[:, :]:
                obliczone = siec.calculate_outputs(i[:-1])[1]
                classa = 0
                if obliczone - 1 <= 0.5:
                    classa = 1
                elif obliczone - 2 <= 0.5:
                    classa = 2
                elif obliczone - 3 <= 0.5:
                    classa = 3

                if i[-1] == classa:
                    correct_amount += 1

                if i[-1] == 1:
                    all_1[classa - 1] += 1
                elif i[-1] == 2:
                    all_2[classa - 1] += 1
                elif i[-1] == 3:
                    all_3[classa - 1] += 1
                it += 1
        print("KLASYFIKACJA OBIEKTOW  :   1,  2,  3")
        print("KLASYFIKACJA OBIEKTU 1 : ", all_1)
        print("KLASYFIKACJA OBIEKTU 2 : ", all_2)
        print("KLASYFIKACJA OBIEKTU 3 : ", all_3)
        print("ILOŚC Wszystkich: ", it)
        print("ILOŚć Odgadnietych: ", correct_amount)

    elif siec.is_aproximation:
        values = read_2d_float_array_from_file(test_file)
        values2 = numpy.zeros_like(values)
        indexes = numpy.argsort(values[:, 0])
        for i in range(len(indexes)):
            values2[i] = values[indexes[i]]
        plot_function(siec, train_file, neurons, values2)


if __name__ == "__main__":
    main()
