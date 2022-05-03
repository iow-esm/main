# This script will read the grid information of all submodels and create the required mapping files for the OASIS coupler.
# Call this script from the /scripts/prepare folder

import os
import sys

import parallelize_mappings_helpers

# get current folder and check if it is scripts/run
mydir = os.getcwd()
if (mydir[-16:] != '/scripts/prepare'):
    print('usage: python3 ./parallelize_mappings.py')
    print('should be called from ${IOW_ESM_ROOT}/scripts/prepare')
    sys.exit()

# if we started from scripts/run we know our root directory
IOW_ESM_ROOT = mydir[0:-16]

#########################################################################################################
# STEP 1a: Find out which models we have #
#########################################################################################################

# import the global_settings parser and the model handling modules
sys.path.append(IOW_ESM_ROOT + "/scripts/run")
from parse_global_settings import GlobalSettings
from model_handling import get_model_handlers, ModelTypes, GridTypes

# parse the global settings
global_settings = GlobalSettings(IOW_ESM_ROOT)

# get the model handlers
model_handlers = get_model_handlers(global_settings)
models = list(model_handlers.keys())

# get list of bottom models 
bottom_models = []
for model in models:
    if model_handlers[model].model_type == ModelTypes.bottom:
        bottom_models.append(model)

if bottom_models == []:
    print('ERROR: No bottom models found in input folder.')
    sys.exit()
    
for model in bottom_models:
    print("Found bottom model " + model)

#########################################################################################################
# STEP 1b: For each of them get the domain decomposition                                                #
#########################################################################################################



# do the conversion of model grids to the SCRIP format
for model in bottom_models:

    work_dir = global_settings.root_dir + "/input/" + model + "/mappings/parallel"
    if os.path.isdir(work_dir):
       os.system('rm -rf '+work_dir)
    # create it
    os.makedirs(work_dir)

    print('Getting domain decomposition for model ' + model + '...')
    # get model task vector from model handler
    model_tasks = model_handlers[model].get_domain_decomposition()
    print('...done.')

    eg_tasks = {}
    for grid in model_handlers[model].grids:
        print('Getting domain decomposition for the ' + grid + ' exchange grid...')
        # get the corresponding exchange grid task vector
        eg_tasks[grid] = parallelize_mappings_helpers.add_exchange_grid_task_vector(global_settings, model, model_tasks, grid, work_dir)
        print('...done.')

    halo_cells = {}
    for grid in model_handlers[model].grids:
        print('Getting halo cells for the ' + grid + ' exchange grid...')
        halo_cells[grid] = parallelize_mappings_helpers.get_halo_cells(global_settings, model, grid, work_dir)
        print('...done.')
        #parallelize_mappings_helpers.visualize_domain_decomposition(global_settings, model, model_tasks, eg_tasks[grid], grid, halo_cells[grid])

    for grid in model_handlers[model].grids:
        # sort the exchange grid according to the tasks, get the permutation vector
        print('Sorting the ' + grid + ' exchange grid according to the domain decomposition...')
        permutation = parallelize_mappings_helpers.sort_exchange_grid(global_settings, model, grid, halo_cells[grid], work_dir)
        print('...done.')
    
    for grid in model_handlers[model].grids:
        parallelize_mappings_helpers.update_remapping(global_settings, model, grid, work_dir)
