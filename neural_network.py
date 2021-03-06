from typing import List
from math import exp

from random import random, randint, choice

from make_stuff_go_faster import r_number, fastmap

sigmoid = lambda x : 1/(1+ exp(-x)) 

mutation_chance = 1E-2

repr_functions = {
    "random": lambda x,y : choice([x,y])
}

class Connection():
    def __init__(self, left_side: int, right_side: int):
        self.left_side = left_side
        self.right_side = right_side
        self.weights: List[List[int]] = []
        self.biases: List[int] = []

    def random_init(self):
        left_side, right_side = self.left_side, self.right_side
        for _ in range(right_side):
            self.weights.append([])
            for _ in range(left_side):
                self.weights[-1].append(r_number())
        for _ in range(left_side):
            self.biases.append(r_number())

    def eval(self, input_vec)->  List[int]:
        result = []
        for neuron_weights in self.weights:
            n = sum(neuron_weights[i] * input_vec[i] + self.biases[i] for i in range(self.right_side))
            n = sigmoid(n)
            result.append(n)
        return result

    def reproduce(self, other, function=repr_functions["random"]):
        child = Connection(self.left_side, self.right_side)
        for i in range(len(self.weights)):
            child.weights.append([])
            for j in range(self.left_side):
                if random() < mutation_chance:
                    child.weights[-1].append(r_number())
                else:
                    child.weights[-1].append(function(self.weights[i][j], other.weights[i][j]))

        for i in range(len(self.biases)):
            if random() < mutation_chance:
                child.biases.append(r_number())
            else:
                child.biases.append(function(self.biases[i], other.biases[i]))

        return child



class Neural_Network():
    def __init__(self, shape: List[int]) -> None:
        self.shape = shape
        self.layer_connections: List[Connection] = []
        for i in range(len(shape[:-1])):
            left_side, right_side = shape[i], shape[i+1] 
            connection = Connection(left_side, right_side)
            connection.random_init()
            self.layer_connections.append(connection)

    def eval(self, input_vec)-> List[int]:
        result = input_vec
        for i in range(len(self.shape)-1):
            result = self.layer_connections[i].eval(result)
        return result

    def __repr__(self):
        return "Neural net:" + str(self.shape)
    def reproduce(self, other):
        child = Neural_Network(self.shape)
        child.layer_connections = [self.layer_connections[i].reproduce(other.layer_connections[i]) 
                                                        for i in range(len(self.layer_connections))]
        return child
    