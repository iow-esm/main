class GlobalSettings:

    def __init__(self, root_dir, global_settings = "input/global_settings.py"):
        
        # create a local dictionary with content of the global_settings file
        ldict = {}
        exec(open(root_dir + "/" + global_settings).read(), globals(), ldict)
        
        # map dictionary entries to class members with the smae name
        for variable in ldict.keys():
            setattr(self, variable, ldict[variable]) 
            
        # TODO test if all non-optional variables are set
            
        self.root_dir = root_dir 
        
        if self.workdir_base[0]=='/': 
            # workdir_base gives absolute path, just use it
            self.work_directory_root = self.workdir_base
        else:
            # workdir_base gives relative path to IOW_ESM_ROOT
            self.work_directory_root = self.root_dir + '/' + self.workdir_base