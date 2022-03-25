import pickle
import glob

class GlobalSettings:
    """Class that contains the variables of global_settings.py as attributes.

    Attributes:
        All that are present in global_settings.py.
        
        additionally:
        root_dir                    Memorized path of root directory.
        attempt_handler_obj_file    File which is used to serialize the current state of the attempt_handler attribute.  
                                    IMPORTANT: If you want to start from scratch, you have to remove this file.
    """

    def __init__(self, root_dir, global_settings = "input/global_settings.py"):
        """
        Imports the global_settings.py file and creates attributes in this class with the same name and values. 

        Parameters
        ----------
            root_dir : str
                Path to the root directory
            global_settings : str, default "input/global_settings.py" 
                Path to the global_settings.py file, relative to root_dir.
                
        """
        
        # create a local dictionary with content of the global_settings file
        ldict = {}
        exec(open(root_dir + "/" + global_settings).read(), globals(), ldict)
        
        # map dictionary entries to class members with the smae name
        for variable in ldict.keys():
            setattr(self, variable, ldict[variable]) 
            
        # TODO test if all non-optional variables are set
        
        # TODO set optional arguments to their default here
        
        # check if attempt handler has been set in global_settings
        try: 
            self.attempt_handler
        # if not take the default
        except:
            self.attempt_handler = None
            
        # memorize the root directory as a part of the global_settings
        self.root_dir = root_dir 
        
        # construct a unique name of the file for serializing the attempt_handler object
        self.attempt_handler_obj_file = self.root_dir + "/" + self.run_name + "_attempt_handler.obj"
        
    
    def serialize_attempt_handler(self):
        """
        Serializes the attempt_handler object into a binary file.

        This function is used to store the state of the attempt_handler object at the end of a run.
        Such it can be restored when starting a new run.

        Parameters
        ----------
        None

        Returns
        -------
        None
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
        
        Parameters
        ----------
        None

        Returns
        -------
        None
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