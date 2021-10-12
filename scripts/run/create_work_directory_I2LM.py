# This script will fill the required files into the work directory for a CCLM model.
# The function is called from create_work_directories.py 

from datetime import datetime
import os
import shutil

import change_in_namelist
import get_run_information

def create_work_directory_I2LM(IOW_ESM_ROOT,        # root directory of IOW ESM
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
    destfile = full_directory+'/int2lm.exe'
    if not os.path.isfile(destfile):
        # no executable, need to copy
        if debug_mode:
            sourcefile = IOW_ESM_ROOT+'/tools/I2LM/int2lm/bin_DEBUG/int2lm.exe'
        else:
            sourcefile = IOW_ESM_ROOT+'/tools/I2LM/int2lm/bin_PRODUCTION/int2lm.exe'
        # check if file exists
        if os.path.isfile(sourcefile):
            shutil.copyfile(sourcefile,destfile)   # copy the file
        else:
            print('ERROR creating work directory '+full_directory+': Wanted to copy the executable from '+sourcefile+
                  ' but that does not exist. You may have to build it.')
    st = os.stat(destfile)                 # get current permissions
    os.chmod(destfile, st.st_mode | 0o777) # add a+rwx permission



    # STEP 2: Read global options file
    #exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read())

    # STEP 3: Adjust INPUT with global settings
    my_startdate = datetime.strptime(start_date,'%Y%m%d')
    my_enddate = datetime.strptime(end_date,'%Y%m%d')
    my_initdate = datetime.strptime(init_date,'%Y%m%d')
    starthours = (my_startdate - my_initdate).days*24
    finalhours = (my_enddate - my_initdate).days*24
    
    # int2lm needs hours in start time, since we allow at maximum a daily resolution in job run time
    # we will always start from hour zero
    start_date = start_date + '00'
    
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&CONTRL', before='/END', start_of_line='ydate_ini',
                     new_value = '=\''+start_date+'\',')
                     
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&CONTRL', before='/END', start_of_line='hstart',
                     new_value = '=0, hstop='+str(finalhours-starthours)+',')
                     
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&DATA', before='/END', start_of_line='yncglob_contact',
                     new_value = '=\''+email+'\',')
                     
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&DATA', before='/END', start_of_line='yncglob_institution',
                     new_value = '=\''+institution+'\',')
    
    # STEP 2: Read local options file
    exec(open(full_directory  + '/local_settings.py').read(), globals())
    
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&DATA', before='/END', start_of_line='ylmext_lfn',
                     new_value = '=\''+ climatology_file +'\',')
    
    global climatology_dir
    if climatology_dir == "":
        climatology_dir = full_directory
    
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&DATA', before='/END', start_of_line='ylmext_cat',
                     new_value = '=\''+climatology_dir+'\',')
                     
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&DATA', before='/END', start_of_line='yinext_lfn',
                     new_value = '=\'' + coarse_data_pref +start_date+'.nc\',')
                     
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&DATA', before='/END', start_of_line='yinext_cat',
                     new_value = '=\'' + coarse_data_dir + '/year' + start_date[:4] +'\',')                    
    
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&DATA', before='/END', start_of_line='yin_cat',
                     new_value = '=\'' + coarse_data_dir + '/year' + start_date[:4] +'\',')   
                     
    output_dir = full_directory + '/' + start_date[:8]
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&DATA', before='/END', start_of_line='ylm_cat',
                     new_value = '=\'' + output_dir +'\',')   
    
    if not os.path.isdir(output_dir):   
        os.mkdir(output_dir)
                     
    change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT',
                     after='&DATA', before='/END', start_of_line='yncglob_source',
                     new_value = '=\'' + sourcefile +'\',')
                     
    info_file_name = full_directory + "/RUN_INFO"
    with open(info_file_name, 'w') as file:
        file.write(get_run_information.get_run_information(IOW_ESM_ROOT, debug_mode))
    file.close()
    
    return