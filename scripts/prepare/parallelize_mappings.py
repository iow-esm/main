# This script will read the grid information of all submodels and create the required mapping files for the OASIS coupler.
# Call this script from the /scripts/prepare folder

import os
import shutil
import sys

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
from model_handling import get_model_handlers, ModelTypes

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
    print('getting domain decomposition for model '+model)
    model_handlers[model].get_domain_decomposition()
