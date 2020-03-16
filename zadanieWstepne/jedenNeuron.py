import numpy
from matplotlib import pyplot as plt
import time


class NeuralNetwork:
    def __init__(self):
        self.weight_matrix = 10 * numpy.random.random(3) - 5

    def funkcja_skokowa(self, inputcik):
        wynik = numpy.dot(inputcik, self.weight_matrix)  # iloczyn skalarny tak o świrki
        if wynik > 0:
            return 1
        return 0

    def train(self, inputs, expected_outputs, amount_of_tries):
        wspolczynnik_uczenia = 0.01
        for i in range(0, amount_of_tries):
            for j in range(0, len(inputs)):
                wynikpl = self.funkcja_skokowa(inputs[j])
                if wynikpl == expected_outputs[j]:
                    pass
                elif wynikpl == 1 and expected_outputs[j] == 0:
                    self.weight_matrix -= wspolczynnik_uczenia * inputs[j]
                elif wynikpl == 0 and expected_outputs[j] == 1:
                    self.weight_matrix += wspolczynnik_uczenia * inputs[j]
                pass
            pass
        pass


def wczytajPunktyZPliku(fileName):
    punkty_pod, punkty_nad = [], []
    with open(fileName, "r") as plik:
        lines = plik.read().splitlines()
    lines = [tup for tup in lines if not tup == ""]
    for i in lines:
        liczby = list(map(float, i.split()))
        if liczby[2] == 0:
            punkty_pod.append([liczby[0], liczby[1]])
        else:
            punkty_nad.append([liczby[0], liczby[1]])
    return punkty_pod, punkty_nad


def main():
    punkty_pod, punkty_nad = wczytajPunktyZPliku("punkt.txt")
    x1, y1 = numpy.asarray(punkty_pod).T
    plt.scatter(x1, y1)
    x2, y2 = numpy.asarray(punkty_nad).T
    plt.scatter(x2, y2)
    for i in punkty_pod:
        i.append(1)
    for i in punkty_nad:
        i.append(1)
    figura = plt.gcf()
    print(punkty_pod)
    print(punkty_nad)
    neural_network = NeuralNetwork()
    var3 = numpy.poly1d([neural_network.weight_matrix[0] / -neural_network.weight_matrix[1],
                         neural_network.weight_matrix[2] / -neural_network.weight_matrix[1]])
    z = numpy.linspace(-5, 5, num=10)
    fx = []
    for i in range(len(z)):
        fx.append(var3(z[i]))
    plt.plot(z, fx)
    plt.show()
    plt.scatter(x1, y1)
    plt.scatter(x2, y2)

    print('Losowe wagi na start')
    print(neural_network.weight_matrix)
    super_lista = []
    train_inputs = numpy.array(punkty_pod + punkty_nad)
    for i in punkty_pod:
        super_lista.append(0)
    for i in punkty_nad:
        super_lista.append(1)
    train_outputs = numpy.array([super_lista]).T

    neural_network.train(train_inputs, train_outputs, 10)
    print('Nowe wagi po treningu 10 razy')
    print(neural_network.weight_matrix)
    var3 = numpy.poly1d([neural_network.weight_matrix[0]/-neural_network.weight_matrix[1],
                        neural_network.weight_matrix[2]/-neural_network.weight_matrix[1]])
    z = numpy.linspace(-5, 5, num=10)
    fx = []
    for i in range(len(z)):
        fx.append(var3(z[i]))
    plt.plot(z, fx)
    plt.show()
    plt.scatter(x1, y1)
    plt.scatter(x2, y2)
    neural_network.train(train_inputs, train_outputs, 10000)
    print('Nowe wagi po treningu 10010 razy')
    print(neural_network.weight_matrix)
    var3 = numpy.poly1d([neural_network.weight_matrix[0] / -neural_network.weight_matrix[1],
                         neural_network.weight_matrix[2] / -neural_network.weight_matrix[1]])
    z = numpy.linspace(-5, 5, num=10)
    fx = []
    for i in range(len(z)):
        fx.append(var3(z[i]))
    plt.plot(z, fx)
    plt.show()
    pass


if __name__ == "__main__":
    main()

# import numpy
# import time
#
#
# class NeuralNetwork():
#
#     def __init__(self):
#         # Using seed to make sure it'll
#         # generate same weights in every run
#         numpy.random.seed(1)
#
#         # 2x1 Weight matrix
#         self.weight_matrix = 2 * numpy.random.random((3, 1)) - 1
#
#     def funkcja_skokowa(self, input):
#         wynik = numpy.dot(self.weight_matrix, input)
#         if wynik > 1:
#             return 1
#         return 0
#
#     def train(self, inputs, expected_outputs, amount_of_tries):
#         for i in range(amount_of_tries):
#             for j in range(len(inputs)):
#                 wynikpl = self.funkcja_skokowa(inputs[j])
#                 if wynikpl == expected_outputs[j]:
#                     pass
#                 elif wynikpl == 1 and expected_outputs[j] == 0:
#                     self.weight_matrix -= inputs[j]
#                 elif wynikpl == 0 and expected_outputs[j] == 1:
#                     self.weight_matrix += inputs[j]
#                 pass
#             pass
#         pass
#
#
# def wczytajPunktyZPliku(fileName):
#     punkty_pod, punkty_nad = [], []
#     with open(fileName, "r") as plik:
#         lines = plik.read().splitlines()
#     lines = [tup for tup in lines if not tup == ""]
#     for i in lines:
#         # x, y, z = i.split()\
#         liczby = list(map(float, i.split()))
#         if liczby[2] == 0:
#             punkty_pod.append([1, liczby[0], liczby[1]])
#         else:
#             punkty_nad.append([1, liczby[0], liczby[1]])
#     return punkty_pod, punkty_nad
#
#
# def main():
#     siec = NeuralNetwork()
#     punkty_pod, punkty_nad = wczytajPunktyZPliku("punkt.txt")
#     expected = []
#     for i in punkty_pod:
#         expected.append(0)
#     for i in punkty_nad:
#         expected.append(1)
#     print(numpy.array(punkty_pod + punkty_nad))
#     siec.train(numpy.array(punkty_pod + punkty_nad), numpy.array(expected).T, 10)
#
#
# if __name__ == "__main__":
#     main()