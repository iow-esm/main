# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:43:21 2021

@author: Sven
"""

from iow_esm_globals import *

class IowEsmErrorLevels():
    fatal = "fatal"
    warning = "warning"
    info = "info"

class IowEsmErrors():
    clone_origins = (IowEsmErrorLevels.fatal, "Not all origins could be cloned!")
    build_origins_first_time = (IowEsmErrorLevels.fatal, "Not all origins could be built!")
    deploy_setups_first_time = (IowEsmErrorLevels.fatal, "Not all setups could be deployed!")
    destination_not_set = (IowEsmErrorLevels.warning, "Destination not set.")

class IowEsmErrorHandler():
    def __init__(self, gui):
        self.gui = gui
        
        self.levels = {
            IowEsmErrorLevels.fatal : 0,
            IowEsmErrorLevels.warning : 1,
            IowEsmErrorLevels.info : 2
            }
        
        self.errors = {}
        for level in self.levels.keys():
            self.errors[level] = []
            
        self.log_file = root_dir + "/gui.log"
        
        self._read_log()
    
    def _read_log(self):
        try:
            with open(self.log_file, 'r') as file:
                self.errors = json.load(file)
            file.close()
        except:
            pass
        
    def _write_log(self):
        with open(self.log_file, 'w') as file:
            json.dump(self.errors, file)
        file.close()
        
        
    def report_error(self, level, info):
        if level not in self.levels.keys():
            self.gui.print(level + ", no such error level.")
            return False
        
        self._read_log()
        
        self.errors[level].append(info)
        self.gui.print(level + ": " + info)
        
        self._write_log()
        return True
        
    def check_for_error(self, level, info=""):
        self._read_log()
        
        if info == "":
            return self.errors[level] != []
        
        return info in self.errors[level]
        
    def remove_from_log(self, level, info=""):
        self._read_log()
        
        if info == "":
            self.errors[level] = []
        else:
            self.errors[level] = list(filter(lambda a: a != info, self.errors[level]))
            
        self._write_log()
        
    def get_log(self):
        return self.errors