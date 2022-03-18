# This script is executed by every MPI process.
# It checks if the model succeeded. Otherwise it writes a "failed_<modelname>.txt" marker file to the work directory.

import glob
import os
import shutil
import time
import sys

# get the model handler for this process
from model_handling import get_model_handler

# wait five seconds to allow for write procedures to finish
time.sleep(5.0)

# get current folder and check if it is scripts/run
mydir = os.getcwd()
if (mydir[-12:] != '/scripts/run'):
    print('ERROR: mpi_task.py was started from outside the folder ${IOW_ESM_ROOT}/scripts/run')
    sys.exit()

# if we started from scripts/run we know our root directory
IOW_ESM_ROOT = mydir[0:-12]

###################################
# STEP 1: Read in global settings #
###################################
from parse_global_settings import GlobalSettings
global_settings = GlobalSettings(IOW_ESM_ROOT)

###############################################
# STEP 2: Find out the parallelization layout #
###############################################
sys.path.append(IOW_ESM_ROOT + "/scripts/prepare")
from get_parallelization_layout import get_parallelization_layout
layout = get_parallelization_layout(IOW_ESM_ROOT)

#############################################################################
# STEP 3: Find out my own thread number and which model I have been running #
#############################################################################
exec(global_settings.python_get_rank, globals()) # the expression python_get_rank is defined in global_settings.py
my_model = layout['this_model'][int(my_id)]

firstinnode = layout['this_firstinnode'] # only do something if I am the first thread of this model on my node
firstthread = layout['this_firstthread'] # only do something if I am the first thread of this model 
if firstinnode[my_id]:

    ###############################################################################################
    # STEP 4: Find out the global and local workdir and the end date from an environment variable #
    ###############################################################################################
    local_workdir_base = os.environ["IOW_ESM_LOCAL_WORKDIR_BASE"]
    global_workdir_base = os.environ["IOW_ESM_GLOBAL_WORKDIR_BASE"]
    end_date = os.environ["IOW_ESM_END_DATE"] 
    start_date = os.environ["IOW_ESM_START_DATE"]        

    ############################################
    # STEP 5: Check if the model run succeeded #
    ############################################
    if firstthread[my_id]: 
        model_handler = get_model_handler(global_settings, my_model)
        if not model_handler.check_for_success(local_workdir_base, start_date, end_date):
            failfile = open(global_workdir_base+'/failed_'+my_model+'.txt', 'w')
            failfile.writelines('Model '+my_model+' failed and did not reach the end date '+str(end_date)+'\n')
            failfile.close()

    ##########################################################################
    # STEP 6: If required, copy the work directory to the global file system #
    ##########################################################################
    # we have to copy step by step since all processes copy in parallel
    if (not os.path.isdir(global_workdir_base+'/'+my_model)):
        os.system('mkdir '+global_workdir_base+'/'+my_model)
    files = [d for d in os.listdir(local_workdir_base+'/'+my_model+'/') if os.path.isfile(os.path.join(local_workdir_base+'/'+my_model+'/',d))]
    for file in files:
        os.system('cp --preserve=links '+local_workdir_base+'/'+my_model+'/'+file+' '+global_workdir_base+'/'+my_model+'/.')
    folders = [d for d in os.listdir(local_workdir_base+'/'+my_model+'/') if os.path.isdir(os.path.join(local_workdir_base+'/'+my_model+'/',d))]
    for folder in folders:
        if (not os.path.isdir(global_workdir_base+'/'+my_model+'/'+folder)):
            os.system('mkdir '+global_workdir_base+'/'+my_model+'/'+folder)
        files = [d for d in os.listdir(local_workdir_base+'/'+my_model+'/'+folder+'/') if os.path.isfile(os.path.join(local_workdir_base+'/'+my_model+'/'+folder+'/',d))]
        for file in files:
            os.system('cp --preserve=links '+local_workdir_base+'/'+my_model+'/'+folder+'/'+file+' '+global_workdir_base+'/'+my_model+'/'+folder+'/.')
    os.system('sync')
