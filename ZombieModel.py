# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 14:09:40 2021

@author: exs
"""


from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

import math
import random


def get_distance(pos1, pos2):
    """
    finds distance between two points given as coordinate tuple (x, y)
    """
    
    x1, y1 = pos1 
    x2, y2 = pos2 
    
    dx = x1 - x2
    dy = y1 - y2 
    
    return math.sqrt(dx**2 + dy**2)


class ZombieModel(Model):
    """ The model with some number of agents - either Human or Zombie """
    def __init__(self, human_number, grid_size, zombie_pos, startup_pos):
        self.humans = human_number
        self.total_agents = human_number + 1
        self.grid_size = grid_size
        self.startup_pos = startup_pos
        
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(grid_size, grid_size, False)
        
        ## only one zombie to start
        agent_creation_list = ['zombie'] + ['human']*human_number
        
        # create list of all possible x, y coordinates as tuples - so each coordinate can only have one agent
        all_coords = []
        for x in range(grid_size):
            for y in range(grid_size):
                all_coords += [(x, y)]
        
        # create the agents
        for n in range(self.total_agents):
            agent = SubjectAgent(n, agent_creation_list[n], self)
            
            ## add agent to the schedule
            self.schedule.add(agent)
            
            ## add agent to the grid
            if agent.state == 'zombie':
                if zombie_pos == ('?', '?'):
                    agent_coords = random.choice(all_coords)
                else:
                    agent_coords = zombie_pos
                all_coords.remove(agent_coords)
            elif self.startup_pos == []:
                agent_coords = random.choice(all_coords)
                all_coords.remove(agent_coords)
            else:
                agent_coords = self.startup_pos[n]
            
            agent.start_pos = agent_coords
            self.grid.place_agent(agent, agent_coords)
    
    
    def step(self):
        self.schedule.step()
        
        for x in self.schedule.agents:
            if x.state == 'zombie':
                x.zombie_age += 1
            elif x.state == 'human':
                x.human_age += 1
        
        


class SubjectAgent(Agent):
    """ An Agent which can be a Human or Zombie """
    
    def __init__(self, unique_id, state, model):
        super().__init__(unique_id, model)
        self.state = state # human or zombie 
        self.orig_state = state # human or zombie 
        self.zombie_age = 1 if state == 'zombie' else 0
        self.human_age = 0
        self.speed = 1 # radius of movement: hardcoded at one for now
    
    # iterator    
    def step(self):
        
        self.locate_target()
        self.move()
        
        pass
    
    
    def locate_target(self):
        ## find the closest agent of opposite type
        possible_targets = [agent for agent in self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius = self.model.grid_size)
                            if agent.state != self.state]
        
        # shuffle because 'get_neighbors' tends to order the list from bottom-left to top-right 
        ## in the case of equally distant targets it stops the target all being assigned to the most bottom-left
        random.shuffle(possible_targets)
        
        if len(possible_targets) == 0:
            self.target = []
        else:
            target_distance = [(get_distance(self.pos, agent.pos), agent) for agent in possible_targets]
            target_distance.sort(key=lambda tup: tup[0])
            self.target = target_distance[0][1]
    
    
    def move(self):
        # get agent's movement options 
        ## Note: if speed is increased for some then extra logic must be incorporated so that agents do not move to 'blocked' cells
        movement_options = [coord for coord in self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius = self.speed)
                            if self.model.grid.is_cell_empty(coord)] + [self.pos]
        
        # shuffle because 'get_neighborhood' tends to order the list from bottom-left to top-right 
        ## in the case of equally good movement options this stops the new coords being always chosen as the most bottom-left option
        random.shuffle(movement_options)
        
        
        if self.target == []:
            # if there are no agents remaining of the opposite type
            self.model.grid.move_agent(self, random.choice(movement_options))
        
        elif self.state == 'human':
            
            dist_from_target = [(get_distance(self.target.pos, coord), coord) for coord in movement_options]
            dist_from_target.sort(key=lambda tup: tup[0], reverse=True)
            
            new_coords = dist_from_target[0][1]
            self.model.grid.move_agent(self, new_coords)
        
        elif self.state == 'zombie' and self.zombie_age >= 1:
            
            # see if the zombie is adjacent to it's target human
            adj_target = [human for human in self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius = 1) if human.unique_id == self.target.unique_id]
            if len(adj_target) > 0:
                self.target.state = 'zombie'
            else:
                dist_from_target = [(get_distance(self.target.pos, coord), coord) for coord in movement_options]
                dist_from_target.sort(key=lambda tup: tup[0], reverse=False)
                
                new_coords = dist_from_target[0][1]
                self.model.grid.move_agent(self, new_coords)
            
                

