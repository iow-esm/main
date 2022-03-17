# This script will read the grid information of all submodels and create the required mapping files for the OASIS coupler.
# Call this script from the /scripts/prepare folder

import os
import shutil
import sys

import grid_create_exchangegrid_MOM5
import grid_create_uv_t_regridding

import grid_create_maskfile_CCLM

# get current folder and check if it is scripts/run
mydir = os.getcwd()
fail = False
if (mydir[-16:] != '/scripts/prepare'):
    fail = True
else:
    IOW_ESM_ROOT = mydir[0:-16]

if (fail):
    print('usage: python3 ./create_mappings.py')
    print('should be called from ${IOW_ESM_ROOT}/scripts/prepare')
    sys.exit()

#########################################################################################################
# STEP 1: Find out which models we have, and for each of them convert the model grid(s) to SCRIP format #
#########################################################################################################

# get a list of all subdirectories in "input" folder -> these are the models
models = [d for d in os.listdir(IOW_ESM_ROOT+'/input/') if os.path.isdir(os.path.join(IOW_ESM_ROOT+'/input/',d))]

# import model handling modules
sys.path.append(IOW_ESM_ROOT + "/scripts/run")

from parse_global_settings import GlobalSettings
global_settings = GlobalSettings(IOW_ESM_ROOT)

import importlib
model_handlers = {}
for model in models:
    try:   
        model_handling_module = importlib.import_module("model_handling_" + model[0:4])
        model_handlers[model] = model_handling_module.ModelHandler(global_settings, model)
    except:
        print("No handler has been found for model " + model + ". Add a module model_handling_" + model[0:4] + ".py")
        pass # TODO pass has to be replaced by exit when models have a handler 

# find out which model it is and run the corresponding function
for model in models:
    if model[0:5]=='MOM5_' or model[0:5]=='CCLM_': # TODO remove if condition when all models have handlers
        print('creating SCRIP grids for model '+model)
        model_handlers[model].grid_convert_to_SCRIP()

###########################################################################################################
# STEP 2: Walk through all ocean and land models to create exchange grid and mappings to/from atmos model #
###########################################################################################################

# find CCLM model - this is atmos model
atmosmodel = -1
for i,model in enumerate(models):
    if model[0:5]=='CCLM_':
        atmosmodel = i

if atmosmodel<0:
    print('ERROR: No atmospheric model (CCLM_...) found in input folder.')
    sys.exit()

# for all other models, create mappings and exchange grid
for model in models:
    if model[0:5]=='MOM5_':
        print('creating t_grid mappings:  '+model+' <-> '+models[atmosmodel])
        grid_create_exchangegrid_MOM5.grid_create_exchangegrid_MOM5(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                                    models[atmosmodel],  # name of atmospheric model instance
                                                                    model,               # name of bottom model instance 
                                                                    't_grid')            # 't_grid' or 'u_grid' or 'v_grid'
        print('creating u_grid mappings:  '+model+' <-> '+models[atmosmodel])
        grid_create_exchangegrid_MOM5.grid_create_exchangegrid_MOM5(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                                    models[atmosmodel],  # name of atmospheric model instance
                                                                    model,               # name of bottom model instance 
                                                                    'u_grid')            # 't_grid' or 'u_grid' or 'v_grid'
        print('creating v_grid mappings:  '+model+' <-> '+models[atmosmodel])
        grid_create_exchangegrid_MOM5.grid_create_exchangegrid_MOM5(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                                    models[atmosmodel],  # name of atmospheric model instance
                                                                    model,               # name of bottom model instance 
                                                                    'v_grid')            # 't_grid' or 'u_grid' or 'v_grid'

###########################################################################
# STEP 3: Create regridding matrices between u,v and t grid exchangegrids #
###########################################################################

for i,model in enumerate(models):
    if i!=atmosmodel:
        print('creating regridding matrices between u-grid and t-grid:  '+model+' <-> '+models[atmosmodel])
        grid_create_uv_t_regridding.grid_create_uv_t_regridding(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                         model,               # name of bottom model instance 
                                                         'u_grid')            # 'u_grid' or 'v_grid'
        print('creating regridding matrices between v-grid and t-grid:  '+model+' <-> '+models[atmosmodel])
        grid_create_uv_t_regridding.grid_create_uv_t_regridding(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                         model,               # name of bottom model instance 
                                                         'v_grid')            # 'u_grid' or 'v_grid'

	

###########################################################
# STEP 4: Concatenate all exchange grids into a large one #
###########################################################

print('combining exchange grid files:  ')

# for the moment we only have one exchange grid, so just copy it
for i,model in enumerate(models):
    if i!=atmosmodel:
        print('    adding grids for '+model+':')
        print('        t_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/t_grid_exchangegrid.nc', IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/t_grid_exchangegrid.nc')
        print('        u_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/u_grid_exchangegrid.nc', IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/u_grid_exchangegrid.nc')
        print('        v_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/v_grid_exchangegrid.nc', IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/v_grid_exchangegrid.nc')
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
for i,model in enumerate(models):
    if i!=atmosmodel:
        print('    adding mapping for '+model+':')
        print('        t_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/remap_t_grid_exchangegrid_to_'+models[atmosmodel]+'.nc',
                    IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/remap_t_grid_exchangegrid_to_'+models[atmosmodel]+'.nc')
        print('        u_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/remap_u_grid_exchangegrid_to_'+models[atmosmodel]+'.nc',
                    IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/remap_u_grid_exchangegrid_to_'+models[atmosmodel]+'.nc')
        print('        v_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/remap_v_grid_exchangegrid_to_'+models[atmosmodel]+'.nc',
                    IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/remap_v_grid_exchangegrid_to_'+models[atmosmodel]+'.nc')
        # copy mapping back from atmospheric grid to exchange grid
        print('    adding remapping for '+model+':')
        for grid in ['u', 'v', 't']:
            print('        ' + grid + '_grid...')
            shutil.copy(IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/remap_to_exchangegrid_for_'+model+'_'+grid+'_grid.nc',
                IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/remap_'+ grid +'_grid_' + models[atmosmodel] + '_to_exchangegrid.nc')
        print('        done.')

###################################################################
# STEP 6: Concatenate the regridding matrices (u<->t, v<->t_grid) #
###################################################################

# for the moment we only have one exchange grid, so just copy it
for i,model in enumerate(models):
    if i!=atmosmodel:
        print('    adding regriddings for '+model+':')
        print('        t_grid -> u_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/regrid_t_grid_'+model+'_to_u_grid.nc', IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/regrid_t_grid_to_u_grid.nc')
        print('        u_grid -> t_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/regrid_u_grid_'+model+'_to_t_grid.nc', IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/regrid_u_grid_to_t_grid.nc')
        print('        t_grid -> v_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/regrid_t_grid_'+model+'_to_v_grid.nc', IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/regrid_t_grid_to_v_grid.nc')
        print('        v_grid -> t_grid...')
        shutil.copy(IOW_ESM_ROOT+'/input/'+model+'/mappings/regrid_v_grid_'+model+'_to_t_grid.nc', IOW_ESM_ROOT+'/input/'+models[atmosmodel]+'/mappings/regrid_v_grid_to_t_grid.nc')
     
# later, two options:
#   (a) fluxes for every bottom model are calculated in a single MPI task of the flux calculator
#       => just concatenate the regridding matrices but increase the indices
#   (b) there is a bottom model whose fluxes are split to different MPI tasks
#       => For each task, create the own regridding matrices inside the own extended subgrid of the exchange grid (see STEP 4)


##########################################################################################################################
# STEP 7: write a file for the atmos model which states the fraction of each grid cell which does bidirectional coupling #
##########################################################################################################################

print('write maskfile for atmos model, stating which cells are coupled...  ')
model = models[atmosmodel]
if model[0:5]=='CCLM_':
    grid_create_maskfile_CCLM.grid_create_maskfile_CCLM(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                        models[atmosmodel], "t_grid")  # name of atmospheric model instance, which grid
    grid_create_maskfile_CCLM.grid_create_maskfile_CCLM(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                        models[atmosmodel], "u_grid")  # name of atmospheric model instance, which grid   
    grid_create_maskfile_CCLM.grid_create_maskfile_CCLM(IOW_ESM_ROOT,        # root directory of IOW ESM
                                                        models[atmosmodel], "v_grid")  # name of atmospheric model instance, which grid                                                        
print('done.')

