# This script will fill the required files into the work directory for a CCLM model.
# The function is called from create_work_directories.py 

from datetime import datetime
import os
import shutil

import change_in_namelist

import modify_cclm_restart_file

def create_work_directory_CCLM(IOW_ESM_ROOT,        # root directory of IOW ESM
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
    destfile = full_directory+'/lmparbin'
    if not os.path.isfile(destfile):
        # no executable, need to copy
        if debug_mode:
            sourcefile = IOW_ESM_ROOT+'/components/CCLM/cclm/bin_DEBUG/lmparbin'
        else:
            sourcefile = IOW_ESM_ROOT+'/components/CCLM/cclm/bin_PRODUCTION/lmparbin'
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

    # STEP 3: Adjust times in INPUT_IO
    my_startdate = datetime.strptime(start_date,'%Y%m%d')
    my_enddate = datetime.strptime(end_date,'%Y%m%d')
    my_initdate = datetime.strptime(init_date,'%Y%m%d')
    starthours = (my_startdate - my_initdate).days*24
    finalhours = (my_enddate - my_initdate).days*24

    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_IO',
                     after='&IOCTL', before='/END', start_of_line='nhour_restart',
                     new_value = '='+str(starthours)+','+str(finalhours)+','+str(finalhours-starthours)+',')
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_IO',
                     after='&GRIBOUT', before='/END', start_of_line='hcomb',
                     new_value = '='+str(starthours)+','+str(finalhours)+',1,', repeated=True)
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_ORG',
                     after='&RUNCTL', before='/END', start_of_line='ydate_ini',
                     new_value = '=\''+str(init_date)+'00\' ydate_end=\''+str(end_date)+'00\',')
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_ORG',
                     after='&RUNCTL', before='/END', start_of_line='hstart',
                     new_value = '='+str(starthours)+', hstop='+str(finalhours)+',')
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_OASIS',
                     after='&OASISCTL', before='/END', start_of_line='dt_cp',
                     new_value = ' = '+str(coupling_time_step))             

    # STEP 5: Copy hotstart files if a corresponding folder exists
    if (start_date != init_date):
        hotstart_folder = IOW_ESM_ROOT + '/hotstart/' + runname + '/' + my_directory + '/' + start_date
        os.system('cp '+hotstart_folder+'/* '+full_directory+'/')        # copy all hotstart files 
   

    # STEP 6: Get a corrected land mask from restart file
    # restart files currently only exist for the first day of a month
    if coupling_time_step > 0:
        beginning_of_month = start_date[:6] + "01" + start_date[8:]
        modify_cclm_restart_file.modify_cclm_restart_file(work_directory_root, my_directory, beginning_of_month)

    return