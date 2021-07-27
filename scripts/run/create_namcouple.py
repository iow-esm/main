# This script will call the flux_calculator with the argument --generate_namcouple.
# This call will create a namcouple file automatically from the flux_calculator.nml 
# and overwrite the namcouple in IOW_ESM_ROOT + '/input'!
# From there it will be broadcasted to the models

import os
import shutil

def create_namcouple(IOW_ESM_ROOT,        # root directory of IOW ESM
                       work_directory_root, # /path/to/work/directory for all models
                       start_date,          # 'YYYYMMDD'
                       end_date,            # 'YYYYMMDD'
                       init_date,           # 'YYYYMMDD'
                       coupling_time_step,  # in seconds
                       runname,             # string
                       debug_mode = False): # FALSE if executables compiled for production mode shall be used, 
                                            # TRUE if executables compiled for debug mode shall be used

    print('Generating namcouple via flux_calculator...')
    
    # read in global settings
    exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read(),globals())
    
    work_dir = work_directory_root+'/flux_calculator'
    
    print('  create temporary ' + work_dir)
    os.makedirs(work_dir)
    
    exec(open('create_work_directory_flux_calculator.py').read(),globals()) # read in function create_work_directory_MOM5                      
    create_work_directory_flux_calculator(IOW_ESM_ROOT,work_directory_root,'flux_calculator',str(start_date),str(end_date),str(init_date),
                                   coupling_time_step,runname,debug_mode)
    # Start flux_calculator excutable with switch --generate_namcouple before starting the model
    shellscript_name = './create_namcouple.sh'
    shellscript = open(shellscript_name, 'w')
    shellscript.writelines('#!/bin/bash\n')
    shellscript.writelines('cd '+work_directory_root+'/flux_calculator\n')
    shellscript.writelines('exec ./flux_calculator --generate_namcouple > logfile_namcouple_generation.txt 2>&1')
    shellscript.close()
    st = os.stat(shellscript_name)                 # get current permissions
    os.chmod(shellscript_name, st.st_mode | 0o777) # add a+rwx permission
    mpi_command = mpi_run_command.split(' ')[0]
    print('  create namcouple file with command: '+mpi_command, flush=True)
    # this creates namcouple in the flux_calculator work directory and copies it to the other directories
    os.system(mpi_command + " " + mpi_n_flag + " 1 " + shellscript_name)
    print('  ... creating namcouple finished ', flush=True)
    
    destfile = IOW_ESM_ROOT+'/input/namcouple'
    sourcefile = work_dir+'/namcouple'
    
    print('  copy ' + sourcefile + ' to ' + destfile, flush=True)
    if os.path.isfile(sourcefile):
        shutil.copyfile(sourcefile,destfile)   # copy the file
    else:
        print('ERROR creating namcouple file: Wanted to copy the file from '+sourcefile+
          ' but that does not exist..')
    
    print('  remove temporary ' + work_dir)
    os.system('rm -rf ' + work_dir)
    
    print('... generating namcouple via flux_calculator done.')
    return
