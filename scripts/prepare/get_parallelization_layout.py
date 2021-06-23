# This script will harvest the parallelization info from all models in the input directory.
# The function will return this information in a dictionary.

import math
import os
import re
import sys

def get_parallelization_layout(IOW_ESM_ROOT):        # root directory of IOW ESM

    # Read global options file
    exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read(), globals())# read in global options

    # Get a list of all subdirectories in "input" folder -> these are the models
    models = [d for d in os.listdir(IOW_ESM_ROOT+'/input/') if os.path.isdir(os.path.join(IOW_ESM_ROOT+'/input/',d))]

    model_threads = [0 for model in models]     # list how many threads this model uses
    model_executable = ['' for model in models] # list the name of this model's executable

    # Possibly add flux_calculator as an additional model
    if flux_calculator_mode=='single_core_per_bottom_model':
        models           = models           + ['flux_calculator']
        model_threads    = model_threads    + [0]
        model_executable = model_executable + ['']

    # Loop over the models to find out how many threads they will need
    for i, model in enumerate(models):
        mythreads = 0
        # check which model it is
        if model[0:5]=='CCLM_': 
            myexecutable = 'lmparbin'
            # CCLM model - parallelization is described in INPUT_ORG, e.g. nprocx= 8, nprocy= 24
            inputfile = IOW_ESM_ROOT+'/input/'+model+'/INPUT_ORG'
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
        if model[0:5]=='MOM5_':
            myexecutable = 'fms_MOM_SIS.x'
            # MOM5 model - parallelization is given in input.nml in section &ocean_model_nml
            # "layout = 14,10"  e.g. means 14x10 rectangles exist, but a few of them may be masked out
            # "mask_table = 'INPUT/mask_table'" (optional) means we will find this file there
            # it contains the number of masked (=inactive) rectangles in the first line
            inputfile = IOW_ESM_ROOT+'/input/'+model+'/input.nml'
            mythreads_x = 0
            mythreads_y = 0
            mythreads_masked = 0
            if not os.path.isfile(inputfile):
                print('Could not determine parallelization layout because the following file was missing: '+inputfile)
            else:
                status = 'before' # make sure we seek in the correct area only
                f = open(inputfile)
                for line in f:
                    if (line.strip()=='&ocean_model_nml') & (status == 'before'):
                        status = 'active' # start searching
                    if (line.strip()=='/') & (status == 'active'):
                        status = 'after'  # stop searching
                    if (status == 'active'):                        
                        match = re.search("layout\s*=\s*(\d+)\s*,\s*(\d+)", line) # search for two comma-separated numbers after 'layout=', but allow spaces
                        if match:
                            mythreads_x = int(match.group(1))
                            mythreads_y = int(match.group(2))
                        match = re.search("mask_table\s*=\s*'([^']*)'", line) # search for anything between single quotes behind 'mask_table=', 
                                                                              # but allow spaces
                        if match:
                            maskfile = IOW_ESM_ROOT+'/input/'+model+'/'+match.group(1)
                            if not os.path.isfile(maskfile):
                                print('Could not determine parallelization layout because the following MOM5 mask file was missing: '+maskfile)
                                mythreads_masked = -1
                            else:
                                fm = open(maskfile)
                                mythreads_masked = int(fm.readline().strip())
                                fm.close()
                f.close()
                if mythreads_masked < 1: # did not find mask file
                    mythreads = 0
                else:
                    mythreads = mythreads_x * mythreads_y - mythreads_masked
        if model=='flux_calculator':
            mythreads = len(models)-2
            myexecutable = 'flux_calculator'
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
