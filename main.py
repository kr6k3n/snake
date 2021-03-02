from NN import Neural_Network
import random as r

ACTIONS = ["up", "down", "left", "right", "void"]


frame_x = 720
frame_y = 480

input_size = 2*frame_x*frame_y


SHAPE = [input_size, 
        input_size//4, 
        input_size//8, 
        input_size//16, 
        5]

class Snake():
    def __init__(self):
        self.NN = Neural_Network(SHAPE)
        self.size =  int()
        self.time = int()
        # simulation

    def score(self):
        return (self.size*self.time)**2 + self.time

    def reproduce(self, other):
        child = Snake()
        child.NN = self.NN.reproduce(other.NN)
        return child
    
    def get_output(self, frames):
        nn_output = self.NN.eval(frames)
        return nn_output.index(max(nn_output))

class Generation():
    def __init__(self, generation_size: int):
        self.generation_size
        self.population: List[Snake] = [Snake() for _ in range(self.generation_size)]
        self.alive_snakes = self.population
    def simulate_generation(self):
        pass

    def next_gen(self):
        sorted_snakes = sorted(self.population, key=lambda s : s.score())
        sorted_snakes = sorted_snakes[:gen_size//4]
        self.population: List[Snake] = list()
        for _ in range(self.generation_size):
            parent_1, parent_2  = r.choice(sorted_snakes),  r.choice(sorted_snakes)
            self.population.append(parent_1.reproduce(parent_2))

def main():
    generation = Generation(200)
    for idG in range(5):
        generation.simulate_generation()
        generation.next_gen()
    
    
if __name__ == "__main__":
    main()