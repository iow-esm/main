# This script will read the grid information of all submodels and create the required mapping files for the OASIS coupler.
# Call this script from the /scripts/prepare folder

import os
import shutil
import sys

import grid_create_exchangegrid_MOM5
import grid_create_uv_t_regridding

import grid_create_maskfile_CCLM

run_name = str(sys.argv[1])

# get current folder and check if it is scripts/run
mydir = os.getcwd()
if (mydir[-16:] != '/scripts/prepare'):
    print('usage: python3 ./create_mappings.py')
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
from model_handling import get_model_handlers, ModelTypes

# parse the global settings
global_settings = GlobalSettings(IOW_ESM_ROOT, run_name)

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

for model in models:
    old_mappings = global_settings.input_dir+"/"+model+"/mappings"
    if os.path.isdir(old_mappings):
        print("Remove old mappings for model " + model + ".")
        os.system("rm -r " + old_mappings)

#########################################################################################################
# STEP 1b: For each of them convert the model grid(s) to SCRIP format                                   #
#########################################################################################################

# do the conversion of model grids to the SCRIP format
for model in [atmos_model] + bottom_models:
    print('creating SCRIP grids for model '+model)
    model_handlers[model].grid_convert_to_SCRIP()

###########################################################################################################
# STEP 2: Walk through all ocean and land models to create exchange grid and mappings to/from atmos model #
###########################################################################################################

# for all bottom models, create mappings and exchange grid
for model in bottom_models:

    # TODO: here should be a double loop over
    #   1. atmospheric grids
    #   2. all available bootom grids
    print('creating t_grid mappings:  '+model+' <-> '+atmos_model)
    grid_create_exchangegrid_MOM5.grid_create_exchangegrid_MOM5(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                                atmos_model,  # name of atmospheric model instance
                                                                model,               # name of bottom model instance 
                                                                't_grid')            # 't_grid' or 'u_grid' or 'v_grid'
    print('creating u_grid mappings:  '+model+' <-> '+atmos_model)
    grid_create_exchangegrid_MOM5.grid_create_exchangegrid_MOM5(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                                atmos_model,  # name of atmospheric model instance
                                                                model,               # name of bottom model instance 
                                                                'u_grid')            # 't_grid' or 'u_grid' or 'v_grid'
    print('creating v_grid mappings:  '+model+' <-> '+atmos_model)
    grid_create_exchangegrid_MOM5.grid_create_exchangegrid_MOM5(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                                atmos_model,  # name of atmospheric model instance
                                                                model,               # name of bottom model instance 
                                                                'v_grid')            # 't_grid' or 'u_grid' or 'v_grid'

###########################################################################
# STEP 3: Create regridding matrices between u,v and t grid exchangegrids #
###########################################################################

for model in bottom_models:
        
    print('creating regridding matrices between u-grid and t-grid:  '+model+' <-> '+atmos_model)
    grid_create_uv_t_regridding.grid_create_uv_t_regridding(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                     model,               # name of bottom model instance 
                                                     'u_grid')            # 'u_grid' or 'v_grid'
    print('creating regridding matrices between v-grid and t-grid:  '+model+' <-> '+atmos_model)
    grid_create_uv_t_regridding.grid_create_uv_t_regridding(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                     model,               # name of bottom model instance 
                                                     'v_grid')            # 'u_grid' or 'v_grid'

	

###########################################################
# STEP 4: Concatenate all exchange grids into a large one #
###########################################################

print('combining exchange grid files:  ')

# for the moment we only have one exchange grid, so just copy it
for model in bottom_models:
        
    print('    adding grids for '+model+':')
    print('        t_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/t_grid_exchangegrid.nc', global_settings.input_dir+'/'+atmos_model+'/mappings/t_grid_exchangegrid.nc')
    print('        u_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/u_grid_exchangegrid.nc', global_settings.input_dir+'/'+atmos_model+'/mappings/u_grid_exchangegrid.nc')
    print('        v_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/v_grid_exchangegrid.nc', global_settings.input_dir+'/'+atmos_model+'/mappings/v_grid_exchangegrid.nc')
    print('        done.')
# later, two options:
#   (a) fluxes for every bottom model are calculated in a single MPI task of the flux calculator
#       => just concatenate the exchange grids
#   (b) there is a bottom model whose fluxes are split to different MPI tasks
#       => (1) select the cells that a task shall calculate
#          (2) add the cells required for the regridding (u_grid <-> t_grid, v_grid <-> t_grid)
#          (3) concatenate these extended sub-grids, so some exchange grid cells may occur more than once
        

#############################################################################################################
# STEP 5: combine the files exchange_to_atmos_file into a common one, considering the priority of the grids # 
#############################################################################################################

print('create common mapping file:  ')

# for the moment we only have one exchange grid, so just copy it
for model in bottom_models:

    print('    adding mapping for '+model+':')
    print('        t_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/remap_t_grid_exchangegrid_to_'+atmos_model+'.nc',
                global_settings.input_dir+'/'+atmos_model+'/mappings/remap_t_grid_exchangegrid_to_'+atmos_model+'.nc')
    print('        u_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/remap_u_grid_exchangegrid_to_'+atmos_model+'.nc',
                global_settings.input_dir+'/'+atmos_model+'/mappings/remap_u_grid_exchangegrid_to_'+atmos_model+'.nc')
    print('        v_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/remap_v_grid_exchangegrid_to_'+atmos_model+'.nc',
                global_settings.input_dir+'/'+atmos_model+'/mappings/remap_v_grid_exchangegrid_to_'+atmos_model+'.nc')
    # copy mapping back from atmospheric grid to exchange grid
    print('    adding remapping for '+model+':')
    for grid in ['u', 'v', 't']:
        print('        ' + grid + '_grid...')
        shutil.copy(global_settings.input_dir+'/'+atmos_model+'/mappings/remap_to_exchangegrid_for_'+model+'_'+grid+'_grid.nc',
            global_settings.input_dir+'/'+atmos_model+'/mappings/remap_'+ grid +'_grid_' + atmos_model + '_to_exchangegrid.nc')
    print('        done.')

###################################################################
# STEP 6: Concatenate the regridding matrices (u<->t, v<->t_grid) #
###################################################################

# for the moment we only have one exchange grid, so just copy it
for model in bottom_models:
    print('    adding regriddings for '+model+':')
    print('        t_grid -> u_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/regrid_t_grid_'+model+'_to_u_grid.nc', global_settings.input_dir+'/'+atmos_model+'/mappings/regrid_t_grid_to_u_grid.nc')
    print('        u_grid -> t_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/regrid_u_grid_'+model+'_to_t_grid.nc', global_settings.input_dir+'/'+atmos_model+'/mappings/regrid_u_grid_to_t_grid.nc')
    print('        t_grid -> v_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/regrid_t_grid_'+model+'_to_v_grid.nc', global_settings.input_dir+'/'+atmos_model+'/mappings/regrid_t_grid_to_v_grid.nc')
    print('        v_grid -> t_grid...')
    shutil.copy(global_settings.input_dir+'/'+model+'/mappings/regrid_v_grid_'+model+'_to_t_grid.nc', global_settings.input_dir+'/'+atmos_model+'/mappings/regrid_v_grid_to_t_grid.nc')
     
# later, two options:
#   (a) fluxes for every bottom model are calculated in a single MPI task of the flux calculator
#       => just concatenate the regridding matrices but increase the indices
#   (b) there is a bottom model whose fluxes are split to different MPI tasks
#       => For each task, create the own regridding matrices inside the own extended subgrid of the exchange grid (see STEP 4)


##########################################################################################################################
# STEP 7: write a file for the atmos model which states the fraction of each grid cell which does bidirectional coupling #
##########################################################################################################################

print('write maskfile for atmos model, stating which cells are coupled...  ')
grid_create_maskfile_CCLM.grid_create_maskfile_CCLM(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                    atmos_model, "t_grid")  # name of atmospheric model instance, which grid
grid_create_maskfile_CCLM.grid_create_maskfile_CCLM(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                    atmos_model, "u_grid")  # name of atmospheric model instance, which grid   
grid_create_maskfile_CCLM.grid_create_maskfile_CCLM(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                    atmos_model, "v_grid")  # name of atmospheric model instance, which grid                                                        
print('done.')

from model_handling_flux import FluxCalculatorModes
# if the flux calculator should be parallized, execute the script right here (can be also started manually)
if global_settings.flux_calculator_mode != FluxCalculatorModes.single_core:
    exec(open("parallelize_mappings.py").read())