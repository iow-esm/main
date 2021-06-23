# This script is executed by every MPI process.
# It will find out by the PE number which compartment model of the Earth System Model it shall run.

import os
import time

import create_work_directories

# get current folder and check if it is scripts/run
mydir = os.getcwd()
fail = False
if (mydir[-12:] != '/scripts/run'):
    fail = True
else:
    IOW_ESM_ROOT = mydir[0:-12]

if (fail):
    print('ERROR: mpi_task.py was started from outside the folder ${IOW_ESM_ROOT}/scripts/run')
    sys.exit()

# wait five seconds for file system
time.sleep(5.0)

###################################
# STEP 1: Read in global settings #
###################################
exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read(),globals())

###############################################
# STEP 2: Find out the parallelization layout #
###############################################
exec(open(IOW_ESM_ROOT+'/scripts/prepare/get_parallelization_layout.py').read(),globals())
layout = get_parallelization_layout(IOW_ESM_ROOT)

###########################################################################
# STEP 3: Find out my own thread number and which model I will be running #
###########################################################################
exec(python_get_rank, globals()) # the expression python_get_rank is defined in global_settings.py
my_model = layout['this_model'][int(my_id)]

######################################################################################
# STEP 4: Find out start date and end date, these are given as environment variables #
######################################################################################
start_date = int(os.environ["IOW_ESM_START_DATE"])
end_date = int(os.environ["IOW_ESM_END_DATE"])
attempt = os.environ["IOW_ESM_ATTEMPT"]
local_workdir_base = os.environ["IOW_ESM_LOCAL_WORKDIR_BASE"]
global_workdir_base = os.environ["IOW_ESM_GLOBAL_WORKDIR_BASE"]

###############################################################
# STEP 5: Create my model's work directory on the local node. #
###############################################################
firstinnode = layout['this_firstinnode'] # only create the directory if I am the first thread of this model on my node
if firstinnode[my_id]:
    create_work_directories.create_work_directories(IOW_ESM_ROOT,          # root directory of IOW ESM
                                                    local_workdir_base,    # /path/to/work/directory for all models
                                                    link_files_to_workdir, # True if links are sufficient or False if files shall be copied
                                                    str(start_date),       # 'YYYYMMDD'
                                                    str(end_date),         # 'YYYYMMDD'
                                                    debug_mode,            # False if executables compiled for production mode shall be used, 
                                                                           # True if executables compiled for debug mode shall be used
                                                    my_model,              # create workdir for my model only
                                                    global_workdir_base)   # we need the global path also because we put some files there

    # create an empty file "finished_creating_workdir.txt" that tells other tasks that they may start now
    f = open(local_workdir_base+'/'+my_model+'/finished_creating_workdir_'+str(start_date)+'_attempt'+attempt+'.txt','w')
    f.close()
