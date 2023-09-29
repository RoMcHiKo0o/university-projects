import random as rand
import numpy

from utils import lerp


class NN:
    def random_init_weights(self):
        for i in range(self.number_of_hidden):
            weights = []
            for j in range(self.number_of_inputs + 1):
                weights.append(rand.random() * 2 - 1)

            self.hidden_layer.append(weights)

        for i in range(self.number_of_outputs):
            weights = []
            for j in range(self.number_of_hidden + 1):
                weights.append(rand.random() * 2 - 1)

            self.output_layer.append(weights)

    def __init__(self, number_of_inputs=5, number_of_hidden=10, number_of_outputs=4):
        self.number_of_inputs = number_of_inputs
        self.number_of_hidden = number_of_hidden
        self.number_of_outputs = number_of_outputs

        # Lists of weights for each layer
        self.hidden_layer = []
        self.output_layer = []
        self.random_init_weights()

    def mutate(self, hidden_layer, output_layer, offset):
        for i in range(self.number_of_hidden):
            for j in range(self.number_of_inputs + 1):
                self.hidden_layer[i][j] = lerp(hidden_layer[i][j], self.hidden_layer[i][j], offset)

        for i in range(self.number_of_outputs):
            for j in range(self.number_of_hidden + 1):
                self.output_layer[i][j] = lerp(output_layer[i][j], self.output_layer[i][j], offset)

    def step(self, input_layer):
        input_layer.append(1)

        y = []
        for neuron_weights in self.hidden_layer:
            y.append(numpy.dot(input_layer, neuron_weights))

        y.append(1)
        response = []

        for neuron_weights in self.output_layer:
            response.append(numpy.sign(numpy.dot(y, neuron_weights)))

        return response


if __name__ == '__main__':
    network = NN()
    print(network.step([0.5, 0.1, 0.37, 0.57, 0.5]))
