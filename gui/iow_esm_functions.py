# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:55:17 2021

@author: Sven
"""

from iow_esm_globals import *
from iow_esm_error_handler import IowEsmErrors

class IowEsmFunctions:
    def __init__(self, gui):
        self.gui = gui
        self.eh = self.gui.error_handler
        
    def execute_shell_cmd(self, cmd):
        self.gui.print("Executing: \"" + cmd + "\"...")
        
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        while(p.poll() is None):
            line = p.stdout.readline()
            self.gui.print(" " + str(line.decode("utf-8")[:-1]))
            
        self.gui.print("...done")
                
    def clone_origins(self):
        cmd = root_dir + "/clone_origins.sh"
        self.execute_shell_cmd(cmd)
        
        for ori in read_iow_esm_configuration(root_dir + '/ORIGINS').keys():
            if glob.glob(root_dir + "/" + ori + "/.git") == []:
                self.eh.report_error(*IowEsmErrors.clone_origins)
                return
        
        self.eh.remove_from_log(*IowEsmErrors.clone_origins)
            
        cmd = "find . -name \"*.*sh\" -exec chmod u+x {} \\;"
        os.system(cmd)
        
        cmd = "find " + root_dir + "/components/MOM5/exp/ -name \"*\" -exec chmod u+x {} \\;"
        os.system(cmd)
        
        cmd = "find " + root_dir + "/components/MOM5/bin/ -name \"*\" -exec chmod u+x {} \\;"
        os.system(cmd)
        
        cmd = "find . -name \"configure\" -exec chmod u+x {} \\;"
        os.system(cmd)
        
        self.gui.refresh()
        
    def set_destination(self, dst):
        self.gui.current_destination = dst
        
        self.gui.entries["current_dst"].delete(0, tk.END)
        self.gui.entries["current_dst"].insert(0, self.gui.current_destination)
        
        self.gui.print("Current destination: " + self.gui.current_destination)
        
    def build_origin(self, ori):
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False
        
        cmd = "cd " + ori + "; ./build.sh " + self.gui.current_destination + " " + self.gui.current_build_conf

        self.execute_shell_cmd(cmd)
        
    def build_origins(self):
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False
        
        cmd = "./build.sh " + self.gui.current_destination + " " + self.gui.current_build_conf
        self.execute_shell_cmd(cmd)
        
        return True
        
    def build_origins_first_time(self):
        if not self.build_origins():
            return False
        
        last_build_file = root_dir + "/LAST_BUILD_" + self.gui.current_destination + "_" + self.gui.current_build_conf.split(" ")[0]
        
        if glob.glob(last_build_file) == []:
            self.eh.report_error(*IowEsmErrors.build_origins_first_time)
            #self.gui.refresh()
            return False

        with open(last_build_file, 'r') as file:
            file_content = file.read()
        file.close()
        
        for ori in self.gui.origins:
            if ori.split("/")[-1] not in file_content:
                self.eh.report_error(*IowEsmErrors.build_origins_first_time)
                #self.gui.refresh()
                return False

        self.eh.remove_from_log(*IowEsmErrors.build_origins_first_time)
            
        self.gui.refresh()
        
    def set_build_config(self, mode):
        if mode == "release" or mode == "debug":
            self.gui.current_build_conf = mode + " " + self.gui.current_build_conf.split()[1]
        
        if mode == "fast" or mode == "rebuild":
            self.gui.current_build_conf = self.gui.current_build_conf.split()[0] + " " + mode
        
        self.gui.entries["current_build_config"].delete(0, tk.END)
        self.gui.entries["current_build_config"].insert(0, self.gui.current_build_conf)
        self.gui.print("Current build configuration: " + self.gui.current_build_conf)
        
    def set_setup(self, setup):
        self.gui.current_setups.append(setup)
        if len(self.gui.current_setups) == 1:
            self.gui.entries["current_setups"].insert(tk.END, self.gui.current_setups[-1])
        else:
            self.gui.entries["current_setups"].insert(tk.END, ", " + self.gui.current_setups[-1])
            
        self.gui.print("Current setups: " + str(self.gui.current_setups))
        
    def get_setups_info(self):
        for setup in self.gui.current_setups:
            file_content = ""
            
            if ":" in self.gui.setups[setup]: 
                user_at_host, path = self.gui.setups[setup].split(":")
                cmd = "ssh " + user_at_host + " \"if [ -f " + path +  "/SETUP_INFO ]; then cat " + path + "/SETUP_INFO; fi\""
                self.gui.print(cmd)
                sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                file_content = sp.stdout.read()
                
            else:
                file_name = self.gui.setups[setup] +  "/SETUP_INFO"
                try:
                    with open(file_name, 'r') as file:
                        file_content = file.read()
                    file.close()
                except Exception as e:
                    self.gui.print(e)
                    
            if file_content != "":
                newWindow = tk.Toplevel(self.gui.window)
                label = tk.Label(master=newWindow, text="Info: " + setup + " (" + self.gui.setups[setup] + ")")
                label.pack()
                text = tk.Text(master=newWindow)
                text.insert(tk.END, file_content)
                text.pack()
        
    def clear_setups(self):
        self.gui.current_setups = []
        self.gui.entries["current_setups"].delete(0, tk.END)
        
    def edit_setups(self):
        newWindow = tk.Toplevel(self.gui.window)
        self.gui._edit_file(root_dir + "/SETUPS", root_dir + "/SETUPS", master=newWindow)
        
    def edit_destinations(self):
        newWindow = tk.Toplevel(self.gui.window)
        self.gui._edit_file(root_dir + "/DESTINATIONS", root_dir + "/DESTINATIONS", master=newWindow)
        
    def archive_setup(self):
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False
        
        if len(self.gui.current_setups) > 1:
            self.gui.print("More than one setup is selected. Take the last one as base.")

        archive = self.gui.entries["archive_setup"].get()
        
        cmd = "./archive_setups.sh " + self.gui.current_destination + " " + self.gui.current_setups[-1] + " " + archive
        self.execute_shell_cmd(cmd)
            
    def deploy_setups(self):
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False
        
        for setup in self.gui.current_setups:
            cmd = "./deploy_setups.sh " + self.gui.current_destination + " " + setup
            
            self.execute_shell_cmd(cmd)
            
    def deploy_setups_first_time(self):
        self.deploy_setups()
        self.gui.refresh()
            
    def run(self):
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False 
        
        cmd = root_dir + "/run.sh " + self.gui.current_destination
        for setup in self.gui.current_setups:
            cmd = cmd + " " + setup
            
        self.execute_shell_cmd(cmd)
        
    def store_file_from_tk_text(self, file_name, tk_text):
        content = tk_text.get("1.0", tk.END)
        with open(file_name, 'w') as file:
            file.write(content)
        file.close()
        
        self.gui.refresh()