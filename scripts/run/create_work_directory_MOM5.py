# This script will fill the required files into the work directory for a MOM5 model.
# The function is called from create_work_directories.py 

from datetime import datetime
import os
import shutil

import change_in_namelist
import get_run_information

def create_work_directory_MOM5(IOW_ESM_ROOT,        # root directory of IOW ESM
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
    destfile = full_directory+'/fms_MOM_SIS.x'
    if not os.path.isfile(destfile):
        # no executable, need to copy
        if debug_mode:
            sourcefile = IOW_ESM_ROOT+'/components/MOM5/exec/IOW_ESM_DEBUG/MOM_SIS/fms_MOM_SIS.x'
        else:
            sourcefile = IOW_ESM_ROOT+'/components/MOM5/exec/IOW_ESM_PRODUCTION/MOM_SIS/fms_MOM_SIS.x'
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

    # STEP 3: Adjust times in input.nml
    my_startdate = datetime.strptime(start_date,'%Y%m%d')
    my_enddate = datetime.strptime(end_date,'%Y%m%d')
    my_initdate = datetime.strptime(init_date,'%Y%m%d')

    rundays = (my_enddate - my_startdate).days

    change_in_namelist.change_in_namelist(filename=full_directory+'/input.nml',
                     after='&coupler_nml', before='/', start_of_line='days',
                     new_value = '='+str(rundays))
    change_in_namelist.change_in_namelist(filename=full_directory+'/input.nml',
                     after='&coupler_nml', before='/', start_of_line='current_date',
                     new_value = '='+datetime.strftime(my_initdate,'%Y,%m,%d,0,0,0'))
    change_in_namelist.change_in_namelist(filename=full_directory+'/input.nml',
                     after='&coupler_nml', before='/', start_of_line='dt_cpld',
                     new_value = '='+str(coupling_time_step))
    change_in_namelist.change_in_namelist(filename=full_directory+'/input.nml',
                     after='&coupler_nml', before='/', start_of_line='dt_atmos',
                     new_value = '='+str(coupling_time_step))
    change_in_namelist.change_in_namelist(filename=full_directory+'/diag_table',
                     after='', before='EOF', start_of_line='*AUTO*',
                     new_value = datetime.strftime(my_initdate,"%Y %m %d 0 0 0"), 
                     completely_replace_line=True)

    # STEP 4: Create an empty folder named "RESTART"
    os.makedirs(full_directory+'/RESTART') 

    # STEP 5: Copy hotstart files if a corresponding folder exists
    if (start_date != init_date):
        hotstart_folder = IOW_ESM_ROOT + '/hotstart/' + runname + '/' + my_directory + '/' + start_date
        os.system('cp '+hotstart_folder+'/*.res.nc '+full_directory+'/INPUT/')    # copy MOM5 hotstart files
        os.system('cp '+hotstart_folder+'/coupler.res '+full_directory+'/INPUT/') # copy MOM5 file stating present date
        os.system('cp '+hotstart_folder+'/res*.nc '+full_directory+'/')           # copy OASIS3 hotstart files
    # otherwise use initial data in INIT folder for a cold start
    else:
        if not os.path.isdir(full_directory + '/INIT'):
            print("ERROR: For a cold start an INIT folder must be provided but could not be found. The model will probably crash.")
        else:
            os.system('cp '+full_directory+'/INIT/* '+full_directory+'/INPUT/')
        
    info_file_name = full_directory + "/RUN_INFO"
    with open(info_file_name, 'w') as file:
        file.write(get_run_information.get_run_information(IOW_ESM_ROOT, debug_mode))
    file.close()

    return
