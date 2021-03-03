from neural_network import Neural_Network
from typing import List
import random as r
from copy import deepcopy as copy

import tqdm

from make_stuff_go_faster import fastmap



ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "VOID"]

frame_y = 50
frame_x = int(3/2 * frame_y)

input_size = 2*frame_x*frame_y

GEN_SIZE = 30
GENERATION_AMOUNT = 10
SHAPE = [input_size, 
         input_size//64,
         input_size//256,
         input_size//512,
         5]
print(SHAPE)

blank_framebuffer: List[List[int]] = list()
for y in range(frame_y):
    blank_framebuffer.append([])
    for x in range(frame_x):
        blank_framebuffer[-1].append(False)

class Snake():
    def __init__(self, init_NN=True) -> None:
        if init_NN:
            self.NN: Neural_Network = Neural_Network(SHAPE)
        else:
            self.NN: Neural_Network = None
        self.size: int=  int()
        self.time: int = int()
        ##### simulation variables #####
        self.pos: List[int] = [100, 50]
        self.body: List[List[int]] = [[100, 50], [100-10, 50], [100-(2*10), 50]]
        self.length: int = 3
        self.direction: str = 'RIGHT'
        self.change_to: str = self.direction
        self.food_pos: List[int] = [r.randrange(1, (frame_x//10)) * 10, r.randrange(1, (frame_y//10)) * 10]
        self.food_spawn: bool = True
        self.dead: bool = False
        ##### data fed to neural network #####
        self.current_frame: List[List[int]] = None
        self.framebuffer: List[List[int]] = None
        self.reset_framebuffer()

    def __repr__(self):
        return "Snake, "

    def reset_simulation(self):
        self.pos = [100, 50]
        self.body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
        self.length = 3
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.food_pos = [r.randrange(1, (frame_x//10)) * 10, r.randrange(1, (frame_y//10)) * 10]
        self.food_spawn = True
        self.dead = False
        self.reset_framebuffer()

    def reset_framebuffer(self) -> None:
        self.framebuffer = copy(blank_framebuffer)
        self.current_frame = copy(blank_framebuffer)

    def score(self) -> int:
        return (self.length*self.time)**2 + self.time

    def reproduce(self, other) -> Neural_Network:
        child = Snake()
        child.NN = self.NN.reproduce(other.NN)
        return child
    
    def get_output(self, frames) -> int:
        nn_output = self.NN.eval(frames)
        return nn_output.index(max(nn_output))

    def render_frames(self) -> None:
        self.framebuffer = copy(self.current_frame)
        self.current_frame = blank_framebuffer
        for pos in self.body:
            self.current_frame[pos[0]][pos[1]] = True
        for pos in self.food_pos:
            self.current_frame[pos[0]][pos[1]] = True

    def merge_frames(self):
        merged = list()
        for r1, r2 in zip(self.current_frame, self.framebuffer):
            for c1,c2 in zip(r1,r2):
                merged.append(c1)
                merged.append(c2)
        return merged

    def simulate(self) -> bool: # returns false if snake is dead
        # get neural network output
        self.change_to = ACTIONS[self.get_output(self.merge_frames())]
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
            self.pos[1] -= 10
        if self.direction == 'DOWN':
            self.pos[1] += 10
        if self.direction == 'LEFT':
            self.pos[0] -= 10
        if self.direction == 'RIGHT':
            self.pos[0] += 10
        self.body.insert(0, list(self.pos))
        # grow snake
        if self.pos[0] == self.food_pos[0] and self.pos[1] == self.food_pos[1]:
            self.length += 1
            self.food_spawn = False
        else:
            self.body.pop()
        #spawning food
        if not self.food_spawn:
            self.food_pos = [r.randrange(1, (frame_x//10)) * 10, r.randrange(1, (frame_y//10)) * 10]
        self.food_spawn = True

        # Game Over conditions
        # Getting out of bounds
        if self.pos[0] < 0 or self.pos[0] > frame_x-10:
            self.dead = True
            return False
        if self.pos[1] < 0 or self.pos[1] > frame_y-10:
            self.dead = True
            return False
        # Touching the snake body
        for block in self.body[1:]:
            if self.pos[0] == block[0] and self.pos[1] == block[1]:
                self.dead = True
                return False
        self.time += 1
        self.render_frames()
        
    def reproduce(self, other):
        child = Snake(init_NN=False)
        child.NN = self.NN.reproduce(other.NN)
        return child

def new_snake(x):
    return Snake()

def create_child(parent_pool) -> Snake:
    parent_1, parent_2  = r.choice(parent_pool),  r.choice(parent_pool)
    return parent_1.reproduce(parent_2)

class Generation():
    def __init__(self, generation_size: int) -> None:
        self.generation_size = generation_size
        print("creating initial population...")
        self.population: List[Snake] = list(fastmap(new_snake, range(self.generation_size), display_progress=True))
        for s in self.population: print("initialized", s.NN)
        self.alive_snakes = [s for s in self.population]
    
    def simulate_step(self) -> None:
        for snake in self.alive_snakes:
            if not snake.simulate():
                self.alive_snakes.remove(snake)  

    def simulate_generation(self):
        time = 0
        while len(self.alive_snakes)> 0:
            self.simulate_step()
            # debug
            print("time", time, ":", len(self.alive_snakes), "snakes alive")
            time += 1
        

    def next_gen(self) -> None:
        #sort by score
        sorted_snakes = sorted(self.population, key=lambda s : s.score(), reverse=True)
        print("best score here", sorted_snakes[0].score())
        # kill all snakes except top 25%
        print("killing snakes...")
        sorted_snakes = sorted_snakes[:self.generation_size//4]
        print("merging snakes")
        new_snakes_amount = max(1,self.generation_size//100)
        new_children_amount = self.generation_size-new_snakes_amount
        self.population = list(fastmap(create_child,list(sorted_snakes for _ in range(new_children_amount)), display_progress=True))
        print("adding new children")
        self.population += list(fastmap(new_snake, range(new_snakes_amount), display_progress=True))



def main():
    generation = Generation(generation_size=GEN_SIZE)
    for g in range(GENERATION_AMOUNT):
        print("Simulating gen",g,":")
        generation.simulate_generation()
        generation.next_gen()
    
if __name__ == "__main__":
    main()

