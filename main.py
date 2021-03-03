from neural_network import Neural_Network
from typing import List
import random as r
from copy import deepcopy as copy

import tqdm

from make_stuff_go_faster import fastmap



ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "VOID"]

frame_y = 480
frame_x = int(3/2 * frame_y)

input_size = (2*frame_x*frame_y)//100

GEN_SIZE = 100
GENERATION_AMOUNT = 10
SHAPE = [input_size, 
         input_size//16,
         input_size//32,
         input_size//64,
         5]

print("SHAPE", SHAPE)

blank_framebuffer: List[List[int]] = list()
for y in range(frame_y//10):
    blank_framebuffer.append([])
    for x in range(frame_x//10):
        blank_framebuffer[-1].append(False)

class Snake():
    def __init__(self, init_NN=True) -> None:
        if init_NN:
            self.NN: Neural_Network = Neural_Network(SHAPE)
        else:
            self.NN: Neural_Network = None
        self.size: int =  int()
        self.time: int = int()
        ##### simulation variables #####
        self.pos: List[int] = [frame_x//2, frame_y//2]
        self.body: List[List[int]] = [[self.pos[0]-10*i, self.pos[1]] for i in range(3)]
        self.length: int = 3
        # controls
        self.direction: str = 'RIGHT'
        self.change_to: str = self.direction
        self.food_pos: List[int] = [r.randrange(1, (frame_x//10)) * 10, r.randrange(1, (frame_y//10)) * 10]
        #self.food_spawn: bool = True
        self.dead: bool = False
        ##### data fed to neural network #####
        self.current_frame: List[List[int]] = None
        self.framebuffer: List[List[int]] = None
        self.reset_framebuffer()

    def __repr__(self):
        return f"Snake| size {self.size}, length {self.length}"



    def reset_framebuffer(self) -> None:
        self.framebuffer = copy(blank_framebuffer)
        self.current_frame = copy(blank_framebuffer)

    
    def get_output(self, frames) -> int:
        nn_output = self.NN.eval(frames)
        return nn_output.index(max(nn_output))

    def render_frames(self) -> None:
        self.framebuffer = copy(self.current_frame)
        self.current_frame = blank_framebuffer
        #render snake
        for pos in self.body:
            self.current_frame[pos[0]//10][pos[1]//10] = True
        #render food
        self.current_frame[self.food_pos[0]//10][self.food_pos[1]//10] = True

    def merge_frames(self):
        merged = list()
        for r1, r2 in zip(self.current_frame, self.framebuffer):
            for c1,c2 in zip(r1,r2):
                merged.append(c1)
                merged.append(c2)
        return merged
    
    def score(self) -> int:
        return (self.length*self.time)**2 + self.time

    def reproduce(self, other) -> Neural_Network:
        child = Snake()
        child.NN = self.NN.reproduce(other.NN)
        return child

    def simulate(self) -> bool: # returns false if snake is dead
        # get neural network output
        self.change_to = ACTIONS[self.get_output(self.merge_frames())]
        print("action: ", self.change_to)
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
            #replace food
            self.food_pos = [r.randrange(1, (frame_x//10)) * 10, r.randrange(1, (frame_y//10)) * 10]
        else:
            self.body.pop() 

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
        return True
        
    def reproduce(self, other):
        child = Snake(init_NN=False)
        child.NN = self.NN.reproduce(other.NN)
        return child

def new_snake(x):
    return Snake()

def create_child(parent_pool) -> Snake:
    parent_1, parent_2  = r.choice(parent_pool),  r.choice(parent_pool)
    return parent_1.reproduce(parent_2)

def snake_step(snake):
    return snake.simulate()

class Generation():
    def __init__(self, generation_size: int) -> None:
        self.generation_size = generation_size
        print("creating initial population...")
        self.population: List[Snake] = fastmap(new_snake, range(self.generation_size), display_progress=True)
        self.alive_snakes = [s for s in self.population]
    
    def simulate_step(self) -> None:
        for snake_index, snake_alive in enumerate(fastmap(snake_step, self.alive_snakes)):
            if not snake_alive:
                self.alive_snakes.pop(snake_index)  

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
        self.population = fastmap(create_child,list(sorted_snakes for _ in range(new_children_amount)), display_progress=True)
        print("adding new children")
        self.population += fastmap(new_snake, range(new_snakes_amount), display_progress=True)



def main():
    generation = Generation(generation_size=GEN_SIZE)
    for g in range(GENERATION_AMOUNT):
        print("Simulating gen",g,":")
        generation.simulate_generation()
        generation.next_gen()
    
if __name__ == "__main__":
    main()



    # def reset_simulation(self):
    #     self.pos =  [frame_x//2, frame_y//2]
    #     self.body = [[self.pos[0], self.pos[1]-10*i] for i in range(3)]
    #     self.length = 3
    #     self.direction = 'UP'
    #     self.change_to = self.direction
    #     self.food_pos = [r.randrange(1, (frame_x//10)) * 10, r.randrange(1, (frame_y//10)) * 10]
    #     self.food_spawn = True
    #     self.dead = False
    #     self.reset_framebuffer()