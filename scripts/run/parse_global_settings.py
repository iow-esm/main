import pickle
import glob

class GlobalSettings:
    """Class that contains the variables of global_settings.py as attributes.

    Attributes will be all that are present in global_settings.py.
        
    Additionally there will be `root_dir` which is the memorized path of root directory and
    `attempt_handler_obj_file`. The latter is the file which is used to serialize the current state of the attempt_handler attribute.  
    IMPORTANT: If you want to start from scratch, you have to remove this file.

    :param root_dir:        Path to the root directory
    :type root_dir:         str
            
    :param global_settings: Path to the global_settings.py file, relative to root_dir, default "input/global_settings.py" 
    :type global_settings:  str
    """

    def __init__(self, root_dir, input_name = ""):

        # memorize the root directory as a part of the global_settings
        self.root_dir = root_dir 

        self.input_name = input_name

        # if input_name is not empty we provide a specific input folder
        if self.input_name != "":
            self.run_name = input_name
            self.input_dir = self.root_dir + "/input/" + self.input_name
        # if it is empty there is only one input folder and the global_settings.py therein specifies the run name
        else:
            self.input_dir = self.root_dir + "/input"
        
        # create a local dictionary with content of the global_settings file
        ldict = {}
        exec(open(self.input_dir + "/global_settings.py").read(), globals(), ldict)

        # check if machine is specified
        try:
            self.machine = ldict["machine"]
        except:
            self.machine = None

        # if machine is specified get variables and store them as embers with the same name
        if self.machine is not None:
            machine_ldict = {}
            exec(open(self.root_dir + "/scripts/run/machine_settings_" + self.machine + ".py").read(), globals(), machine_ldict)
            for variable in machine_ldict.keys():
                setattr(self, variable, machine_ldict[variable]) 
        
        # map dictionary entries to class members with the smae name
        for variable in ldict.keys():

            # check if run_name is specified although name should be given by input folder
            if variable == "run_name":
                try:
                    self.run_name
                    print("Run name is already psecified by input folder name. Setting in global_settings.py has no effect!")
                    continue
                except:
                    pass

            setattr(self, variable, ldict[variable]) 

        try:
            if self.workdir_base[0]=='/': 
            # workdir_base gives absolute path, just use it
                self.global_workdir_base = self.workdir_base + "/" + self.run_name
            # workdir_base gives relative path to IOW_ESM_ROOT
            else:
                self.global_workdir_base = self.root_dir+'/'+self.workdir_base+'/'+self.run_name
        except:
        # workdir_base is not given use default
            self.global_workdir_base = self.root_dir+'/work/'+self.run_name

        if self.local_workdir_base != '':
            self.local_workdir_base += "/"+self.run_name    

        
        # TODO test if all non-optional variables are set
        
        # TODO set optional arguments to their default here

        try:
            self.exchange_grid_type
            #allowed values are "atmos", "bottom", "intersection" (default, equivalent to value None or not set)                                                                
        except:
            self.exchange_grid_type = "intersection"
        
        # check if attempt handler has been set in global_settings
        try: 
            self.attempt_handler
        # if not take the default
        except:
            self.attempt_handler = None
        
        # construct a unique name of the file for serializing the attempt_handler object
        self.attempt_handler_obj_file = self.root_dir + "/" + self.run_name + "_attempt_handler.obj"
        
    
    def serialize_attempt_handler(self):
        """
        Serializes the attempt_handler object into a binary file.

        This function is used to store the state of the attempt_handler object at the end of a run.
        Such it can be restored when starting a new run.

        """    
        
        # if we have no attempt_handler there is nothing to do
        if self.attempt_handler is None:
            return
        
        # dump the object into a file
        with open(self.attempt_handler_obj_file,"wb") as file:
            pickle.dump(self.attempt_handler, file)
            
    
    def deserialize_attempt_handler(self):
        """
        Deserializes the attempt_handler object from a binary file.

        If a file named as attempt_handler_obj_file exists, the attempt_handler object is restore from that.
        If there is not such a file, nothing is done here and the attempt_handler object is initialized as implemented in its contructor.
        
        """       
        
        # if we have no attempt_handler there is nothing to do
        if self.attempt_handler is None:
            return
            
        # if there is not yet a file, we can not restore
        if not glob.glob(self.attempt_handler_obj_file):
            return
        
        # restore the object from a file
        with open(self.attempt_handler_obj_file,"rb") as file:
            self.attempt_handler = pickle.load(file)        