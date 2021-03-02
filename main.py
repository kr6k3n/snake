from NN import Neural_Network
from typing import List
import random as r

from copy import deepcopy as copy

ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "VOID"]


frame_x = 720
frame_y = 480

input_size = 2*frame_x*frame_y


SHAPE = [input_size, 
         input_size//4,
         input_size//8,
         input_size//16,
         5]

def init_framebuffer() -> List[List[int]]:
    framebuffer: List[List[int]] = list()
    for y in range(frame_y):
        framebuffer.append([])
        for x in range(frame_x):
            framebuffer[-1].append(False)
    return framebuffer

class Snake():
    def __init__(self):
        self.NN = Neural_Network(SHAPE)
        self.size =  int()
        self.time = int()
        # simulation variables
        self.pos = [100, 50]
        self.body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
        self.length = 3
        self.direction = 'RIGHT'
        self.change_to = self.direction
        # data fed to neural network
        self.current_frame = None
        self.framebuffer
        self.reset_framebuffer()

    def reset(self) -> None:
        self.framebuffer = init_framebuffer()
        self.current_frame = copy(self.framebuffer)

    def score(self):
        return (self.size*self.time)**2 + self.time

    def reproduce(self, other):
        child = Snake()
        child.NN = self.NN.reproduce(other.NN)
        return child
    
    def get_output(self, frames):
        nn_output = self.NN.eval(frames)
        return nn_output.index(max(nn_output))

    def simulate(self) -> bool: # returns false if snake is dead
        # get neural network output
        self.change_to = ACTIONS[self.get_output()]
        # Making sure the snake cannot move in the opposite direction instantaneously
        if self.change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        if self.change_to == 'DOWN' and self.direction != 'UP':
            direction = 'DOWN'
        if self.change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        if self.change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'

        # Moving the snake
        if self.direction == 'UP':
            self.snake_pos[1] -= 10
        if self.direction == 'DOWN':
            self.snake_pos[1] += 10
        if self.direction == 'LEFT':
            self.snake_pos[0] -= 10
        if self.direction == 'RIGHT':
            self.snake_pos[0] += 10
        self.snake_body.insert(0, list(self.snake_pos))
        # grow snake
        if self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]:
            self.length += 1
            self.food_spawn = False
        else:
            self.snake_body.pop()
        #spawning food
        if not self.food_spawn:
            self.food_pos = [random.randrange(1, (frame_x//10)) * 10, random.randrange(1, (frame_y//10)) * 10]
        self.food_spawn = True
        # Game Over conditions
        # Getting out of bounds
        if self.snake_pos[0] < 0 or self.snake_pos[0] > frame_x-10:
            return False
        if self.snake_pos[1] < 0 or self.snake_pos[1] > frame_y-10:
            return False
        # Touching the snake body
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                return False

class Generation():
    def __init__(self, generation_size: int):
        self.generation_size = generation_size
        self.population: List[Snake] = [Snake() for _ in range(self.generation_size)]
        self.alive_snakes = self.population

        # simultation variables
        food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
        food_spawn = True
    def simulate_generation(self):
        pass

    def next_gen(self) -> None:
        sorted_snakes = sorted(self.population, key=lambda s : s.score())
        sorted_snakes = sorted_snakes[:self.generation_size//4]
        self.population: List[Snake] = list()
        for _ in range(self.generation_size):
            parent_1, parent_2  = r.choice(sorted_snakes),  r.choice(sorted_snakes)
            self.population.append(parent_1.reproduce(parent_2))

    def simulate_step(self) -> None:
        
        


def main():
    generation = Generation(generation_size=200)
    for _ in range(5):
        generation.simulate_generation()
        generation.next_gen()
    
if __name__ == "__main__":
    main()

