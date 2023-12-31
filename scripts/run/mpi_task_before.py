# This script is executed by every MPI process.
# It will find out by the PE number which compartment model of the Earth System Model it shall run.

import os
import time
import sys

import create_work_directories

try:
    input_name = str(sys.argv[1])
except:
    input_name = ""

# get current folder and check if it is scripts/run
mydir = os.getcwd()
if (mydir[-12:] != '/scripts/run'):
    print('ERROR: mpi_task.py was started from outside the folder ${IOW_ESM_ROOT}/scripts/run')
    sys.exit()

# if we started from scripts/run we know our root directory
IOW_ESM_ROOT = mydir[0:-12]

# wait five seconds for file system
time.sleep(5.0)

###################################
# STEP 1: Read in global settings #
###################################
from parse_global_settings import GlobalSettings
global_settings = GlobalSettings(IOW_ESM_ROOT, input_name)

###############################################
# STEP 2: Find out the parallelization layout #
###############################################
sys.path.append(IOW_ESM_ROOT + "/scripts/prepare")
from get_parallelization_layout import get_parallelization_layout
layout = get_parallelization_layout(global_settings)

###########################################################################
# STEP 3: Find out my own thread number and which model I will be running #
###########################################################################
exec(global_settings.python_get_rank, globals()) # the expression python_get_rank is defined in global_settings.py
my_model = layout['this_model'][int(my_id)]

######################################################################################
# STEP 4: Find out start date and end date, these are given as environment variables #
######################################################################################
start_date = int(os.environ["IOW_ESM_START_DATE"])
end_date = int(os.environ["IOW_ESM_END_DATE"])
attempt = os.environ["IOW_ESM_ATTEMPT"]
local_workdir_base = os.environ["IOW_ESM_LOCAL_WORKDIR_BASE"]

# get all model handlers such that the flux calculator knows about the other models
from model_handling import get_model_handlers
model_handlers = get_model_handlers(global_settings)
# get the model handler for this process
model_handler = model_handlers[my_model]

###############################################################
# STEP 5: Create my model's work directory on the local node. #
###############################################################
firstinnode = layout['this_firstinnode'] # only create the directory if I am the first thread of this model on my node
if firstinnode[my_id]: 
    create_work_directories.create_work_directories(global_settings,          # global_settings object
                                                    local_workdir_base,    # /path/to/work/directory for all models
                                                    str(start_date),       # 'YYYYMMDD'
                                                    str(end_date),         # 'YYYYMMDD'
                                                    model_handler)         # pass the model handler for this process
                                                    

    # create an empty file "finished_creating_workdir.txt" that tells other tasks that they may start now
    f = open(local_workdir_base+'/'+my_model+'/finished_creating_workdir_'+str(start_date)+'_attempt'+attempt+'.txt','w')
    f.close()
