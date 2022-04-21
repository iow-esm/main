# This script will harvest the parallelization info from all models in the input directory.
# The function will return this information in a dictionary.

import math
import os
import re
import sys

def get_parallelization_layout(global_settings):        # root directory of IOW ESM
       
    # for model handlin
    from model_handling import get_model_handlers    

    # get a list of all subdirectories in "input" folder -> these are the models
    model_handlers = get_model_handlers(global_settings)
    models = list(model_handlers.keys())

    model_threads = [0 for model in models]     # list how many threads this model uses
    model_executable = ['' for model in models] # list the name of this model's executable 

    # Loop over the models to find out how many threads they will need
    for i, model in enumerate(models):
        myexecutable = model_handlers[model].get_model_executable()
        mythreads = model_handlers[model].get_num_threads()
            
        # fill in the number of threads and executable names into the list
        model_threads[i]=mythreads
        model_executable[i]=myexecutable
    
    # get total number of threads and nodes
    total_threads = sum(model_threads)
    total_cores = total_threads                        # simple layout, one thread per core, may change later
    total_nodes = math.ceil(total_threads / global_settings.cores_per_node) # total number of nodes needed

    # now generate a list for every thread which gives its core, node and model, 
    # and states whether it is the first thread of this model on its node or the first task of this model in total
    this_thread = [0]*total_threads
    this_core = [0]*total_threads
    this_node = [0]*total_threads
    this_model = [0]*total_threads
    this_firstinnode = [True]*total_threads
    this_firstthread = [True]*total_threads
    model_i = 0
    model_num = 0 
    node_i = 0
    node_num = 0
    for i in range(total_threads):
        while model_i >= model_threads[model_num]:
            model_i = 0
            model_num = model_num + 1
        while node_i >= global_settings.cores_per_node:
            node_i = 0
            node_num = node_num + 1
        this_thread[i] = i
        this_core[i] = node_i
        this_node[i] = node_num
        this_model[i] = models[model_num]
        this_firstinnode[i] = (node_i == 0) | (model_i == 0) # whether it is the first thread of this model on its node
        this_firstthread[i] = (model_i == 0)                 # whether it is the first thread of this model in total
        model_i = model_i + 1
        node_i = node_i + 1

    return {'total_threads': total_threads, 'total_cores': total_cores, 'total_nodes': total_nodes, 
            'models': models, 'model_threads': model_threads, 'model_executable': model_executable,
            'this_thread': this_thread, 'this_core': this_core, 'this_node': this_node, 'this_model': this_model, 
            'this_firstinnode': this_firstinnode, 'this_firstthread': this_firstthread}
