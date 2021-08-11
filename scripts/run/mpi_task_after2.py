# This script is executed by every MPI process if the run succeeded.
# It will copy files to the output and hotstart folders

import os
import shutil

import move_results_CCLM
import move_results_MOM5
import move_results_I2LM

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

###################################
# STEP 1: Read in global settings #
###################################
exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read(),globals())

###############################################
# STEP 2: Find out the parallelization layout #
###############################################
exec(open(IOW_ESM_ROOT+'/scripts/prepare/get_parallelization_layout.py').read(),globals())
layout = get_parallelization_layout(IOW_ESM_ROOT)

#############################################################################
# STEP 3: Find out my own thread number and which model I have been running #
#############################################################################
exec(python_get_rank, globals()) # the expression python_get_rank is defined in global_settings.py
my_model = layout['this_model'][int(my_id)]

firstinnode = layout['this_firstinnode'] # only do something if I am the first thread of this model on my node
firstthread = layout['this_firstthread'] # only do something if I am the first thread of this model 
if firstinnode[my_id]:

    ##############################################################################################
    # STEP 4: Find out the local workdir and the start and end date from an environment variable #
    ##############################################################################################
    local_workdir_base = os.environ["IOW_ESM_LOCAL_WORKDIR_BASE"]
    start_date = os.environ["IOW_ESM_START_DATE"]
    end_date = os.environ["IOW_ESM_END_DATE"]    

    ######################################################################################
    # STEP 5: Find out which model I am and start the appropriate move_results_* routine #
    ######################################################################################
    if my_model[0:5]=='MOM5_':
        move_results_MOM5.move_results_MOM5(work_directory_root+'/'+model,                                #workdir
                                            IOW_ESM_ROOT+'/output/'+run_name+'/'+my_model+'/'+start_date, #outputdir
                                            IOW_ESM_ROOT+'/hotstart/'+run_name+'/'+my_model+'/'+end_date) #hotstartdir
    if my_model[0:5]=='CCLM_':
        if firstthread[my_id]:    # only the first thread will write output and hotstarts
            move_results_CCLM.move_results_CCLM(work_directory_root+'/'+model,                                #workdir
                                                IOW_ESM_ROOT+'/output/'+run_name+'/'+my_model+'/'+start_date, #outputdir
                                                IOW_ESM_ROOT+'/hotstart/'+run_name+'/'+my_model+'/'+end_date, #hotstartdir
                                                end_date)
                                                
    if my_model[0:5]=='I2LM_':
        if firstthread[my_id]:    # only the first thread will write output and hotstarts
            move_results_I2LM.move_results_I2LM(work_directory_root+'/'+model,                                #workdir
                                                IOW_ESM_ROOT+'/output/'+run_name+'/'+my_model+'/'+start_date, #outputdir
                                                IOW_ESM_ROOT+'/hotstart/'+run_name+'/'+my_model+'/'+end_date, #hotstartdir
                                                str(start_date))
    os.system('sync')
