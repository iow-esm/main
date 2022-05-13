# This script will read the grid information of all submodels and create the required mapping files for the OASIS coupler.
# Call this script from the /scripts/prepare folder

import os
import sys
import glob

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

# find atmos model
atmos_model = None
for model in models:
    if model_handlers[model].model_type == ModelTypes.atmosphere:
        atmos_model = model
        break # there can only be one

if atmos_model is None:
    print('ERROR: No atmospheric model found in input folder.')
    sys.exit()

print("Found atmospheric model " + atmos_model)

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


#TODO don't restore backup when everything works as expected
for model in bottom_models + [atmos_model]:
    model_dir = global_settings.root_dir + "/input/" + model + "/mappings"

    #TODO don't do backup when everything works as expected
    if os.path.isdir(model_dir + "/serial"):
        os.system("rm " + model_dir + "/*.nc")
        os.system("mv " + model_dir + "/serial/* " + model_dir + "/")

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
        print('Apply ' + model + ' domain decomposition to the ' + grid + ' exchange grid...')
        # get the corresponding exchange grid task vector
        eg_tasks[grid] = parallelize_mappings_helpers.get_exchange_grid_task_vector(global_settings, model, model_tasks, grid, work_dir)
        print('...done.')

    for grid in model_handlers[model].grids:
        print('Add task vector for the ' + grid + ' exchange grid...')
        parallelize_mappings_helpers.add_exchange_grid_task_vector(global_settings, model, eg_tasks[grid], grid, work_dir)
        print('...done.')

    halo_cells = {}
    for grid in model_handlers[model].grids:
        print('Getting halo cells for the ' + grid + ' exchange grid...')
        halo_cells[grid] = parallelize_mappings_helpers.get_halo_cells(global_settings, model, grid, work_dir)
        print('...done.')
        #parallelize_mappings_helpers.visualize_domain_decomposition(global_settings, model, grid, model_tasks, eg_tasks[grid], halo_cells[grid])

    for grid in model_handlers[model].grids:
        # sort the exchange grid according to the tasks, get the permutation vector
        print('Sorting the ' + grid + ' exchange grid according to the domain decomposition...')
        permutation = parallelize_mappings_helpers.sort_exchange_grid(global_settings, model, grid, halo_cells[grid], work_dir)
        print('...done.')
    
    for grid in model_handlers[model].grids:
        print('Updating the remapping between model ' + model + ' ' + grid + ' and exchange ' + grid + '...')
        parallelize_mappings_helpers.update_remapping(global_settings, model, grid, work_dir)
        print('...done.')
        print('Updating the regridding from ' + grid + ' exchange grid...')
        parallelize_mappings_helpers.update_regridding(global_settings, model, grid, work_dir)
        print('...done.')

# combine updated grid, remapping and regridding files
print("Combining updated exchage grids from bottom models " + str(bottom_models) + " to common exchange grid for atmos model " + atmos_model + "...")
atmos_work_dir = global_settings.root_dir + "/input/" + atmos_model + "/mappings/parallel"
if os.path.isdir(atmos_work_dir):
    os.system('rm -rf '+atmos_work_dir)
os.makedirs(atmos_work_dir)

# currently there is only one exchange grid so just copy it from the bottom model to the atmos model
for model in bottom_models:
    bottom_work_dir = global_settings.root_dir + "/input/" + model + "/mappings/parallel"
    for grid in model_handlers[model].grids:
        os.system("cp " + bottom_work_dir + "/" + grid + "_exchangegrid.nc " + atmos_work_dir + "/")
    # copy regridding as well
    for regrid_file in glob.glob(bottom_work_dir + "/regrid_*.nc"):
        # create new file name without the model name (since this file should mimic the merged one from many bottom models)
        new_file_name = regrid_file.split("/")[-1]
        new_file_name = new_file_name.split(model)[0] + new_file_name.split(model)[1][1:]
        os.system("cp " + regrid_file + " " + atmos_work_dir + "/" + new_file_name)
print('...done.')

# find total set of available grids
all_grids = []
for model in bottom_models:
    all_grids += model_handlers[model].grids

all_grids = list(set(all_grids))

# update mapping between updated exchange grids and atmos model grid
for grid in all_grids:
    print('Updating the remapping between model ' + atmos_model + ' ' + grid + ' and exchange ' + grid + '...')
    parallelize_mappings_helpers.update_remapping(global_settings, atmos_model, grid, atmos_work_dir)
    print('...done.')
  
# overwrite old files with work
for model in bottom_models + [atmos_model]:
    print("Overwrite old files with new files...")
    model_dir = global_settings.root_dir + "/input/" + model + "/mappings"
    work_dir = model_dir + "/parallel"

    #TODO don't do backup when everything works as expected
    if os.path.isdir(model_dir + "/serial"):
        os.system('rm -rf '+ model_dir + "/serial")
    os.makedirs(model_dir + "/serial")
    os.system("rsync -t " + model_dir + "/* " + model_dir + "/serial/")
    os.system("rm " + model_dir + "/*.nc")
    # restore unchanged files from serial
    os.system("cp " +  model_dir + "/serial/maskfile*.nc " + model_dir)
    os.system("cp " +  model_dir + "/serial/?_grid.nc " + model_dir)

    # move the files
    os.system("mv " + work_dir + "/* " + model_dir + "/")
    os.system("rm -rf " + work_dir)

#for model in bottom_models:
#    for grid in model_handlers[model].grids:
#        parallelize_mappings_helpers.visualize_domain_decomposition(global_settings, model, grid, model_tasks)