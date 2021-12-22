# This script will fill the required files into the work directory for a CCLM model.
# The function is called from create_work_directories.py 

import os
import shutil

def move_results_CCLM(workdir,        # work directory of this model instance
                      outputdir,      # directory for output
                      hotstartdir,    # directory for hotstarts
                      end_date):      # 'YYYYMMDD'

    # STEP 1: CREATE DIRECTORIES IF REQUIRED
    if (not os.path.isdir(outputdir)): 
        os.makedirs(outputdir)
    if (not os.path.isdir(hotstartdir)):
        os.makedirs(hotstartdir)

    # STEP 2: MOVE OUTPUT
    os.system('mv '+workdir+'/out* '+outputdir+'/.')
    
    os.system('mv '+workdir+'/AS*.nc '+outputdir+'/.')
    os.system('mv '+workdir+'/AR*.nc '+outputdir+'/.')
    
    if os.path.isfile(workdir + '/RUN_INFO'):
        os.system('mv '+workdir+'/RUN_INFO '+outputdir+'/.')

    # STEP 3: MOVE HOTSTART
    hotstartfile = workdir+'/lrfd'+end_date+'00o'           # CCLM hotstart file
    os.system('mv '+hotstartfile+' '+hotstartdir+'/.')
    os.system('mv '+workdir+'/restart* '+hotstartdir+'/.')  # OASIS hotstart file
