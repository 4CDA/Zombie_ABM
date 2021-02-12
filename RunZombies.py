# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 14:22:24 2021

@author: exs
"""

import numpy as np
import matplotlib.pyplot as plt

import imageio
import os

# local files
from ZombieModel import ZombieModel


        
def create_gif(file_list, destination_folder, gif_name):
    """
    Creates a GIF file of a list of .png files

    ----------
    file_list : list - of file names to create gif from.
    destination_folder : str - Name of folder in which to save gif.
    gif_name : str - Name of new gif to be saved.

    """
    
    images = []
    for filename in file_list:
        images.append(imageio.imread(filename))
    imageio.mimsave(os.path.join(destination_folder, gif_name+'.gif'), images, duration = .75)



seed_total = 1000
output_vis = True

start_humans = 9
place_zombie = (0, 0)#('?', '?')
grid_size = 10
folder = 'ZombieModelOutput'

# create the folder for storing images/gifs
if output_vis:
    try: 
        os.makedirs(folder)
    except OSError as e:
        if 'File exists' != e.strerror:
            raise

## empty lists/dicts for storing model results
t_results = []
age_average = []
age_position = {}
for x in range(grid_size):
    for y in range(grid_size):
        age_position[(x, y)] = []


## set up grid size and plot formatting
## colour
colour_dict = {'human': 'blue', 'zombie': 'red'}
# create the axis ticks - complicated because I want my output to look like a grid
i = -0.5 
ticks = []
while i < grid_size:
    ticks += [i]
    i += 1

for seed in range(seed_total):    
    
    ZombieHunt = ZombieModel(start_humans, grid_size, place_zombie, [])
    file_list = []
    
    # define the controlling parameters for the seed
    current_human_no = start_humans
    t = 0
    
    if seed%10 == 0:
        print('running seed '+str(seed)+'...')
    
    while current_human_no > 0 and t < 50:
        
        # only output 1 out of 10 seeds
        if output_vis and seed%(seed_total/10) == 0: 
            # extract data from model
            positions = [x.pos for x in ZombieHunt.schedule.agents]
            plot_colour = [colour_dict[x.state] for x in ZombieHunt.schedule.agents]
            # plot_labels = [str('Agent'+str(x.unique_id)) for x in ZombieHunt.schedule.agents]
            plot_labels = ['' for x in ZombieHunt.schedule.agents]
            
            # create graph
            x, y = zip(*positions)
            plt.scatter(x, y, c=plot_colour, s=150)
            # plt.title('seed '+str(seed)+', t = '+str(t))
            plt.title('iteration = '+str(t))
            plt.xlim(-0.5, grid_size-0.5)
            plt.ylim(-0.5, grid_size-0.5)
            
            for i, txt in enumerate(plot_labels):
                plt.annotate(txt, (x[i], y[i]))
            
            plt.xticks(ticks, "")
            plt.yticks(ticks, "")
            plt.grid(b= True, which='major', axis='both', color='black', linestyle='-', linewidth=0.5)
            # plt.show()
            
            file_name = folder+'/seed'+str(seed)+'t'+str(t)+'.png'
            file_list += [file_name]
            
            # save image then clear
            plt.savefig(file_name)
            plt.clf()
        
        # advance the control parameters
        t += 1
        current_humans = [x.start_pos for x in ZombieHunt.schedule.agents if x.state == 'human']
        current_human_no = len(current_humans)
        
        # finally iterate the model (t=0 will appear just as the initialization of the model)
        ZombieHunt.step()
    
    # record the results from the seed
    t_results += [t]
    avg = [x.human_age for x in ZombieHunt.schedule.agents if x.orig_state == 'human']
    age_average += [sum(avg)/len(avg)]
    for x in ZombieHunt.schedule.agents:
        age_position[x.start_pos] += [x.human_age]
    
    # create the gif
    if output_vis and len(file_list) > 0:
        create_gif(file_list, folder, 'seed'+str(seed))


#########################################
## Visualizations

# Histogram: Max human Life
plt.hist(t_results, bins=max(t_results)-min(t_results))
plt.title("Distribution of Max Human Age over 1000 Simulations")
plt.yticks(list(range(80, 10)), "")
if output_vis:
    plt.savefig(folder+"/Max Human Age.png")
    plt.clf()
else:
    plt.show()

# Histogram: Average Human Life
plt.hist(age_average, bins=int(np.ceil(max(t_results))-np.floor(min(t_results))))
plt.title("Distribution of Average Human Age over 1000 Simulations")
plt.yticks(list(range(80, 10)), "")
if output_vis:
    plt.savefig(folder+"/Average Human Age.png")
    plt.clf()
else:
    plt.show()


# Heat Map: Average Human life starting coords
plot_value = 'Average'
result_array = np.zeros((grid_size, grid_size))
for x in age_position:
    if plot_value == 'Average':
        result_array[x[1], x[0]] = 0 if len(age_position[x])==0 else sum(age_position[x])/len(age_position[x])
    if plot_value == 'Max':
        result_array[x[1], x[0]] = 0 if len(age_position[x])==0 else max(age_position[x])
    if plot_value == 'Min':
        result_array[x[1], x[0]] = 0 if len(age_position[x])==0 else min(age_position[x])

# plt.pcolor(result_array, cmap='hot', vmin = 0, vmax=15)
plt.pcolor(result_array, cmap='hot')

plt.title("Average human age by starting position")
plt.xticks(list(range(grid_size)), "")
plt.yticks(list(range(grid_size)), "")
plt.colorbar()
if output_vis:
    plt.savefig(folder+"/"+plot_value+" Human Age by Star Position.png")
    plt.clf()
else:
    plt.show()
