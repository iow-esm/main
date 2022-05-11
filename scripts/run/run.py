# This script will run the model possibly several times within a job
# Call this script from within your jobscript

from datetime import datetime
import glob
import os
import shutil
import sys
import time

import date_calculations
import create_work_directories

import create_namcouple 
import postprocess_handling

from model_handling import get_model_handlers

import hotstart_handling

from parse_global_settings import GlobalSettings
from model_handling_flux import FluxCalculatorModes
from model_handling import ModelTypes

##################################
# STEP 0: Get the root directory #
##################################

# get current folder and check if it is scripts/run
mydir = os.getcwd()
if (mydir[-12:] != '/scripts/run'):
    print('usage: python3 ./run.py')
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
global_settings = GlobalSettings(IOW_ESM_ROOT)

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
            sys.exit()
    
    
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

    if global_settings.workdir_base[0]=='/': 
        # workdir_base gives absolute path, just use it
        work_directory_root = global_settings.workdir_base
    else:
        # workdir_base gives relative path to IOW_ESM_ROOT
        work_directory_root = IOW_ESM_ROOT+'/'+global_settings.workdir_base

    if os.path.isdir(work_directory_root):
        os.system('rm -rf '+work_directory_root)  # if workdir exists already, delete it
    os.system('sync')
    os.makedirs(work_directory_root)              # create empty work directory      
    
    
    ########################################################################
    # STEP 2d: GENERATE A NAMCOUPLE FILE (IF WANTED)                       #
    ########################################################################
    
    # Check if the namcouple file should be generated automatically by the flux_calculator
    try: 
        generate_namcouple = global_settings.generate_namcouple
    except:
        generate_namcouple = False

    if generate_namcouple:
        create_namcouple.create_namcouple(global_settings, work_directory_root, start_date, end_date)       


    ########################################################################
    # STEP 2e: PREPARE THE INDIVIDUAL WORK DIRECTORIES                     #
    ########################################################################
    
    # GET NUMBER OF CORES AND NODES
    parallelization_layout = get_parallelization_layout(IOW_ESM_ROOT)        

    # CREATE WORK DIRECTORIES AND BATCH SCRIPTS FOR EACH MODEL TO GO TO THEIR INDIVIDUAL WORK DIRECTORIES AND RUN FROM THERE
    model_threads = parallelization_layout['model_threads']
    model_executable = parallelization_layout['model_executable']
    for i,model in enumerate(models):
        file_name = 'run_'+model+'.sh'
        if os.path.islink(file_name):
            os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
        shellscript = open(file_name, 'w')
        shellscript.writelines('#!/bin/bash\n')
        if (global_settings.local_workdir_base==''):
            # workdir is global, so create the directories here
            create_work_directories.create_work_directories(global_settings,          # global_settings object
                                                work_directory_root,   # /path/to/work/directory for all models
                                                str(start_date),       # 'YYYYMMDD'
                                                str(end_date),         # 'YYYYMMDD'                                       
                                                model_handlers[model]) # create workdir for all models
            shellscript.writelines('cd '+work_directory_root+'/'+model+'\n')
        else:
            shellscript.writelines('export IOW_ESM_START_DATE='+str(start_date)+'\n')
            shellscript.writelines('export IOW_ESM_END_DATE='+str(end_date)+'\n')
            shellscript.writelines('export IOW_ESM_ATTEMPT='+str(attempt)+'\n')
            shellscript.writelines('export IOW_ESM_LOCAL_WORKDIR_BASE='+global_settings.local_workdir_base+'\n')
            shellscript.writelines('export IOW_ESM_GLOBAL_WORKDIR_BASE='+work_directory_root+'\n')
            shellscript.writelines('python3 mpi_task_before.py\n')
            shellscript.writelines('waited=0\n')                        # seconds counter for timeout
            shellscript.writelines('timeout=60\n')                      # timeout is set to 60 seconds
            shellscript.writelines('until [ -f '+global_settings.local_workdir_base+'/'+model+'/finished_creating_workdir_'+str(start_date)+'_attempt'+str(attempt)+'.txt ] || [ $waited -ge $timeout ]\n')
            shellscript.writelines('do\n')
            shellscript.writelines('     sleep 1\n')
            shellscript.writelines('     let "waited++"\n')
            shellscript.writelines('done\n')
            shellscript.writelines('if [ $waited -ge $timeout ]; then\n') # if timeout has been reached, echo the error and stop the script
            shellscript.writelines('    echo "Timeout while creating work directories for ' + model + ' has been reached. Abort."\n')
            shellscript.writelines('    exit\n')
            shellscript.writelines('fi\n')
            shellscript.writelines('cd '+global_settings.local_workdir_base+'/'+model+'\n')
        shellscript.writelines(global_settings.bash_get_rank+'\n') # e.g. "my_id=${PMI_RANK}"
        shellscript.writelines('exec ./' + model_executable[i] + ' > logfile_${my_id}.txt 2>&1')
        shellscript.close()
        st = os.stat(file_name)                 # get current permissions
        os.chmod(file_name, st.st_mode | 0o777) # add a+rwx permission
    
    
    ########################################################################
    # STEP 2f: DO THE WORK                                                 #
    ########################################################################
    if global_settings.flux_calculator_mode == FluxCalculatorModes.on_bottom_cores:
        # get a list of node names that are currently used
        node_list = global_settings.get_node_list()

        # find out which threads belong to which models
        threads_of_model = {}
        for i, model in enumerate(parallelization_layout["this_model"]):
            try:
                threads_of_model[model].append(i)
            except:
                threads_of_model[model] = [i]

        # write a machine file
        with open("machine_file", "w") as file:
            # find out which model has how many threads on which node
            for model in threads_of_model.keys():
                threads_on_node = {}
                for thread in threads_of_model[model]:
                    # get the node of this model thread from the parallelization layout
                    node = node_list[parallelization_layout["this_node"][thread]]
                    # add this thread to that node
                    try:
                        threads_on_node[node] += 1
                    except:
                        threads_on_node[node] = 1
                # write how many threads are used for this model on the corresponding nodes
                for node in threads_on_node.keys():
                    # TODO specify how to write a line of a machine(host) file in the global_settings.py
                    # TODO this is only working for Intel MPI at the moment
                    file.write(str(node)+':'+str(threads_on_node[node])+'\n')
        
    # WRITE mpirun APPLICATION FILE FOR THE MPMD JOB (specify how many tasks of which model are started)
    file_name = 'mpmd_file'
    if os.path.islink(file_name):
        os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
    mpmd_file = open(file_name, 'w')
    if global_settings.flux_calculator_mode == FluxCalculatorModes.on_bottom_cores:
        # TODO this is only working for Intel MPI at the moment
        mpmd_file.writelines("-machine machine_file\n")    
    for i,model in enumerate(models):
        mpmd_file.writelines(global_settings.mpi_n_flag+' '+str(model_threads[i])+' ./run_'+model+'.sh\n')
    mpmd_file.close() 

    # START THE MPI JOBS
    full_mpi_run_command = global_settings.mpi_run_command.replace('_CORES_',str(parallelization_layout['total_cores']))
    full_mpi_run_command = full_mpi_run_command.replace('_NODES_',str(parallelization_layout['total_nodes']))
    full_mpi_run_command = full_mpi_run_command.replace('_CORESPERNODE_',str(global_settings.cores_per_node))
    print('  starting model task with command: '+full_mpi_run_command, flush=True)
    os.system(full_mpi_run_command)
    print('  ... model task finished.', flush=True)
    
    
    ########################################################################
    # STEP 2g: CHECK FOR FAILURE                                           #
    ########################################################################    
            
    # CHECK IF THE RUN FAILED GLOBALLY
    if (global_settings.local_workdir_base==''):
        for model in models:
            if not model_handlers[model].check_for_success(work_directory_root, start_date, end_date):
                failfile = open(work_directory_root+'/failed_'+model+'.txt', 'w')
                failfile.writelines('Model '+model+' failed and did not reach the end date '+str(end_date)+'\n')
                failfile.close()
    else:
        # CHECK IF THE RUN FAILED LOCALLY AND COPY LOCAL WORKDIRS TO THE GLOBAL ONE
        file_name = 'run_after1.sh'
        if os.path.islink(file_name):
            os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
        shellscript = open(file_name, 'w')
        shellscript.writelines('export IOW_ESM_LOCAL_WORKDIR_BASE='+global_settings.local_workdir_base+'\n')
        shellscript.writelines('export IOW_ESM_GLOBAL_WORKDIR_BASE='+work_directory_root+'\n')
        shellscript.writelines('export IOW_ESM_END_DATE='+str(end_date)+'\n')
        shellscript.writelines('export IOW_ESM_START_DATE='+str(start_date)+'\n')
        shellscript.writelines('python3 mpi_task_after1.py')
        shellscript.close()
        st = os.stat(file_name)                 # get current permissions
        os.chmod(file_name, st.st_mode | 0o777) # add a+rwx permission

        mpmd_file = open('mpmd_file', 'w')
        if global_settings.flux_calculator_mode == FluxCalculatorModes.on_bottom_cores:
            # TODO this is only working for Intel MPI at the moment
            mpmd_file.writelines("-machine machine_file\n")    
        mpmd_file.writelines(global_settings.mpi_n_flag+' '+str(parallelization_layout['total_threads'])+' ./run_after1.sh\n')
        mpmd_file.close()

        full_mpi_run_command = global_settings.mpi_run_command.replace('_CORES_',str(parallelization_layout['total_cores']))
        full_mpi_run_command = full_mpi_run_command.replace('_NODES_',str(parallelization_layout['total_nodes']))
        full_mpi_run_command = full_mpi_run_command.replace('_CORESPERNODE_',str(global_settings.cores_per_node))
        print('  starting after1 task ...', flush=True)
        os.system(full_mpi_run_command)
        print('  ... after1 task finished.', flush=True)

    # see if files exist that indicate that the run crashed
    crashed = bool(glob.glob(work_directory_root+'/fail*.txt'))
    
    # if we have no attempt handling and the model crashed we can only stop the entire job
    if crashed and (global_settings.attempt_handler is None):
        print('IOW_ESM job finally failed integration from '+str(start_date)+' to '+str(end_date))
        sys.exit()
       
       
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
                sys.exit()
                
            print('Go on with next attempt.', flush=True)
            
        # something went wrong: either model has crashed or the attempt has not passed the criterion   
        if attempt_failed:
            # if the attempt failed we throw away the work and start a new job
            try:
                global_settings.resubmit_command
            except:
                print('No command for resubmitting specified in global_settings.py. Abort.')
                sys.exit()
            
            print('Run failed. Try again.', flush=True)
            os.system("cd " + IOW_ESM_ROOT + "/scripts/run; " + global_settings.resubmit_command)
            sys.exit()
        
        # if the crashed attempt was not evaluated to false, we stop here
        if crashed:
            print('Error: Attempt '+str(attempt)+' has crashed but has been successfully evaluated. Abort.', flush=True)
            sys.exit()
                
    print('  attempt '+str(attempt)+' succeeded.', flush=True)


    ########################################################################
    # STEP 2i: MOVE OUTPUT AND RESTARTS TO THE CORRESPONDING FOLDERS       #
    ######################################################################## 

    # move files from global workdir
    for model in models: 
        model_handlers[model].move_results(work_directory_root, start_date, end_date)


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
    try:
        os.system("cd " + IOW_ESM_ROOT + "/scripts/run; " + global_settings.resubmit_command)
    except:
        print('No command for resubmitting specified in global_settings.py. Abort.')
  
  
#########################################################################################
# STEP 4: JOB SUCCESSFULLY FINISHED - START PROCESSSING (IF WANTED)                     #
#########################################################################################                                             
postprocess_handling.postprocess_handling(global_settings, models, initial_start_date, end_date)



