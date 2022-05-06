# This script will fill the required files into the work directory for a MOM5 model.
# The function is called from create_work_directories.py 

from datetime import datetime
import os
import shutil

import change_in_namelist

import glob

import model_handling

class FluxCalculatorModes:
    single_core = "single_core_per_bottom_model"
    on_bottom_cores = "on_bottom_model_cores"
    none = "none"

class ModelHandler(model_handling.ModelHandlerBase):
    """Base class for all specific model handler.
    
    This constructor must be called in the constructor of the child class as e.g.
    `ModelHandlerBase.__init__(self, model_handling.ModelTypes.bottom, global_settings, my_directory)`
    The child class must be implmented as `ModelHandler` in a python module called `model_handling_ABCD.py` 
    where `ABCD` is a four letter acronym of your model.
    
    :param global_settings:         Object containing the global settings
    :type global_settings:          class:`GlobalSettings` 
    
    :param my_directory:            Name of the model's input folder, usually model_domain, e.g. MOM5_Baltic. IMPORTANT: model names can only have four letters as e.g. MOM5, CCLM, GETM etc.
    :type my_directory:             str
                                    
    :param model_handlers:          Dictionary with model handlers of other models that are coupled to the flux calculator. The keys are the directory names of the other models.
                                    Default: {} must be present to be created in the `model_handling.get_model_handler` method. 
    :type model_type:               dict {str : class:`ModelHandler`}
    """
    def __init__(self, global_settings, my_directory, model_handlers = {}):
        # initialize base class
        model_handling.ModelHandlerBase.__init__(self,  model_handling.ModelTypes.flux_calculator, 
                                                        global_settings, 
                                                        my_directory, 
                                                        grids = [model_handling.GridTypes.t_grid, model_handling.GridTypes.u_grid, model_handling.GridTypes.v_grid])     
        # memorize the model handlers for the other models
        self.model_handlers = model_handlers                                                                                                                                    
        
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
        # TODO when several bottom models are supported, here should be a check for which model we adapt the num_tasks_per_model
        mythreads = self.get_my_threads()
        for i, model in enumerate(mythreads.keys()):
            change_in_namelist.change_in_namelist(filename=full_directory+'/flux_calculator.nml',
                            after='&input', before='/', start_of_line='num_tasks_per_model(' + str(i+1) + ')',
                            new_value = '='+str(mythreads[model]) + ',_*_')                         
        
        # STEP 4: Create an empty folder named "mappings" and place exchange grid files and mapping files there
        os.makedirs(full_directory+'/mappings') 
        for mapping_dir in glob.glob(IOW_ESM_ROOT+'/input/*/mappings'):
            os.system('cp '+ mapping_dir +'/?_grid_exchangegrid.nc '+full_directory+'/mappings')
            os.system('cp '+ mapping_dir +'/remap_*.nc '+full_directory+'/mappings')
            os.system('cp '+ mapping_dir +'/regrid_*.nc '+full_directory+'/mappings')

        return
        
    def get_model_executable(self):
        return 'flux_calculator'
        
    def get_num_threads(self):

        mythreads = self.get_my_threads()
        # get total number of threads for the flux calculator
        sum_mythreads = 0
        for model in mythreads.keys():
            sum_mythreads += mythreads[model]  

        return sum_mythreads

    def get_my_threads(self):
        # get a list of the models that are coupled to the flux calculator
        models = list(self.model_handlers.keys())

        # get number of threads from the bottom models or 
        mythreads = {}
        for model in models:
            # only consider bottom models here
            if self.model_handlers[model].model_type != model_handling.ModelTypes.bottom:
                continue

            if self.global_settings.flux_calculator_mode == FluxCalculatorModes.on_bottom_cores: # one core for each bottom model one
                mythreads[model] = self.model_handlers[model].get_num_threads()  
            elif self.global_settings.flux_calculator_mode == FluxCalculatorModes.single_core: # single core per bottom model
                mythreads[model] = 1  
            else: # case flux_calculator_mode = 'none' -> no flux calculator should run
                mythreads[model] = 0      
        
        return mythreads
