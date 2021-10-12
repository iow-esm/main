# This script will fill the required files into the work directory for a CCLM model.
# The function is called from create_work_directories.py 

import os
import shutil

def move_results_I2LM(workdir,        # work directory of this model instance
                      outputdir,      # directory for output
                      hotstartdir,    # directory for hotstarts
                      start_date):
                      
    # STEP 1: CREATE DIRECTORIES IF REQUIRED
    if (not os.path.isdir(outputdir)): 
        os.makedirs(outputdir)
    if (not os.path.isdir(hotstartdir)):
        os.makedirs(hotstartdir)

    # STEP 2: MOVE OUTPUT
    os.system('mv '+workdir+'/'+start_date+' '+outputdir+'/.')
    
    if os.path.isfile(workdir + '/RUN_INFO'):
        os.system('mv '+workdir+'/RUN_INFO '+outputdir+'/.')

    # STEP 3: MOVE HOTSTART
    # there is no real hotstart file, the existence of the hotstart folder marks where we stopped