# This script will run the model possibly several times within a job
# Call this script from within your jobscript

from datetime import datetime, timedelta
import glob
import os
import sys
import time

import date_calculations

import create_namcouple 
import postprocess_handling

from model_handling import get_model_handlers

import hotstart_handling

from parse_global_settings import GlobalSettings

import run_helpers

try:
    input_name = str(sys.argv[1])
except:
    input_name = ""

##################################
# STEP 0: Get the root directory #
##################################

# get current folder and check if it is scripts/run
mydir = os.getcwd()
if (mydir[-12:] != '/scripts/run'):
    print('usage: python3 ./run.py ')
    print('should be called from ${IOW_ESM_ROOT}/scripts/run')
    sys.exit()

# if we started from scripts/run we know our root directory
IOW_ESM_ROOT = mydir[0:-12]

sys.path.append(IOW_ESM_ROOT + "/scripts/prepare")
from get_parallelization_layout import get_parallelization_layout

################################################################################################################################
# STEP 1: Find out which models we have, how far they have already run, and how far they will be integrated in the current job #
################################################################################################################################

# read in global settings
global_settings = GlobalSettings(IOW_ESM_ROOT, input_name)

#os.system("touch " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_started.txt")

# remove finished marker
if glob.glob(IOW_ESM_ROOT + "/" + global_settings.run_name + "_finished.txt"):
    os.system("rm " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_finished.txt")

# we seemingly want to start from scratch, so remove failed marker
if glob.glob(IOW_ESM_ROOT + "/" + global_settings.run_name + "_failed.txt"):
    os.system("rm " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_failed.txt")

# get a list of all subdirectories in "input" folder -> these are the models
model_handlers = get_model_handlers(global_settings)
models = model_handlers.keys()

print("Found the following models:")
for model in models:
    print(" " + model + ", type: " + model_handlers[model].model_type)
      
# find out what is the latest date of each model's hotstart
start_date = hotstart_handling.check_for_hotstart_folders(global_settings, models)

# memorize initial start date for the postprocessing step (see below)
initial_start_date = start_date

# write out when our job will start
print('Starting the IOW_ESM job at '+str(start_date), flush=True)

########################################################################
# STEP 2: Do several runs (with possibly several attempts) in this job #
########################################################################

for run in range(global_settings.runs_per_job):

    ########################################################################
    # STEP 2a: CALCULATE END DATE OF THIS RUN                              #
    ########################################################################
 
    # determine length and unit of run from given string (e.g. "10 days")
    run_length = global_settings.run_duration.split(' ') # e.g. '10 days' to ['10', 'days']
    run_units = run_length[1]
    run_length = int(run_length[0])
    # add this difference to the start_date
    start_datetime = datetime.strptime(str(start_date), '%Y%m%d')
    if (run_units == 'day') | (run_units == 'days'):
        end_datetime = date_calculations.add_days(start_datetime,run_length)
    elif (run_units == 'month') | (run_units == 'months'):
        end_datetime = date_calculations.add_months(start_datetime,run_length)
    elif (run_units == 'year') | (run_units == 'years'):
        end_datetime = date_calculations.add_years(start_datetime,run_length)
    end_date = int(datetime.strftime(end_datetime, '%Y%m%d'))

    # check whether we exceed the final date
    if int(global_settings.init_date) < int(global_settings.final_date):   # otherwise integrate until model crashes
        if int(end_date) > int(global_settings.final_date):
            end_date = global_settings.final_date
        if int(start_date) >= int(global_settings.final_date):
            print('IOW_ESM job finished integration to final date '+global_settings.final_date)
            os.system("touch " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_finished.txt")
            os.system("rm "+IOW_ESM_ROOT + "/" + global_settings.run_name + "_running.txt")
            sys.exit()
    
    os.system("touch " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_running.txt")
    
    ########################################################################
    # STEP 2b: ATTEMPT HANDLING: PREPARATION                               #
    ########################################################################
    
    # if we have an attempt_handler we can do the preparation here
    if global_settings.attempt_handler is not None:
        
        # get the last state of the attempt_handler from file
        global_settings.deserialize_attempt_handler()
        
        # get the next attempt 
        attempt = global_settings.attempt_handler.next_attempt
        
        # error case, we should not get here, but just in case
        if attempt is None:
            print("All attempts are exhausted. Abort.")
            print("To start from scratch, please remove " + global_settings.attempt_handler_obj_file + ".")
            os.system("rm "+IOW_ESM_ROOT + "/" + global_settings.run_name + "_running.txt")
            os.system("touch " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_failed.txt")
            sys.exit()
            
        # do the customer's preparation here
        print("Prepare attempt " + str(attempt) + "...", flush = True)
        global_settings.attempt_handler.prepare_attempt(start_date=start_date, end_date=end_date)
        print("Preparation of attempt " + str(attempt) + " done.", flush = True)
        
    # if there is no attempt handling we only have attempt "1"
    else:
        attempt = "1"
    
    print('Starting IOW_ESM run from '+str(start_date)+' to '+str(end_date)+' - attempt '+str(attempt), flush=True)


    ########################################################################
    # STEP 2c: PREPARE THE GLOBAL WORK DIRECORIES                          #
    ########################################################################

    if os.path.isdir(global_settings.global_workdir_base):
        os.system('rm -rf '+global_settings.global_workdir_base)  # if workdir exists already, delete it
    os.system('sync')
    os.makedirs(global_settings.global_workdir_base)              # create empty work directory      
    
    
    ########################################################################
    # STEP 2d: GENERATE A NAMCOUPLE FILE (IF WANTED)                       #
    ########################################################################
    
    # Check if the namcouple file should be generated automatically by the flux_calculator
    try: 
        generate_namcouple = global_settings.generate_namcouple
    except:
        generate_namcouple = False

    if generate_namcouple:
        create_namcouple.create_namcouple(global_settings, start_date, end_date)       

    ########################################################################
    # STEP 2e: PREPARE THE INDIVIDUAL WORK DIRECTORIES                     #
    ########################################################################
    
    # GET NUMBER OF CORES AND NODES
    parallelization_layout = get_parallelization_layout(global_settings)        

    # CREATE WORK DIRECTORIES AND BATCH SCRIPTS FOR EACH MODEL TO GO TO THEIR INDIVIDUAL WORK DIRECTORIES AND RUN FROM THERE
    run_helpers.write_run_scripts(global_settings, model_handlers, parallelization_layout, attempt, start_date, end_date)
    
    ########################################################################
    # STEP 2f: DO THE WORK                                                 #
    ########################################################################
        
    # WRITE mpirun APPLICATION FILE FOR THE MPMD JOB (specify how many tasks of which model are started)
    run_helpers.write_mpmd_file(global_settings, model_handlers, parallelization_layout)

    # START THE MPI JOBS
    run_helpers.start_mpi_jobs(global_settings)
    
    ########################################################################
    # STEP 2g: CHECK FOR FAILURE                                           #
    ########################################################################    
            
    run_helpers.write_run_after_scripts(global_settings, model_handlers, parallelization_layout, start_date, end_date)

    # see if files exist that indicate that the run crashed
    crashed = bool(glob.glob(global_settings.global_workdir_base+'/fail*.txt'))
    
    # if we have no attempt handling and the model crashed we can only stop the entire job
    if crashed and (global_settings.attempt_handler is None):
        print('IOW_ESM job finally failed integration from '+str(start_date)+' to '+str(end_date))
        os.system("rm "+IOW_ESM_ROOT + "/" + global_settings.run_name + "_running.txt")
        os.system("touch " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_failed.txt")
        sys.exit()
       
    try:
        resubmit_command = global_settings.resubmit_command.replace("jobscript", "jobscript_"+global_settings.input_name)
    except:
        resubmit_command = None
       
    ########################################################################
    # STEP 2h: ATTEMPT HANDLING: EVALUATION                                #
    ########################################################################  
       
    # if we have attempt handling, we have more options
    if global_settings.attempt_handler is not None:
    
        print("Model has to pass the evaluation for attempt " + str(attempt) + "...", flush = True)
        # evaluate this attempt: react to crash and/or check attempt's criterion
        attempt_failed = not global_settings.attempt_handler.evaluate_attempt(crashed, start_date=start_date, end_date=end_date)
        print("Evaluation for attempt " + str(attempt) + " done.", flush = True)
        
        # store state of attempt_handler for next run
        global_settings.serialize_attempt_handler()
            
        # the attempt has not passed the criterion, iterate to next attempt (if there is)
        if attempt_failed:
        
            print('Attempt '+str(attempt)+' failed.', flush=True)
            
            # if this was the final attempt, we stop here
            if global_settings.attempt_handler.next_attempt is None:
                print('All attempts exhausted. IOW_ESM job finally failed integration from '+str(start_date)+' to '+str(end_date))
                os.system("rm "+global_settings.attempt_handler_obj_file) # remove attempt handler state to enable restart
                os.system("rm "+IOW_ESM_ROOT + "/" + global_settings.run_name + "_running.txt")
                os.system("touch " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_failed.txt")
                sys.exit()
                
            print('Go on with next attempt.', flush=True)
            
        # something went wrong: either model has crashed or the attempt has not passed the criterion   
        if attempt_failed:
            # if the attempt failed we throw away the work and start a new job
            if resubmit_command is None:
                print('No command for resubmitting specified in global_settings.py. Abort.')
                os.system("rm "+IOW_ESM_ROOT + "/" + global_settings.run_name + "_running.txt")
                sys.exit()
            
            print('Run failed. Try again with command '+resubmit_command+'.', flush=True)
            os.system("cd " + IOW_ESM_ROOT + "/scripts/run; " + resubmit_command)
            sys.exit()
        
        # if the crashed attempt was not evaluated to false, we stop here
        if crashed:
            print('Error: Attempt '+str(attempt)+' has crashed but has been successfully evaluated. Abort.', flush=True)
            os.system("touch " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_failed.txt")
            os.system("rm "+IOW_ESM_ROOT + "/" + global_settings.run_name + "_running.txt")
            sys.exit()
                
    print('  attempt '+str(attempt)+' succeeded.', flush=True)


    ########################################################################
    # STEP 2i: MOVE OUTPUT AND RESTARTS TO THE CORRESPONDING FOLDERS       #
    ######################################################################## 

    # move files from global workdir
    for model in models: 
        model_handlers[model].move_results(global_settings.global_workdir_base, start_date, end_date)


    ########################################################################
    # STEP 2j: PROCEED TO NEXT RUN                                         #
    ######################################################################## 

    start_date = end_date
    # but wait until hotstart files are copied
    time.sleep(5.0)    


#########################################################################################
# STEP 3: JOB SUCCESSFULLY FINISHED - SUBMIT NEW JOB UNLESS FINAL DATE HAS BEEN REACHED #
#########################################################################################

if int(start_date) < int(global_settings.final_date):
    print('IOW_ESM job did not reach the final date ' +global_settings.final_date + '. Resubmit a new job.')
    if resubmit_command is None:
        print('No command for resubmitting specified in global_settings.py. Cannot go on.')
    else:
        os.system("cd " + IOW_ESM_ROOT + "/scripts/run; " + resubmit_command)
  
#########################################################################################
# STEP 4: JOB SUCCESSFULLY FINISHED - START PROCESSSING (IF WANTED)                     #
#########################################################################################                                             
postprocess_handling.postprocess_handling(global_settings, models, initial_start_date, int(datetime.strftime(end_datetime-timedelta(days=1), '%Y%m%d'))) # subtract one day to avoid overlap with other processes

# if this run has successfully finished, mark it
if int(start_date) >= int(global_settings.final_date):
    os.system("touch " + IOW_ESM_ROOT + "/" + global_settings.run_name + "_finished.txt")
    os.system("rm "+IOW_ESM_ROOT + "/" + global_settings.run_name + "_running.txt")



