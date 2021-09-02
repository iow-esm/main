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

import move_results_CCLM
import move_results_MOM5
import move_results_I2LM

import create_namcouple 

# get current folder and check if it is scripts/run
mydir = os.getcwd()
fail = False
if (mydir[-12:] != '/scripts/run'):
    fail = True
else:
    IOW_ESM_ROOT = mydir[0:-12]

if (fail):
    print('usage: python3 ./run.py')
    print('should be called from ${IOW_ESM_ROOT}/scripts/run')
    sys.exit()

################################################################################################################################
# STEP 1: Find out which models we have, how far they have already run, and how far they will be integrated in the current job #
################################################################################################################################

# read in global settings
exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read(),globals())

# get a list of all subdirectories in "input" folder -> these are the models
models = [d for d in os.listdir(IOW_ESM_ROOT+'/input/') if os.path.isdir(os.path.join(IOW_ESM_ROOT+'/input/',d))]

# find out what is the latest date of each model's hotstart
last_complete_hotstart_date = -1000
for model in models:
    my_hotstart_dir = IOW_ESM_ROOT+'/hotstart/'+run_name+'/'+model
    # if hotstart dir does not exist yet, create it
    if (not os.path.isdir(my_hotstart_dir)):
        os.makedirs(my_hotstart_dir)
    # list folders in this directory
    my_hotstart_dates = [d for d in os.listdir(my_hotstart_dir) if os.path.isdir(os.path.join(my_hotstart_dir,d))]
    separator=','
    print('my_hotstart_dates for '+model+':'+separator.join(my_hotstart_dates))
    my_hotstart_dates = [int(i) for i in my_hotstart_dates] # integer in format YYYYMMDD
    # see if there are any hotstarts at all for this model
    if my_hotstart_dates:
        new_hotstart_date = max(my_hotstart_dates)  # get the latest one
        if (last_complete_hotstart_date < -1):
            last_complete_hotstart_date = new_hotstart_date
        if new_hotstart_date < last_complete_hotstart_date:
            last_complete_hotstart_date = new_hotstart_date
    else:
        last_complete_hotstart_date = -1      # at least one model has no hotstart at all

# delete all those output and hotstart files after the last common (=successful) hotstart
for model in models:
    my_hotstart_dir = IOW_ESM_ROOT+'/hotstart/'+run_name+'/'+model
    my_hotstart_dates = [d for d in os.listdir(my_hotstart_dir) if os.path.isdir(os.path.join(my_hotstart_dir,d))]
    my_hotstart_dates = [int(i) for i in my_hotstart_dates]
    for my_hotstart_date in my_hotstart_dates:
        if my_hotstart_date > last_complete_hotstart_date:
            os.system('rm -rf '+my_hotstart_dir+'/'+str(my_hotstart_date))

# if there is no hotstart, use the initial date as starting date
if last_complete_hotstart_date < 0:
    start_date = int(init_date)
else:
    start_date = last_complete_hotstart_date

# write out when our job will start
print('Starting the IOW_ESM job at '+str(start_date), flush=True)

########################################################################
# STEP 2: Do several runs (with possibly several attempts) in this job #
########################################################################

for run in range(runs_per_job):
    # CALCULATE END DATE OF THIS RUN
    # determine length and unit of run from given string (e.g. "10 days")
    run_length = run_duration.split(' ') # e.g. '10 days' to ['10', 'days']
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
    if int(init_date) < int(final_date):   # otherwise integrate until model crashes
        if int(end_date) > int(final_date):
            end_date = final_date
        if int(start_date) >= int(final_date):
            print('IOW_ESM job finished integration to final date '+final_date)
            sys.exit()
  
    # DO SEVERAL ATTEMPTS IN CASE INTEGRATION FAILS
    for attempt in range(max_attempts):
        print('Starting IOW_ESM run from '+str(start_date)+' to '+str(end_date)+' - attempt '+str(attempt+1), flush=True)

        # PREPARE THE WORK DIRECORIES IF THEY ARE GLOBAL
        if workdir_base[0]=='/': 
            # workdir_base gives absolute path, just use it
            work_directory_root = workdir_base
        else:
            # workdir_base gives relative path to IOW_ESM_ROOT
            work_directory_root = IOW_ESM_ROOT+'/'+workdir_base

        if os.path.isdir(work_directory_root):
            os.system('rm -rf '+work_directory_root)  # if workdir exists already, delete it
        os.system('sync')
        os.makedirs(work_directory_root)              # create empty work directory      
        
                # Check if the namcouple file should be generated automatically by the flux_calculator
        try: 
            namcouple = generate_namcouple
        except:
            namcouple = False

        if namcouple:
            create_namcouple.create_namcouple(IOW_ESM_ROOT, work_directory_root, start_date, end_date, init_date, coupling_time_step, run_name, debug_mode)

        if local_workdir_base=='':  # workdir is global, so create the directories here
            create_work_directories.create_work_directories(IOW_ESM_ROOT,          # root directory of IOW ESM
                                                            work_directory_root,   # /path/to/work/directory for all models
                                                            link_files_to_workdir, # True if links are sufficient or False if files shall be copied
                                                            str(start_date),       # 'YYYYMMDD'
                                                            str(end_date),         # 'YYYYMMDD'
                                                            debug_mode,            # False if executables compiled for production mode shall be used, 
                                                                                   # True if executables compiled for debug mode shall be used
                                                            '')                    # create workdir for all models

        # GET NUMBER OF CORES AND NODES
        exec(open(IOW_ESM_ROOT+'/scripts/prepare/get_parallelization_layout.py').read(),globals())
        parallelization_layout = get_parallelization_layout(IOW_ESM_ROOT)        

        # CREATE BATCH SCRIPTS FOR EACH MODEL TO GO TO THEIR INDIVIDUAL WORK DIRECTORIES AND RUN FROM THERE
        models = parallelization_layout['models']
        model_threads = parallelization_layout['model_threads']
        model_executable = parallelization_layout['model_executable']
        for i,model in enumerate(models):
            file_name = 'run_'+model+'.sh'
            if os.path.islink(file_name):
                os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
            shellscript = open(file_name, 'w')
            shellscript.writelines('#!/bin/bash\n')
            if (local_workdir_base==''):
                shellscript.writelines('cd '+work_directory_root+'/'+model+'\n')
            else:
                shellscript.writelines('export IOW_ESM_START_DATE='+str(start_date)+'\n')
                shellscript.writelines('export IOW_ESM_END_DATE='+str(end_date)+'\n')
                shellscript.writelines('export IOW_ESM_ATTEMPT='+str(attempt+1)+'\n')
                shellscript.writelines('export IOW_ESM_LOCAL_WORKDIR_BASE='+local_workdir_base+'\n')
                shellscript.writelines('export IOW_ESM_GLOBAL_WORKDIR_BASE='+work_directory_root+'\n')
                shellscript.writelines('python3 mpi_task_before.py\n')
                shellscript.writelines('until [ -f '+local_workdir_base+'/'+model+'/finished_creating_workdir_'+str(start_date)+'_attempt'+str(attempt+1)+'.txt ]\n')
                shellscript.writelines('do\n')
                shellscript.writelines('     sleep 1\n')
                shellscript.writelines('done\n')
                shellscript.writelines('cd '+local_workdir_base+'/'+model+'\n')
            shellscript.writelines(bash_get_rank+'\n') # e.g. "my_id=${PMI_RANK}"
            shellscript.writelines('exec ./' + model_executable[i] + ' > logfile_${my_id}.txt 2>&1')
            shellscript.close()
            st = os.stat(file_name)                 # get current permissions
            os.chmod(file_name, st.st_mode | 0o777) # add a+rwx permission
        
        # WRITE mpirun APPLICATION FILE FOR THE MPMD JOB (specify how many tasks of which model are started)
        file_name = 'mpmd_file'
        if os.path.islink(file_name):
            os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
        mpmd_file = open(file_name, 'w')
        for i,model in enumerate(models):
            mpmd_file.writelines(mpi_n_flag+' '+str(model_threads[i])+' ./run_'+model+'.sh\n')
        mpmd_file.close() 

        # START THE MPI JOBS
        full_mpi_run_command = mpi_run_command.replace('_CORES_',str(parallelization_layout['total_cores']))
        full_mpi_run_command = full_mpi_run_command.replace('_NODES_',str(parallelization_layout['total_nodes']))
        full_mpi_run_command = full_mpi_run_command.replace('_CORESPERNODE_',str(cores_per_node))
        print('  starting model task with command: '+full_mpi_run_command, flush=True)
        os.system(full_mpi_run_command)
        print('  ... model task finished.', flush=True)

        # DO THE LOCAL POSTPROCESSING STEP 1: POSSIBLY COPY LOCAL WORKDIRS TO THE GLOBAL ONE AND CHECK WHETHER THE JOB FAILED
        # CHECK IF THE RUN FAILED
        def files_exist(filepath):
            for filepath_object in glob.glob(filepath):
                if os.path.isfile(filepath_object):
                    return True
            return False

        if (local_workdir_base==''):
            for i,model in enumerate(models):
                if model[0:5]=='MOM5_':
                    hotstartfile = work_directory_root+'/'+model+'/RESTART/*'
                    if not files_exist(hotstartfile):
                        print('run failed because no file exists:'+hotstartfile)
                        failfile = open(work_directory_root+'/failed_'+model+'.txt', 'w')
                        failfile.writelines('Model '+model+' failed and did not reach the end date '+str(end_date)+'\n')
                        failfile.close()
                if model[0:5]=='CCLM_':
                    hotstartfile = work_directory_root+'/'+model+'/lrfd'+str(end_date)+'00o'
                    if not files_exist(hotstartfile):  # this does not exist -> run failed
                        print('run failed because no file exists:'+hotstartfile)
                        failfile = open(work_directory_root+'/failed_'+model+'.txt', 'w')
                        failfile.writelines('Model '+model+' failed and did not reach the end date '+str(end_date)+'\n')
                        failfile.close()
                if model[0:5]=='I2LM_':
                    lastfile = work_directory_root+'/'+model+'/'+str(start_date)+'/lbfd'+str(end_date)+'00.nc'
                    if not files_exist(lastfile):  # this does not exist -> run failed
                        print('run failed because no file exists:'+lastfile)
                        failfile = open(work_directory_root+'/failed_'+model+'.txt', 'w')
                        failfile.writelines('Model '+model+' failed and did not reach the end date '+str(end_date)+'\n')
                        failfile.close()

        else:
            # DO THE LOCAL POSTPROCESSING STEP 1: POSSIBLY COPY LOCAL WORKDIRS TO THE GLOBAL ONE AND CHECK WHETHER THE JOB FAILED
            file_name = 'run_after1.sh'
            if os.path.islink(file_name):
                os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
            shellscript = open(file_name, 'w')
            shellscript.writelines('export IOW_ESM_LOCAL_WORKDIR_BASE='+local_workdir_base+'\n')
            shellscript.writelines('export IOW_ESM_GLOBAL_WORKDIR_BASE='+work_directory_root+'\n')
            shellscript.writelines('export IOW_ESM_END_DATE='+str(end_date)+'\n')
            shellscript.writelines('export IOW_ESM_START_DATE='+str(start_date)+'\n')
            shellscript.writelines('python3 mpi_task_after1.py')
            shellscript.close()
            st = os.stat(file_name)                 # get current permissions
            os.chmod(file_name, st.st_mode | 0o777) # add a+rwx permission

            mpmd_file = open('mpmd_file', 'w')
            mpmd_file.writelines(mpi_n_flag+' '+str(parallelization_layout['total_threads'])+' ./run_after1.sh\n')
            mpmd_file.close()

            full_mpi_run_command = mpi_run_command.replace('_CORES_',str(parallelization_layout['total_cores']))
            full_mpi_run_command = full_mpi_run_command.replace('_NODES_',str(parallelization_layout['total_nodes']))
            full_mpi_run_command = full_mpi_run_command.replace('_CORESPERNODE_',str(cores_per_node))
            print('  starting after1 task ...', flush=True)
            os.system(full_mpi_run_command)
            print('  ... after1 task finished.', flush=True)
 
        # see if files exist that indicate that the run failed
        run_failed = files_exist(work_directory_root+'/fail*.txt')

        # if it finally failed, stop the entire job
        if run_failed & (attempt+1 == max_attempts):
            print('IOW_ESM job finally failed integration from '+str(start_date)+' to '+str(end_date))
            sys.exit()

        # if we succeeded, continue outside the attempt loop
        if not run_failed:
            print('  attempt '+str(attempt+1)+' succeeded.', flush=True)
            break
        print('  attempt '+str(attempt+1)+' failed.', flush=True)

    # MOVE OUTPUT AND RESTARTS TO THE CORRESPONDING FOLDERS
    if ((local_workdir_base!='') & (copy_to_global_workdir==False)): # move files directly from local workdirs
        file_name = 'run_after2.sh'
        if os.path.islink(file_name):
            os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
        shellscript = open(file_name, 'w')
        shellscript.writelines('export IOW_ESM_LOCAL_WORKDIR_BASE='+local_workdir_base+'\n')
        shellscript.writelines('export IOW_ESM_START_DATE='+str(start_date)+'\n')
        shellscript.writelines('export IOW_ESM_END_DATE='+str(end_date)+'\n')
        shellscript.writelines('python3 mpi_task_after2.py')
        shellscript.close()
        st = os.stat(file_name)                 # get current permissions
        os.chmod(file_name, st.st_mode | 0o777) # add a+rwx permission

        mpmd_file = open('mpmd_file', 'w')
        mpmd_file.writelines(mpi_n_flag+' '+str(parallelization_layout['total_threads'])+' ./run_after2.sh\n')
        mpmd_file.close()

        full_mpi_run_command = mpi_run_command.replace('_CORES_',str(parallelization_layout['total_cores']))
        full_mpi_run_command = full_mpi_run_command.replace('_NODES_',str(parallelization_layout['total_nodes']))
        full_mpi_run_command = full_mpi_run_command.replace('_CORESPERNODE_',str(cores_per_node))
        os.system(full_mpi_run_command)    
    else: # move files from global workdir
        for i,model in enumerate(models): 
            if model[0:5]=='CCLM_':
                move_results_CCLM.move_results_CCLM(work_directory_root+'/'+model,                             #workdir
                                                    IOW_ESM_ROOT+'/output/'+run_name+'/'+model+'/'+str(start_date), #outputdir
                                                    IOW_ESM_ROOT+'/hotstart/'+run_name+'/'+model+'/'+str(end_date), #hotstartdir
                                                    str(end_date))
            if model[0:5]=='MOM5_':
                move_results_MOM5.move_results_MOM5(work_directory_root+'/'+model,                             #workdir
                                                    IOW_ESM_ROOT+'/output/'+run_name+'/'+model+'/'+str(start_date), #outputdir
                                                    IOW_ESM_ROOT+'/hotstart/'+run_name+'/'+model+'/'+str(end_date)) #hotstartdir
                                                    
            if model[0:5]=='I2LM_':
                move_results_I2LM.move_results_I2LM(work_directory_root+'/'+model,                             #workdir
                                                    IOW_ESM_ROOT+'/output/'+run_name+'/'+model, #outputdir
                                                    IOW_ESM_ROOT+'/hotstart/'+run_name+'/'+model+'/'+str(end_date), #hotstartdir
                                                    str(start_date))
        
    # PROCEED TO NEXT RUN
    start_date = end_date
    # but wait until hotstart files are copied
    time.sleep(5.0)    

#########################################################################################
# STEP 3: JOB SUCCESSFULLY FINISHED - SUBMIT NEW JOB UNLESS FINAL DATE HAS BEEN REACHED #
#########################################################################################

