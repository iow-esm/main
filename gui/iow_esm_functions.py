# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:55:17 2021

@author: Sven
"""

from iow_esm_globals import *
from iow_esm_error_handler import IowEsmErrors

import platform

from threading import Thread, Event

import os
import signal

class IowEsmFunctions:
    def __init__(self, gui):
        self.gui = gui
        self.eh = self.gui.error_handler
        
        if platform.system() == "Linux":
            self.bash = "`which bash`"
        if platform.system() == "Windows":
            self.bash = "\"C:\\msys64\\usr\\bin\\env.exe\" MSYSTEM=MINGW64 /bin/bash"
            
        self.shell_cmd_thread = Thread()
        self.cancel_cmd = Event()
        self.output = ""
        
    def start_execute_shell_cmd(self, cmd, printing, stop_event):
        
        cmd = self.bash + " -l -c \"cd " + root_dir.replace("\\","/") + "; " + cmd + "\""

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
        
        while(p.poll() is None):
            if printing:
                line = p.stdout.readline()
                self.gui.print(" " + str(line.decode("utf-8")[:-1]))
            else:
                pass
            
            if stop_event.is_set():
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                self.gui.print("...canceled")
                stop_event.clear()
                return
            
        if printing:
            self.gui.print("...done")
            
        self.output = str(p.stdout.read().decode("utf-8"))
        return 
        
    def execute_shell_cmd(self, cmd, printing = True, blocking = True):
        
        if printing:
            self.gui.print("Executing: \"" + cmd + "\"...")
        
        if blocking:
            self.start_execute_shell_cmd(cmd, printing, self.cancel_cmd)
            return self.output
        
        if self.shell_cmd_thread.is_alive():
            self.gui.print("Warning: Another command is already running. Please wait.")
            return ""
        
        self.shell_cmd_thread = Thread(target = self.start_execute_shell_cmd, args = (cmd, printing, self.cancel_cmd))
        self.shell_cmd_thread.start()  

        return self.output
    
    def cancel_shell_cmd(self):
        
        if not  self.shell_cmd_thread.is_alive():
            self.gui.print("Warning: No command is running.")
            return 
        
        self.cancel_cmd.set()
                
    def clone_origins(self):
        cmd = "./clone_origins.sh"
        self.execute_shell_cmd(cmd)
        
        for ori in read_iow_esm_configuration(root_dir + '/ORIGINS').keys():
            if glob.glob(root_dir + "/" + ori + "/.git") == []:
                self.eh.report_error(*IowEsmErrors.clone_origins)
                return
        
        self.eh.remove_from_log(*IowEsmErrors.clone_origins)
        
        self.gui.refresh()
        
    def clone_origin(self, origin):

        cmd = "./clone_origins.sh " + origin
        self.execute_shell_cmd(cmd)
        
        if glob.glob(root_dir + "/" + origin + "/.git") == []:
            self.eh.report_error(*IowEsmErrors.clone_origins)
            return
        
        self.eh.remove_from_log(*IowEsmErrors.clone_origins)

    def check_for_available_inputs(self):
        file_content = ""
        user_at_host, path = self.gui.destinations[self.gui.current_destination].split(":")
        cmd = "ssh " + user_at_host + " \"if [ -d " + path +  "/input ]; then ls " + path + "/input; fi\""
        self.gui.print("Check for available inputs...")
        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        file_content = sp.stdout.read().decode("utf-8") 

        if file_content == "":
            self.gui.print("Found: None")
            self.gui.print("You should deploy a setup first, if you want to run the model.")
            self.gui.available_inputs = []
            return

        if "global_settings.py" in file_content:
            self.gui.available_inputs = ["input"]
        else:
            self.gui.available_inputs = file_content.split("\n")
            self.gui.available_inputs.remove("")
        
        self.gui.print("Found: "+str(self.gui.available_inputs))
        
    def set_destination(self, dst):
        self.gui.current_destination = dst

        self.gui.print("Current destination: ")
        
        if dst == "":
            self.gui.print(" None")
            return
        
        self.gui.print(" " + self.gui.current_destination + " (" + self.gui.destinations[self.gui.current_destination] + ")" )
        self.check_for_available_inputs()

    def set_sync_destination(self, dst):
        self.gui.current_sync_destination = dst

        self.gui.print("Current synchronization destination: ")
        
        if dst == "":
            self.gui.print(" None")
            return
        
        self.gui.print(" " + self.gui.current_sync_destination + " (" + self.gui.destinations[self.gui.current_sync_destination] + ")" )        
        
    def build_origin(self, ori):
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False
        
        ori = ori.replace("\\","/")
        cmd = "cd " + ori + "; ./build.sh " + self.gui.current_destination + " " + self.gui.current_build_conf

        self.execute_shell_cmd(cmd, blocking = False)
        
    def build_origins(self):
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False
        
        cmd = "./build.sh " + self.gui.current_destination + " " + self.gui.current_build_conf
        self.execute_shell_cmd(cmd, blocking = False)
        
        return True
        
    def build_origins_first_time(self):
        
        # try to build the origins
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False
        
        cmd = "./build.sh " + self.gui.current_destination + " " + self.gui.current_build_conf
        self.execute_shell_cmd(cmd)
        
        # if build has happened a file has been created, if not log error
        last_build_file = root_dir + "/LAST_BUILD_" + self.gui.current_destination + "_" + self.gui.current_build_conf.split(" ")[0]
        
        if glob.glob(last_build_file) == []:
            self.eh.report_error(*IowEsmErrors.build_origins_first_time)
            return False

        # in the file all origins should appear by name
        with open(last_build_file, 'r') as file:
            file_content = file.read()
        file.close()
        
        for ori in self.gui.origins:
            if ori.split("/")[-1] not in file_content:
                self.eh.report_error(*IowEsmErrors.build_origins_first_time)
                return False

        # if everything went fine we can remove old errors
        self.eh.remove_from_log(*IowEsmErrors.build_origins_first_time)
        
    def set_build_config(self, mode):
        if mode == "release" or mode == "debug":
            self.gui.current_build_conf = mode + " " + self.gui.current_build_conf.split()[1]
        
        if mode == "fast" or mode == "rebuild":
            self.gui.current_build_conf = self.gui.current_build_conf.split()[0] + " " + mode
        
        self.gui.print("Current build configuration: " + self.gui.current_build_conf)
        
    def set_setup(self, setup):
        if setup == "":
            self.clear_setups()
            return
        
        self.gui.current_setups.append(setup)
        if len(self.gui.current_setups) == 1:
            self.gui.entries["current_setups"].insert(tk.END, self.gui.current_setups[-1])
        else:
            self.gui.entries["current_setups"].insert(tk.END, ", " + self.gui.current_setups[-1])
            
        self.gui.print("Current setups: ")
        for setup in self.gui.current_setups:
            self.gui.print(" " + setup + " (" + str(self.gui.setups[setup]) + ")")
        
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
        
        self.gui.print("Current setups: []")
        
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
        
        cmd = "./archive_setup.sh " + self.gui.current_destination + " " + self.gui.current_setups[-1] + " " + archive
        self.execute_shell_cmd(cmd)
            
    def deploy_setups(self):
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False
        
        for setup in self.gui.current_setups:
            cmd = "./deploy_setups.sh " + self.gui.current_destination + " " + setup
            
            self.execute_shell_cmd(cmd)
            
        #self.clear_setups()
        
        return True
            
    def deploy_setups_first_time(self):
        if not self.deploy_setups():
            return False
        
        last_setups_file = root_dir + "/LAST_DEPLOYED_SETUPS_" + self.gui.current_destination
        
        if glob.glob(last_setups_file) == []:
            self.eh.report_error(*IowEsmErrors.deploy_setups_first_time)
            return False

        self.eh.remove_from_log(*IowEsmErrors.deploy_setups_first_time)
            
    def run(self):
        if self.gui.current_destination == "":
            self.eh.report_error(*IowEsmErrors.destination_not_set)
            return False 
        
        cmd = "./run.sh " + self.gui.current_destination
        
        if self.gui.prepare_before_run.get() != 0:
            cmd += " prepare-before-run"

        self.gui.print("abc "+self.gui.current_sync_destination)

        if self.gui.current_sync_destination != "":
            cmd += " sync_to=" + self.gui.current_sync_destination
        
        for setup in self.gui.current_setups:
            cmd = cmd + " " + setup
            
        self.execute_shell_cmd(cmd, blocking = False)
        
    def store_file_from_tk_text(self, file_name, tk_text):
        content = tk_text.get("1.0", tk.END)
        with open(file_name, 'w', newline='') as file: # newline='' avoids carriage return under Windows
            file.write(content)
        file.close()
        
        self.gui.refresh()