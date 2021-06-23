# This script is executed by every MPI process.
# It checks if the model succeeded. Otherwise it writes a "failed_<modelname>.txt" marker file to the work directory.

import glob
import os
import shutil
import time

# wait five seconds to allow for write procedures to finish
time.sleep(5.0)

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

    ###############################################################################################
    # STEP 4: Find out the global and local workdir and the end date from an environment variable #
    ###############################################################################################
    local_workdir_base = os.environ["IOW_ESM_LOCAL_WORKDIR_BASE"]
    global_workdir_base = os.environ["IOW_ESM_GLOBAL_WORKDIR_BASE"]
    end_date = os.environ["IOW_ESM_END_DATE"]    

    ############################################
    # STEP 5: Check if the model run succeeded #
    ############################################
    # Define a function to see whether a file matching a certain pattern exists
    def files_exist(filepath):
        for filepath_object in glob.glob(filepath):
            if os.path.isfile(filepath_object):
                return True
        return False

    if my_model[0:5]=='MOM5_':
        if firstthread[my_id]:    # only the first thread must write a hotstart file
            hotstartfile = local_workdir_base+'/'+my_model+'/RESTART/*'
            if not files_exist(hotstartfile):  
                print('run failed because no file exists:'+hotstartfile)
                failfile = open(global_workdir_base+'/failed_'+my_model+'.txt', 'w')
                failfile.writelines('Model '+my_model+' failed and did not reach the end date '+end_date+'\n')
                failfile.close()
    if my_model[0:5]=='CCLM_':
        if firstthread[my_id]:    # only the first thread must write a hotstart file
            hotstartfile = local_workdir_base+'/'+my_model+'/lrfd'+end_date+'00o'
            if not files_exist(hotstartfile):  # this does not exist -> run failed
                print('run failed because no file exists:'+hotstartfile)
                failfile = open(global_workdir_base+'/failed_'+my_model+'.txt', 'w')
                failfile.writelines('Model '+my_model+' failed and did not reach the end date '+end_date+'\n')
                failfile.close()

    ##########################################################################
    # STEP 6: If required, copy the work directory to the global file system #
    ##########################################################################
    if copy_to_global_workdir:
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