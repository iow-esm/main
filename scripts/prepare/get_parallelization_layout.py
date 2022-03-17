# This script will harvest the parallelization info from all models in the input directory.
# The function will return this information in a dictionary.

import math
import os
import re
import sys



def get_parallelization_layout(IOW_ESM_ROOT):        # root directory of IOW ESM

    # Read global options file
    exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read(), globals())# read in global options
    
    sys.path.append(IOW_ESM_ROOT + "/scripts/run")
    # TODO: exec command to be removed at some point and completely replaced by
    from parse_global_settings import GlobalSettings
    global_settings = GlobalSettings(IOW_ESM_ROOT)    

    # Get a list of all subdirectories in "input" folder -> these are the models
    models = [d for d in os.listdir(IOW_ESM_ROOT+'/input/') if os.path.isdir(os.path.join(IOW_ESM_ROOT+'/input/',d))]

    model_threads = [0 for model in models]     # list how many threads this model uses
    model_executable = ['' for model in models] # list the name of this model's executable

    # Possibly add flux_calculator as an additional model
    if flux_calculator_mode=='single_core_per_bottom_model':
        models           = models           + ['flux_calculator']
        model_threads    = model_threads    + [0]
        model_executable = model_executable + ['']
        
    import importlib
    model_handlers = {}
    for model in models:
        try:   
            model_handling_module = importlib.import_module("model_handling_" + model[0:4])
            model_handlers[model] = model_handling_module.ModelHandler(global_settings, model)
        except:
            print("No handler has been found for model " + model + ". Add a module model_handling_" + model[0:4] + ".py")
            pass # TODO pass has to be replaced by exit when models have a handler     

    # Loop over the models to find out how many threads they will need
    for i, model in enumerate(models):
        mythreads = 0
        # check which model it is
        if model[0:5] == 'I2LM_':
            myexecutable = 'int2lm.exe'
            inputfile = IOW_ESM_ROOT+'/input/'+model+'/INPUT'
            mythreads_x = 0
            mythreads_y = 0
            if not os.path.isfile(inputfile):
                print('Could not determine parallelization layout because the following file was missing: '+inputfile)
            else :
                f = open(inputfile)
                for line in f:
                    match = re.search('nprocx\s*=\s*(\d+)', line) # search for number after 'nprocx=', but allow spaces
                    if match:
                        mythreads_x = int(match.group(1))
                    match = re.search('nprocy\s*=\s*(\d+)', line) # search for number after 'nprocy=', but allow spaces
                    if match:
                        mythreads_y = int(match.group(1))
                f.close()
                mythreads = mythreads_x * mythreads_y
            if mythreads==0:
                print('Could not determine number of threads for model ',model)
                
        if model[0:5]=='MOM5_' or model=='flux_calculator' or model[0:5]=='CCLM_': #TODO remove if condition when all models have handlers
            myexecutable = model_handlers[model].get_model_executable()
            mythreads = model_handlers[model].get_num_threads()
            
        # fill in the number of threads and executable names into the list
        model_threads[i]=mythreads
        model_executable[i]=myexecutable
    
    # get total number of threads and nodes
    total_threads = sum(model_threads)
    total_cores = total_threads                        # simple layout, one thread per core, may change later
    total_nodes = math.ceil(total_threads / cores_per_node) # total number of nodes needed

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
        while node_i >= cores_per_node:
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
