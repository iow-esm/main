class GlobalSettings:

    def __init__(self, root_dir, global_settings = "input/global_settings.py"):
        
        # create a local dictionary with content of the global_settings file
        ldict = {}
        exec(open(root_dir + "/" + global_settings).read(), globals(), ldict)
        
        # map dictionary entries to class members with the smae name
        for variable in ldict.keys():
            setattr(self, variable, ldict[variable]) 
            
        # TODO test if all non-optional variables are set
        
        # TODO set optional arguments to their default here
            
        # memorize the root directory as a part of the global_settings
        self.root_dir = root_dir 