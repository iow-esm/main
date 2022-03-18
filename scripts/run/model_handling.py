import os
import importlib
import sys

# possible model types
class ModelTypes:
    atmosphere          = "atmosphere"          # model type of all atmospheric models
    bottom              = "bottom"              # model type of all bottom models
    flux_calculator     = "flux_calculator"     # reserved only for the flux_calculator
    other               = "other"               # components, tools that are not coupled, as e.g. int2lm
    
# get a single model handler
def get_model_handler(global_settings, model):
    # argument model contains string "model_domain"
    
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

# function to get model handlers from directories found in input folder
def get_model_handlers(global_settings):
    
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
     
# common base class (interface) for specific model handlers
class ModelHandlerBase:
    # base constructor must be called in constructor of inheriting class
    def __init__(self, model_type, global_settings, my_directory):
        self.global_settings = global_settings              # global settings object
        self.my_directory = my_directory                    # name of model's input folder
        self.model_type = model_type                        # one of the ModelTypes
        
    def create_work_directory(self, work_directory_root, start_date, end_date):
        pass
        
    def check_for_success(self, work_directory_root, start_date, end_date):
        return True
    
    def move_results(self, work_directory_root, start_date, end_date):
        pass
    
    def grid_convert_to_SCRIP(self):
        pass
        
    def get_model_executable(self):
        return ""
        
    def get_num_threads(self):
        return 0