# This script will fill the required files into the work directory for a MOM5 model.
# The function is called from create_work_directories.py 

from datetime import datetime
import os
import shutil

import change_in_namelist

import glob

import model_handling

class ModelHandler(model_handling.ModelHandlerBase):
    def __init__(self, global_settings, my_directory):
        # initialize base class
        model_handling.ModelHandlerBase.__init__(self, model_handling.ModelTypes.flux_calculator, global_settings, my_directory)
        
    def create_work_directory(self, work_directory_root, start_date, end_date):
    
        # STEP 0: get local parameters from global settings
        IOW_ESM_ROOT        = self.global_settings.root_dir              # root directory of IOW ESM
        init_date           = self.global_settings.init_date             # 'YYYYMMDD'
        coupling_time_step  = self.global_settings.coupling_time_step    # in seconds
        debug_mode          = self.global_settings.debug_mode            # FALSE if executables compiled for production mode shall be used, 
                                                            # TRUE if executables compiled for debug mode shall be used
                                                            
        my_directory        = self.my_directory             # name of model's input folder
        
        # STEP 1: CHECK IF EXECUTABLE ALREADY EXISTS, IF NOT COPY IT
        full_directory = work_directory_root+'/'+my_directory
        destfile = full_directory+'/flux_calculator'
        if not os.path.isfile(destfile):
            # no executable, need to copy
            if debug_mode:
                sourcefile = IOW_ESM_ROOT+'/components/flux_calculator/bin_DEBUG/flux_calculator' # we may change this in future
            else:
                sourcefile = IOW_ESM_ROOT+'/components/flux_calculator/bin_PRODUCTION/flux_calculator'
            # check if file exists
            if os.path.isfile(sourcefile):
                shutil.copyfile(sourcefile,destfile)   # copy the file
            else:
                print('ERROR creating work directory '+full_directory+': Wanted to copy the executable from '+sourcefile+
                      ' but that does not exist. You may have to build it.')
        st = os.stat(destfile)                 # get current permissions
        os.chmod(destfile, st.st_mode | 0o777) # add a+rwx permission

        # STEP 2: calculate number of timesteps
        my_startdate = datetime.strptime(start_date,'%Y%m%d')
        my_enddate = datetime.strptime(end_date,'%Y%m%d')
        my_initdate = datetime.strptime(init_date,'%Y%m%d')

        rundays = (my_enddate - my_startdate).days
        runseconds = int(rundays)*24*3600
        timesteps = runseconds//coupling_time_step

        # STEP 3: copy flux_calculator.nml file and change timestep and number of time steps
        os.system('cp '+IOW_ESM_ROOT+'/input/flux_calculator.nml '+full_directory+'/flux_calculator.nml')
        
        change_in_namelist.change_in_namelist(filename=full_directory+'/flux_calculator.nml',
                         after='&input', before='/', start_of_line='timestep',
                         new_value = '='+str(coupling_time_step))
        change_in_namelist.change_in_namelist(filename=full_directory+'/flux_calculator.nml',
                         after='&input', before='/', start_of_line='num_timesteps',
                         new_value = '='+str(timesteps))
        
        # STEP 4: Create an empty folder named "mappings" and place exchange grid files and mapping files there
        os.makedirs(full_directory+'/mappings') 
        os.system('cp '+IOW_ESM_ROOT+'/input/CCLM*/mappings/?_grid_exchangegrid.nc '+full_directory+'/mappings')
        os.system('cp '+IOW_ESM_ROOT+'/input/*/mappings/remap_*.nc '+full_directory+'/mappings')
        os.system('cp '+IOW_ESM_ROOT+'/input/CCLM*/mappings/regrid_*.nc '+full_directory+'/mappings')

        return
        
    def get_model_executable(self):
        return 'flux_calculator'
        
    def get_num_threads(self):
        # only one thread for the flux_calculator so far
        mythreads = 1
        return mythreads