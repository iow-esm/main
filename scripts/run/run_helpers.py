import os

from model_handling_flux import FluxCalculatorModes
import create_work_directories

def write_machinefile(global_settings, parallelization_layout):
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
    file_name = "machine_file_"+global_settings.input_name

    with open(file_name, "w") as file:
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
                file.write(global_settings.machinefile_line(node, threads_on_node[node])+'\n')

def write_mpmd_file(global_settings, model_handlers, parallelization_layout):

    if global_settings.flux_calculator_mode == FluxCalculatorModes.on_bottom_cores:
        write_machinefile(global_settings, parallelization_layout)
    
    models = model_handlers.keys()
    model_threads = parallelization_layout['model_threads']

    # WRITE mpirun APPLICATION FILE FOR THE MPMD JOB (specify how many tasks of which model are started)
    file_name = 'mpmd_file_'+global_settings.input_name
    if os.path.islink(file_name):
        os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
    mpmd_file = open(file_name, 'w') 

    for i,model in enumerate(models):
        mpmd_file.writelines(global_settings.mpi_n_flag+' '+str(model_threads[i])+' ./run_'+model+'_'+global_settings.input_name+'.sh\n')
    mpmd_file.close() 

def write_run_scripts(global_settings, model_handlers, parallelization_layout, attempt, start_date, end_date):

    models = model_handlers.keys()
    model_executable = parallelization_layout['model_executable']

    for i,model in enumerate(models):
        file_name = 'run_'+model+'_'+global_settings.input_name+'.sh'
        if os.path.islink(file_name):
            os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
        shellscript = open(file_name, 'w')
        shellscript.writelines('#!/bin/bash\n')
        if (global_settings.local_workdir_base==''):
            # workdir is global, so create the directories here
            create_work_directories.create_work_directories(global_settings,          # global_settings object
                                                str(start_date),       # 'YYYYMMDD'
                                                str(end_date),         # 'YYYYMMDD'                                       
                                                model_handlers[model]) # create workdir for all models
            shellscript.writelines('cd '+global_settings.global_workdir_base+'/'+model+'\n')
        else:
            shellscript.writelines('export IOW_ESM_START_DATE='+str(start_date)+'\n')
            shellscript.writelines('export IOW_ESM_END_DATE='+str(end_date)+'\n')
            shellscript.writelines('export IOW_ESM_ATTEMPT='+str(attempt)+'\n')
            shellscript.writelines('export IOW_ESM_LOCAL_WORKDIR_BASE='+global_settings.local_workdir_base+ '/' +'\n')
            shellscript.writelines('export IOW_ESM_GLOBAL_WORKDIR_BASE='+global_settings.global_workdir_base+'\n')
            shellscript.writelines('python3 mpi_task_before.py ' + global_settings.input_name + '\n')
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
        #shellscript.writelines('module load vtune; exec vtune -collect hotspots -result-dir='+work_directory_root+'/'+model+' ./' + model_executable[i] + ' > logfile_${my_id}.txt 2>&1')
        shellscript.writelines('exec ./' + model_executable[i] + ' > logfile_${my_id}.txt 2>&1')
        shellscript.close()
        st = os.stat(file_name)                 # get current permissions
        os.chmod(file_name, st.st_mode | 0o777) # add a+rwx permission

def start_mpi_jobs(global_settings):
    mpmd_file_name = 'mpmd_file_'+global_settings.input_name
    machine_file_name = "machine_file_"+global_settings.input_name
    full_mpi_run_command = global_settings.mpi_run_command.replace("mpmd_file", mpmd_file_name)
    if global_settings.flux_calculator_mode == FluxCalculatorModes.on_bottom_cores:
        full_mpi_run_command += ' '+global_settings.use_mpi_machinefile.replace("machine_file", machine_file_name)

    print('  starting model task with command: '+full_mpi_run_command, flush=True)
    os.system(full_mpi_run_command)
    print('  ... model task finished.', flush=True)


def write_run_after_scripts(global_settings, model_handlers, parallelization_layout, start_date, end_date):

    models = model_handlers.keys()
    # CHECK IF THE RUN FAILED GLOBALLY
    if (global_settings.local_workdir_base==''):
        for model in models:
            if not model_handlers[model].check_for_success(global_settings.global_workdir_base, start_date, end_date):
                failfile = open(global_settings.global_workdir_base+'/failed_'+model+'.txt', 'w')
                failfile.writelines('Model '+model+' failed and did not reach the end date '+str(end_date)+'\n')
                failfile.close()
    else:
        # CHECK IF THE RUN FAILED LOCALLY AND COPY LOCAL WORKDIRS TO THE GLOBAL ONE
        file_name = 'run_after1_'+global_settings.input_name+'.sh'
        if os.path.islink(file_name):
            os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
        shellscript = open(file_name, 'w')
        shellscript.writelines('export IOW_ESM_LOCAL_WORKDIR_BASE='+global_settings.local_workdir_base + '\n')
        shellscript.writelines('export IOW_ESM_GLOBAL_WORKDIR_BASE='+global_settings.global_workdir_base+'\n')
        shellscript.writelines('export IOW_ESM_END_DATE='+str(end_date)+'\n')
        shellscript.writelines('export IOW_ESM_START_DATE='+str(start_date)+'\n')
        shellscript.writelines('python3 mpi_task_after1.py ' + global_settings.input_name + '\n')
        shellscript.close()
        st = os.stat(file_name)                 # get current permissions
        os.chmod(file_name, st.st_mode | 0o777) # add a+rwx permission

        mpmd_file_name = 'mpmd_file_'+global_settings.input_name
        mpmd_file = open(mpmd_file_name, 'w') 
        mpmd_file.writelines(global_settings.mpi_n_flag+' '+str(parallelization_layout['total_threads'])+' ./'+file_name+'\n')
        mpmd_file.close()

        full_mpi_run_command = global_settings.mpi_run_command.replace("mpmd_file", mpmd_file_name)

        machine_file_name = "machine_file_"+global_settings.input_name
        if global_settings.flux_calculator_mode == FluxCalculatorModes.on_bottom_cores:
            full_mpi_run_command += ' '+global_settings.use_mpi_machinefile.replace("machine_file", machine_file_name)
        print('  starting after1 task ...', flush=True)
        os.system(full_mpi_run_command)
        print('  ... after1 task finished.', flush=True)