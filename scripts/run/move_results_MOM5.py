# This script will fill the required files into the work directory for a CCLM model.
# The function is called from create_work_directories.py 

import os
import shutil

def move_results_MOM5(workdir,        # work directory of this model instance
                      outputdir,      # directory for output
                      hotstartdir):   # directory for hotstarts

    # STEP 1: CREATE DIRECTORIES IF REQUIRED
    if (not os.path.isdir(outputdir)): 
        os.makedirs(outputdir)
    if (not os.path.isdir(outputdir+'/out_raw')):
        os.makedirs(outputdir+'/out_raw')
    if (not os.path.isdir(hotstartdir)):
        os.makedirs(hotstartdir)

    # STEP 2: MOVE OUTPUT
    os.system('mv '+workdir+'/*.nc.???? '+outputdir+'/out_raw/.')
    
    if os.path.isfile(workdir + '/RUN_INFO'):
        os.system('mv '+workdir+'/RUN_INFO '+outputdir+'/.')

    # STEP 3: MOVE HOTSTART
    os.system('mv '+workdir+'/RESTART/* '+hotstartdir+'/.')  # MOM hotstart files
    os.system('mv '+workdir+'/restart* '+hotstartdir+'/.')  # OASIS hotstart file
