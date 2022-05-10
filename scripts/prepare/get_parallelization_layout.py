# This script will harvest the parallelization info from all models in the input directory.
# The function will return this information in a dictionary.

import math
import os
import re
import sys



def get_parallelization_layout(IOW_ESM_ROOT):        # root directory of IOW ESM

    # Read global options file
    sys.path.append(IOW_ESM_ROOT + "/scripts/run")
    from parse_global_settings import GlobalSettings
    global_settings = GlobalSettings(IOW_ESM_ROOT)   
   
    # for model handlin
    from model_handling import get_model_handlers, ModelTypes    

    # get a list of all subdirectories in "input" folder -> these are the models
    model_handlers = get_model_handlers(global_settings)
    models = list(model_handlers.keys())

    model_threads = [0 for model in models]     # list how many threads this model uses
    model_executable = ['' for model in models] # list the name of this model's executable 

    total_threads = 0
    total_cores = 0
    total_nodes = 0
    threads = []

    from model_handling_flux import FluxCalculatorModes

    core = 0
    node = 0
    first_thread_of_flux_calculator = True

    # Loop over the models to find out how many threads they will need
    for i, model in enumerate(models):
        myexecutable = model_handlers[model].get_model_executable()
        mythreads = model_handlers[model].get_num_threads()
            
        # fill in the number of threads and executable names into the list
        model_threads[i]=mythreads
        model_executable[i]=myexecutable

        total_threads += mythreads

        if global_settings.flux_calculator_mode == FluxCalculatorModes.on_bottom_cores:
            if model_handlers[model].model_type == ModelTypes.flux_calculator:
                continue

        for j in range(mythreads):
            threads.append({    "model" : model,
                                "model_type" : model_handlers[model].model_type,
                                "core" : core,
                                "node" : node,
                                "first_of_model" : (j==0),
                                "first_of_node" : (core == 0) or (j==0) })

            if global_settings.flux_calculator_mode == FluxCalculatorModes.on_bottom_cores:
                if model_handlers[model].model_type == ModelTypes.bottom:     
                    threads.append({    "model" : "flux_calculator",
                                        "model_type" : ModelTypes.flux_calculator,
                                        "core" : core,
                                        "node" : node,
                                        "first_of_model" : first_thread_of_flux_calculator,
                                        "first_of_node" : (core == 0) or (j==0) })    
                    first_thread_of_flux_calculator = False                                           

            core += 1
            total_cores += 1
            if core % global_settings.cores_per_node == 0:
                core = 0
                node += 1   
                total_nodes +=1                          

    # started from zero so add one for the total number
    total_nodes +=1
    total_cores += 1

    this_thread = [0]*total_threads
    this_core = [0]*total_threads
    this_node = [0]*total_threads
    this_model = [0]*total_threads
    this_firstinnode = [True]*total_threads
    this_firstthread = [True]*total_threads

    for i, thread in enumerate(threads):
        this_thread[i] = i
        this_core[i] = thread["core"]
        this_node[i] = thread["node"]
        this_model[i] = thread["model"]
        this_firstinnode[i] = thread["first_of_node"]
        this_firstthread[i] = thread["first_of_model"]


    return {'total_threads': total_threads, 'total_cores': total_cores, 'total_nodes': total_nodes, 
            'models': models, 'model_threads': model_threads, 'model_executable': model_executable,
            'this_thread': this_thread, 'this_core': this_core, 'this_node': this_node, 'this_model': this_model, 
            'this_firstinnode': this_firstinnode, 'this_firstthread': this_firstthread}


