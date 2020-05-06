import numpy
import time

import matplotlib.pyplot as plt

# wspolczynnik uczenia
eta = 0.5
# momentum
alfa = 0.5


class NeuralNetwork:
    def __repr__(self):
        return "Instance of NeuralNetwork"

    def __str__(self):
        if self.is_bias:
            return "hidden_layer (wiersze - neurony) :\n" + str(
                self.hidden_layer) + "\noutput_layer (wiersze - neurony) :\n" + str(
                self.output_layer) + "\nbiashiddenlayer\n" + str(
                self.bias_hidden_layer) + "\nbiasoutputlayer\n" + str(self.bias_output_layer)
        return "hidden_layer (wiersze - neurony) :\n" + str(
            self.hidden_layer) + "\noutput_layer (wiersze - neurony) :\n" + str(self.output_layer)

    def __init__(self, number_of_neurons_hidden_layer, number_of_neurons_output, number_of_inputs, is_bias):
        # czy uruchomilismy bias
        self.is_bias = is_bias
        self.iteration = 0
        # warstwy ukryta i wyjściowa oraz odpowiadające im struktury zapisujące zmianę wagi w poprzedniej iteracji, używane do momentum
        self.hidden_layer = (2 * numpy.random.random((number_of_inputs, number_of_neurons_hidden_layer)).T - 1)
        self.delta_weights_hidden_layer = numpy.zeros((number_of_inputs, number_of_neurons_hidden_layer)).T
        self.output_layer = 2 * numpy.random.random((number_of_neurons_hidden_layer, number_of_neurons_output)).T - 1
        self.delta_weights_output_layer = numpy.zeros((number_of_neurons_hidden_layer, number_of_neurons_output)).T
        # jesli wybralismy że bias ma byc to tworzymy dla każdej warstwy wektor wag biasu
        if is_bias:
            self.bias_hidden_layer = (2 * numpy.random.random(number_of_neurons_hidden_layer) - 1)
            self.bias_output_layer = (2 * numpy.random.random(number_of_neurons_output) - 1)
        # jesli nie ma byc biasu to tworzymy takie same warstwy ale zer. Nie ingerują one potem w obliczenia w żaden sposób
        else:
            self.bias_hidden_layer = numpy.zeros(number_of_neurons_hidden_layer)
            self.bias_output_layer = numpy.zeros(number_of_neurons_output)
        # taka sama warstwa delty jak dla layerów
        self.bias_output_layer_delta = numpy.zeros(number_of_neurons_output)
        self.bias_hidden_layer_delta = numpy.zeros(number_of_neurons_hidden_layer)

    # Wzór funkcji
    def sigmoid_fun(self, inputcik):
        return 1 / (1 + numpy.exp(-inputcik))

    # interesujące jest to, że według mojej wiedzy te wzory są równe sobie a dają dość bardzo różne wyniki w niektórych przypadkach
    # z wolfram alpha
    # def sigmoid_fun_deriative(self, inputcik):
    #     return numpy.exp(-inputcik) /  ((numpy.exp(-inputcik) + 1) ** 2)

    def sigmoid_fun_deriative(self, inputcik):
        return inputcik * (1 - inputcik)

    # najpierw liczymy wynik z warstwy ukrytej i potem korzystając z niego liczymy wynik dla neuronów wyjścia
    # Jak wiadomo bias to przesunięcie wyniku o stałą więc jeżeli wybraliśmy że bias istnieje to on jest po prostu dodawany do odpowiedniego wyniku iloczynu skalarnego
    def calculate_outputs(self, inputs):

        hidden_layer_output = self.sigmoid_fun(numpy.dot(inputs, self.hidden_layer.T) + self.bias_hidden_layer)
        output_layer_output = self.sigmoid_fun(
            numpy.dot(hidden_layer_output, self.output_layer.T) + self.bias_output_layer)

        return hidden_layer_output, output_layer_output

    # trening, tyle razy ile podamy epochów
    # dla każdego epochu shufflujemy nasze macierze i przechodzimy przez nie po każdym wierszu z osobna
    def train(self, inputs, expected_outputs, epoch_count, fileName):
        error_list = []
        for it in range(epoch_count):

            # Shuffle once each iteration
            joined_arrays = numpy.concatenate((inputs, expected_outputs), axis=1)
            numpy.random.shuffle(joined_arrays)
            joined_arrays_left, joined_arrays_right = numpy.hsplit(joined_arrays, 2)
            numpy.testing.assert_array_equal(joined_arrays_left, joined_arrays_right)

            mean_squared_error = 0
            ite = 0

            for k, j in zip(joined_arrays_left, joined_arrays_right):

                hidden_layer_output, output_layer_output = self.calculate_outputs(k)

                # błąd dla wyjścia to różnica pomiędzy oczekiwanym wynikiem a otrzymanym
                output_error = output_layer_output - j
                mean_squared_error += output_error.dot(output_error) / 2
                ite += 1

                # output_delta - współczynnik zmiany wagi dla warstwy wyjściowej. Otrzymujemy jeden współczynnik dla każdego neronu.
                # aby potem wyznaczyć zmianę wag przemnażamy go przez input odpowiadający wadze neuronu
                output_delta = output_error * self.sigmoid_fun_deriative(output_layer_output)

                # korzystamy z wcześniej otrzymanego współczynniku błędu aby wyznaczyć błąd dla warstwy ukrytej
                print(output_delta)
                print(self.output_layer)
                print(output_delta.T)
                hidden_layer_error = output_delta.T.dot(self.output_layer)
                print(hidden_layer_error)
                exit(1)
                # jak dla warstwy wyjściowej hidden_layer_delta jest jeden dla każdego neuronu i
                # aby wyznaczyć zmianę wag przemnażamy go przez input odpowiadający wadze neuronu
                hidden_layer_delta = hidden_layer_error * self.sigmoid_fun_deriative(hidden_layer_output)

                output_layer_adjustment = []
                for i in output_delta:
                    output_layer_adjustment.append(hidden_layer_output * i)
                output_layer_adjustment = numpy.asarray(output_layer_adjustment)

                hidden_layer_adjustment = []
                for i in hidden_layer_delta:
                    hidden_layer_adjustment.append(k * i)
                hidden_layer_adjustment = numpy.asarray(hidden_layer_adjustment)

                # jeżeli wybraliśmy żeby istniał bias to teraz go modyfikujemy
                if self.is_bias:
                    hidden_bias_adjustment = eta * hidden_layer_delta + alfa * self.bias_hidden_layer_delta
                    output_bias_adjustment = eta * output_delta + alfa * self.bias_output_layer_delta
                    self.bias_hidden_layer -= hidden_bias_adjustment
                    self.bias_output_layer -= output_bias_adjustment
                    self.bias_hidden_layer_delta = hidden_bias_adjustment
                    self.bias_output_layer_delta = output_bias_adjustment

                # wyliczamy zmianę korzystając z współczynnika uczenia i momentum
                hidden_layer_adjustment = eta * hidden_layer_adjustment + alfa * self.delta_weights_hidden_layer
                output_layer_adjustment = eta * output_layer_adjustment + alfa * self.delta_weights_output_layer

                # modyfikujemy wagi w warstwach
                self.hidden_layer -= hidden_layer_adjustment
                self.output_layer -= output_layer_adjustment

                # zapisujemy zmianę wag by użyć ją w momentum
                self.delta_weights_hidden_layer = hidden_layer_adjustment
                self.delta_weights_output_layer = output_layer_adjustment

            mean_squared_error = mean_squared_error / ite
            error_list.append(mean_squared_error)

        # po przejściu przez wszystkie epoki zapisujemy błędy średniokwadratowe do pliku
        with open(fileName, "w") as file:
            for i in error_list:
                file.write(str(i) + "\n")

    def train_till_error(self, inputs, expected_outputs, fileName, error):
        error_list = []
        mean_squared_error = 1
        while mean_squared_error > error:

            # Shuffle once each iteration
            joined_arrays = numpy.concatenate((inputs, expected_outputs), axis=1)
            numpy.random.shuffle(joined_arrays)
            joined_arrays_left, joined_arrays_right = numpy.hsplit(joined_arrays, 2)
            numpy.testing.assert_array_equal(joined_arrays_left, joined_arrays_right)

            mean_squared_error = 0
            ite = 0

            for k, j in zip(joined_arrays_left, joined_arrays_right):

                hidden_layer_output, output_layer_output = self.calculate_outputs(k)

                # błąd dla wyjścia to różnica pomiędzy oczekiwanym wynikiem a otrzymanym
                output_error = output_layer_output - j
                mean_squared_error += output_error.dot(output_error) / 2
                ite += 1

                # output_delta - współczynnik zmiany wagi dla warstwy wyjściowej. Otrzymujemy jeden współczynnik dla każdego neronu.
                # aby potem wyznaczyć zmianę wag przemnażamy go przez input odpowiadający wadze neuronu
                output_delta = output_error * self.sigmoid_fun_deriative(output_layer_output)

                # korzystamy z wcześniej otrzymanego współczynniku błędu aby wyznaczyć błąd dla warstwy ukrytej
                hidden_layer_error = output_delta.T.dot(self.output_layer)
                # jak dla warstwy wyjściowej hidden_layer_delta jest jeden dla każdego neuronu i
                # aby wyznaczyć zmianę wag przemnażamy go przez input odpowiadający wadze neuronu
                hidden_layer_delta = hidden_layer_error * self.sigmoid_fun_deriative(hidden_layer_output)

                output_layer_adjustment = []
                for i in output_delta:
                    output_layer_adjustment.append(hidden_layer_output * i)
                output_layer_adjustment = numpy.asarray(output_layer_adjustment)

                hidden_layer_adjustment = []
                for i in hidden_layer_delta:
                    hidden_layer_adjustment.append(k * i)
                hidden_layer_adjustment = numpy.asarray(hidden_layer_adjustment)

                # jeżeli wybraliśmy żeby istniał bias to teraz go modyfikujemy
                if self.is_bias:
                    hidden_bias_adjustment = eta * hidden_layer_delta + alfa * self.bias_hidden_layer_delta
                    output_bias_adjustment = eta * output_delta + alfa * self.bias_output_layer_delta
                    self.bias_hidden_layer -= hidden_bias_adjustment
                    self.bias_output_layer -= output_bias_adjustment
                    self.bias_hidden_layer_delta = hidden_bias_adjustment
                    self.bias_output_layer_delta = output_bias_adjustment

                # wyliczamy zmianę korzystając z współczynnika uczenia i momentum
                hidden_layer_adjustment = eta * hidden_layer_adjustment + alfa * self.delta_weights_hidden_layer
                output_layer_adjustment = eta * output_layer_adjustment + alfa * self.delta_weights_output_layer

                # modyfikujemy wagi w warstwach
                self.hidden_layer -= hidden_layer_adjustment
                self.output_layer -= output_layer_adjustment

                # zapisujemy zmianę wag by użyć ją w momentum
                self.delta_weights_hidden_layer = hidden_layer_adjustment
                self.delta_weights_output_layer = output_layer_adjustment

            mean_squared_error = mean_squared_error / ite
            error_list.append(mean_squared_error)
            self.iteration += 1

        # po przejściu przez wszystkie epoki zapisujemy błędy średniokwadratowe do pliku
        with open(fileName, "w") as file:
            for i in error_list:
                file.write(str(i) + "\n")


# otwieramy plik errorów i go plotujemy
def plot_file(fileName, string):
    with open(fileName, "r") as file:
        lines = file.read().splitlines()
    values = []
    ilosc = []
    liczba = 1
    for i in lines:
        values.append(float(i))
        liczba += 1
        ilosc.append(liczba)

    # plt.plot(values, 'o', markersize=1)
    plt.plot(ilosc, values, label=string)
    plt.axis([-1000, len(lines), 0, 0.75])
    # plt.show()


# funkcja zwraca 2d array intów w postaci arraya z paczki numpy.
def read_2d_int_array_from_file(file_name):
    two_dim_list_of_return_values = []
    with open(file_name, "r") as file:
        lines = file.read().splitlines()
    for i in lines:
        one_dim_list = []
        for j in list(map(int, i.split())):
            one_dim_list.append(j)
        two_dim_list_of_return_values.append(one_dim_list)
    return numpy.asarray(two_dim_list_of_return_values).T


def main():
    # liczba neuronów w warstwie ukrytej, liczba wyjść, liczba inputów, czy_bias
    siec1 = NeuralNetwork(1, 4, 4, False)
    siec2 = NeuralNetwork(2, 4, 4, False)
    siec3 = NeuralNetwork(3, 4, 4, False)

    # siec1 = NeuralNetwork(1, 4, 4, True)
    # siec2 = NeuralNetwork(2, 4, 4, True)
    # siec3 = NeuralNetwork(3, 4, 4, True)

    # dane wejściowe, dane wyjściowe, ilość epochów
    siec1.train(read_2d_int_array_from_file("dane.txt"), read_2d_int_array_from_file("dane.txt").T, 10000,
                "mean_squared_error_1b.txt")
    siec2.train(read_2d_int_array_from_file("dane.txt"), read_2d_int_array_from_file("dane.txt").T, 10000,
                "mean_squared_error_2b.txt")
    siec3.train(read_2d_int_array_from_file("dane.txt"), read_2d_int_array_from_file("dane.txt").T, 10000,
                "mean_squared_error_3b.txt")

    # siec1.train_till_error(read_2d_int_array_from_file("dane.txt"), read_2d_int_array_from_file("dane.txt").T, "mean_squared_error_1b.txt", 0.2)
    # siec2.train_till_error(read_2d_int_array_from_file("dane.txt"), read_2d_int_array_from_file("dane.txt").T, "mean_squared_error_2b.txt", 0.001)
    # siec3.train_till_error(read_2d_int_array_from_file("dane.txt"), read_2d_int_array_from_file("dane.txt").T, "mean_squared_error_3b.txt", 0.001)

    # plot_file("mean_squared_error_1b.txt","1 neuron")
    # plot_file("mean_squared_error_2b.txt","2 neurony")

    # plot_file("mean_squared_error_3b.txt","3 neurony")
    # plt.legend()
    # plt.xlabel("iteracje")
    # plt.ylabel("blad sredniokwadratowy")
    # plt.show()
    print("Wynik:")
    inpuciki = numpy.asarray([1, 0, 0, 0])
    print(inpuciki)
    print(siec1.calculate_outputs(inpuciki)[0])
    # print(siec2.calculate_outputs(inpuciki)[0])
    # print(siec3.calculate_outputs(inpuciki)[0])
    inpuciki = numpy.asarray([0, 1, 0, 0])
    print(inpuciki)
    print(siec1.calculate_outputs(inpuciki)[0])
    # print(siec2.calculate_outputs(inpuciki)[0])
    # print(siec3.calculate_outputs(inpuciki)[0])
    inpuciki = numpy.asarray([0, 0, 1, 0])
    print(inpuciki)
    print(siec1.calculate_outputs(inpuciki)[0])
    # print(siec2.calculate_outputs(inpuciki)[0])
    # print(siec3.calculate_outputs(inpuciki)[0])
    inpuciki = numpy.asarray([0, 0, 0, 1])
    print(inpuciki)
    print(siec1.calculate_outputs(inpuciki)[0])
    # print(siec2.calculate_outputs(inpuciki)[0])
    # print(siec3.calculate_outputs(inpuciki)[0])
    # print(siec1.iteration,siec2.iteration,siec3.iteration)


if __name__ == "__main__":
    main()
