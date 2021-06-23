# This script will fill the required files into the work directory for a MOM5 model.
# The function is called from create_work_directories.py 

from datetime import datetime
import os
import shutil

import change_in_namelist

def create_work_directory_flux_calculator(IOW_ESM_ROOT,        # root directory of IOW ESM
                               work_directory_root, # /path/to/work/directory for all models
                               my_directory,        # name of this model instance
                               start_date,          # 'YYYYMMDD'
                               end_date,            # 'YYYYMMDD'
                               init_date,           # 'YYYYMMDD'
                               coupling_time_step,  # in seconds
                               runname,             # string
                               debug_mode = False): # FALSE if executables compiled for production mode shall be used, 
                                                    # TRUE if executables compiled for debug mode shall be used

    # STEP 1: CHECK IF EXECUTABLE ALREADY EXISTS, IF NOT COPY IT
    full_directory = work_directory_root+'/'+my_directory
    destfile = full_directory+'/flux_calculator'
    if not os.path.isfile(destfile):
        # no executable, need to copy
        if debug_mode:
            sourcefile = IOW_ESM_ROOT+'/components/flux_calculator/bin/flux_calculator' # we may change this in future
        else:
            sourcefile = IOW_ESM_ROOT+'/components/flux_calculator/bin/flux_calculator'
        # check if file exists
        if os.path.isfile(sourcefile):
            shutil.copyfile(sourcefile,destfile)   # copy the file
        else:
            print('ERROR creating work directory '+full_directory+': Wanted to copy the executable from '+sourcefile+
                  ' but that does not exist. You may have to build it.')
    st = os.stat(destfile)                 # get current permissions
    os.chmod(destfile, st.st_mode | 0o777) # add a+rwx permission

    # STEP 2: Read global options file
    exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read())

    # STEP 3: calculate number of timesteps
    my_startdate = datetime.strptime(start_date,'%Y%m%d')
    my_enddate = datetime.strptime(end_date,'%Y%m%d')
    my_initdate = datetime.strptime(init_date,'%Y%m%d')

    rundays = (my_enddate - my_startdate).days
    runseconds = int(rundays)*24*3600
    timesteps = runseconds//coupling_time_step

    # STEP 4: copy flux_calculator.nml file and change timestep and number of time steps
    os.system('cp '+IOW_ESM_ROOT+'/input/flux_calculator.nml '+full_directory+'/flux_calculator.nml')

    # STEP 5: Create an empty folder named "mappings" and place exchange grid files and mapping files there
    os.makedirs(full_directory+'/mappings') 
    os.system('cp '+IOW_ESM_ROOT+'/input/CCLM*/mappings/?_grid_exchangegrid.nc '+full_directory+'/mappings')
    os.system('cp '+IOW_ESM_ROOT+'/input/*/mappings/remap_*.nc '+full_directory+'/mappings')
    os.system('cp '+IOW_ESM_ROOT+'/input/CCLM*/mappings/regrid_*.nc '+full_directory+'/mappings')

    return
