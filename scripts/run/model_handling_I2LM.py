# This script will fill the required files into the work directory for a MOM5 model.
# The function is called from create_work_directories.py 

from datetime import datetime
import os
import shutil

import change_in_namelist
import get_run_information

import glob

from netCDF4 import Dataset
import numpy as np

import re

import model_handling

class ModelHandler(model_handling.ModelHandlerBase):
    def __init__(self, global_settings, my_directory):
        # initialize base class
        model_handling.ModelHandlerBase.__init__(self, model_handling.ModelTypes.other, global_settings, my_directory)
        
    def create_work_directory(self, work_directory_root, start_date, end_date):
    
        # STEP 0: get local parameters from global settings
        IOW_ESM_ROOT        = self.global_settings.root_dir              # root directory of IOW ESM
        init_date           = self.global_settings.init_date             # 'YYYYMMDD'
        coupling_time_step  = self.global_settings.coupling_time_step    # in seconds
        run_name            = self.global_settings.run_name              # string
        debug_mode          = self.global_settings.debug_mode            # FALSE if executables compiled for production mode shall be used, 
                                                            # TRUE if executables compiled for debug mode shall be used
        institution         = self.global_settings.institution
        email               = self.global_settings.email
        
        my_directory        = self.my_directory             # name of model's input folder
        
        
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
        
    def check_for_success(self, work_directory_root, start_date, end_date):
        lastfile = work_directory_root+'/'+self.my_directory+'/'+str(start_date)+'/lbfd'+str(end_date)+'00.nc'
        
        # if restart folder is empty we failed
        if glob.glob(lastfile) == []:
            print('run failed because no file exists:'+lastfile)
            return False
        
        # we succeeded
        return True
    
    def move_results(self, work_directory_root, start_date, end_date):
    
        # work directory of this model instance
        workdir = work_directory_root + '/' + self.my_directory
        # directory for output        
        outputdir = self.global_settings.root_dir + '/output/' + self.global_settings.run_name+'/'+self.my_directory+'/'+str(start_date)
        # directory for hotstarts
        hotstartdir = self.global_settings.root_dir + '/hotstart/' + self.global_settings.run_name+'/'+self.my_directory+'/'+str(end_date)   
        
        # STEP 1: CREATE DIRECTORIES IF REQUIRED
        if (not os.path.isdir(outputdir)): 
            os.makedirs(outputdir)
        if (not os.path.isdir(hotstartdir)):
            os.makedirs(hotstartdir)

        # STEP 2: MOVE OUTPUT
        os.system('mv '+workdir+'/'+str(start_date)+'/* '+outputdir+'/.')
        
        if os.path.isfile(workdir + '/RUN_INFO'):
            os.system('mv '+workdir+'/RUN_INFO '+outputdir+'/.')

        # STEP 3: MOVE HOTSTART
        # there is no real hotstart file, the existence of the hotstart folder marks where we stopped
        
    def get_model_executable(self):
        return "int2lm.exe"
        
    def get_num_threads(self):
        # CCLM model - parallelization is described in INPUT_ORG, e.g. nprocx= 8, nprocy= 24
        
        IOW_ESM_ROOT        = self.global_settings.root_dir              # root directory of IOW ESM
        model               = self.my_directory             # name of model's input folder
        
        inputfile = IOW_ESM_ROOT+'/input/'+model+'/INPUT'
        mythreads_x = 0
        mythreads_y = 0
        if not os.path.isfile(inputfile):
            print('Could not determine parallelization layout because the following file was missing: '+inputfile)
        else :
            f = open(inputfile)
            for line in f:
                match = re.search('nprocx\s*=\s*(\d+)', line) # search for number after 'nprocx=', but allow spaces
                if match:
                    mythreads_x = int(match.group(1))
                match = re.search('nprocy\s*=\s*(\d+)', line) # search for number after 'nprocy=', but allow spaces
                if match:
                    mythreads_y = int(match.group(1))
            f.close()
            mythreads = mythreads_x * mythreads_y
        if mythreads==0:
            print('Could not determine number of threads for model ',model)
            
        return mythreads