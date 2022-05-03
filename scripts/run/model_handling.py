import os
import importlib
import sys


class ModelTypes:
    """Available model types
    """
    
    atmosphere          = "atmosphere"
    """Identifier for atmospheric models.
    
    Note that there can be only one atmospheric model in a coupled run.
    """
        
    bottom              = "bottom"
    """Identifier for bottom models as ocean or land models.
    
    In contrast to the atmosphere there can be several bottom models in a coupled run.
    """
    
    flux_calculator     = "flux_calculator"
    """Reserved only for the flux_calculator.
    """
    
    other               = "other"
    """Components, tools that are not coupled, as e.g. the int2lm tool.
    """
    
class GridTypes:
    t_grid = "t_grid"
    u_grid = "u_grid"
    v_grid = "v_grid"

def get_model_handler(global_settings, model):
    """Method to get a single model handler.
    
    This method imports the model-specific handling module `model_handling_ABCD.py`
    where `ABCD` is a four letter acronym of the model.
    
    :param global_settings:         Object containing the global settings
    :type global_settings:          class:`GlobalSettings` 
    
    :param model:                   Name of the model's input folder, usually model_domain, e.g. MOM5_Baltic. IMPORTANT: model names can only have four letters as e.g. MOM5, CCLM, GETM etc.
    :type model:                    str
                                    
    :return:                        Specific model handler object
    :rtype:                         class:`ModelHandler`      
    """
    
    try:   
        # try to import the corresponding module
        model_handling_module = importlib.import_module("model_handling_" + model[0:4])
        # and create the handler object
        model_handler = model_handling_module.ModelHandler(global_settings, model)
    except:
        # if there is no model handler we have to abort here!
        print("No handler has been found for model " + model + ". Add a module model_handling_" + model[0:4] + ".py")
        sys.exit()
    
    return model_handler


def get_model_handlers(global_settings):
    """Method to get handlers for all models that have input folders.
    
    This method checks the input folder and creates model handler objects for found models. 
    If there is one atmospheric model and at least one bottom model the run will be interpreted as a coupled run.
    In that case the flux_calculator is added to the models.
    
    :param global_settings:         Object containing the global settings
    :type global_settings:          class:`GlobalSettings` 
                                    
    :return:                        Dictionary of specific model handler objects. The keys of the dictionary are the names of the input folders
    :rtype:                         dict    
    """
    
    # get a list of input folders 
    models = [d for d in os.listdir(global_settings.root_dir+'/input/') if os.path.isdir(os.path.join(global_settings.root_dir+'/input/',d))]
    
    # assume uncoupled case first
    coupled = False
    
    found_atmos = False
    
    # get model handlers for all found models
    model_handlers = {}
    for model in models:
        model_handlers[model] = get_model_handler(global_settings, model)
        
        # we can only have one atmosphere
        if (model_handlers[model].model_type == ModelTypes.atmosphere) and found_atmos:
            print("Only one atmospheric model is currently supported. Abort.")
            sys.exit()
        
        # we found the first atmospheric model
        if (model_handlers[model].model_type == ModelTypes.atmosphere):
            found_atmos = True
               # if there are other models and fluxcalcualtor should be included we perform a coupled run
            if (len(models) > 1) and (global_settings.flux_calculator_mode != "none"):
                coupled = True     
        
    # we need flux_calculator as additional model if we run a coupled simulation
    if global_settings.flux_calculator_mode=='single_core_per_bottom_model' and coupled:
        model = 'flux_calculator'
        models = models + [model] 
        model_handling_module = importlib.import_module("model_handling_" + model[0:4])
        model_handlers[model] = model_handling_module.ModelHandler(global_settings, model)

    return model_handlers
     
     
class ModelHandlerBase:
    """Base class for all specific model handler.
    
    This constructor must be called in the constructor of the child class as e.g.
    `ModelHandlerBase.__init__(self, model_handling.ModelTypes.bottom, global_settings, my_directory)`
    The child class must be implmented as `ModelHandler` in a python module called `model_handling_ABCD.py` 
    where `ABCD` is a four letter acronym of your model.
    
    :param global_settings:         Object containing the global settings
    :type global_settings:          class:`GlobalSettings` 
    
    :param my_directory:            Name of the model's input folder, usually model_domain, e.g. MOM5_Baltic. IMPORTANT: model names can only have four letters as e.g. MOM5, CCLM, GETM etc.
    :type my_directory:             str
                                    
    :param model_type:              Must be one of attributes of class `ModelTypes`
    :type model_type:               str
    """
    
    # base constructor must be called in constructor of inheriting class
    def __init__(self, model_type, global_settings, my_directory, grids = [GridTypes.t_grid]): 
        self.global_settings = global_settings              # global settings object
        self.my_directory = my_directory                    # name of model's input folder
        self.model_type = model_type                        # one of the ModelTypes
        self.grids = grids                                  # one of the available grids
        
    def create_work_directory(self, work_directory_root, start_date, end_date):
        """Method to perform model-specific steps for creating the work directory.

        This method is overwritten by the child class and will be called after 
        the work directory has been created and the content of the input folder has been copied to that work directory.
        
        It should typically do:
        
        * Copy the executable(s) to the work directory (not into subfolders)
        
        * Apply current start date and end date to input files
        
        :param work_directory_root:     Is the local work directory common to all models, thus it is one lvel above my_directory
        :type work_directory_root:      str
        
        :param start_date:              Start date of the current working period, format YYYYMMDD, e.g. 20220325 for the 25th of March 2022
        :type start_date:               str 
                                        
        :param end_date:                End date of the current working period, format YYYYMMDD, e.g. 20220325 for the 25th of March 2022
        :type end_date:                 str
        """    
        pass
        
    def check_for_success(self, work_directory_root, start_date, end_date):
        """Method to check if model run was successful or not.

        This method is overwritten by the child class and will be called after 
        the MPI task has finished.
        
        It should typically do:
        
        * Check for the existence of some specific output files.
        
        :param work_directory_root:     Is the local work directory common to all models, thus it is one lvel above my_directory
        :type work_directory_root:      str
        
        :param start_date:              Start date of the current working period, format YYYYMMDD, e.g. 20220325 for the 25th of March 2022
        :type start_date:               str 
                                        
        :param end_date:                End date of the current working period, format YYYYMMDD, e.g. 20220325 for the 25th of March 2022
        :type end_date:                 str
        
        :return:                        `True` if model has finished successfully, `False` otherwise
        :rtype:                         bool        
        """        
        return True
    
    def move_results(self, work_directory_root, start_date, end_date):
        """Method to move results from work to output folder.

        This method is overwritten by the child class and will be called after 
        the check_for_success method has returned `True`.
        
        It should typically do:
        
        * Move all files you want to keep that are used or produced by your model.
        
        :param work_directory_root:     Is the local work directory common to all models, thus it is one lvel above my_directory
        :type work_directory_root:      str
        
        :param start_date:              Start date of the current working period, format YYYYMMDD, e.g. 20220325 for the 25th of March 2022
        :type start_date:               str 
                                        
        :param end_date:                End date of the current working period, format YYYYMMDD, e.g. 20220325 for the 25th of March 2022
        :type end_date:                 str      
        """     
        pass
    
    def grid_convert_to_SCRIP(self):
        pass
        
    def get_model_executable(self):
        """Method to get the name of the model's excutable.

        This method is overwritten by the child class and will be called when the MPI run script is created.
        
        It should typically do:
        
        * Return the name of the executable that is located in your work directory after create_work_directory has been called. 
                                                            
        :return:                        Name of the excutable, e.g. "fms_MOM_SIS.x"
        :rtype:                         str
        """         
        return ""
        
    def get_num_threads(self):
        """Method to get the number of threads the model is using.

        This method is overwritten by the child class and will be called when the paralleization layout is created.
        
        It should typically do:
        
        * Return the number of threads using e.g. settings in the model's input files. 
                                        
        :return:                        Number of used threads
        :rtype:                         int    
        """    
        return 0