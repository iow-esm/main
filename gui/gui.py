# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 10:26:50 2021

@author: Sven
"""

import tkinter as tk
import os
import glob
from functools import partial

root_dir = "."

class IowEsmFunctions:
    def __init__(self, gui):
        self.gui = gui
                
    def clone_origins(self):
        cmd = root_dir + "/clone_origins.sh"
        self.gui.print(cmd)
        os.system(cmd)
        
        cmd = "find . -name \"*.sh\" -exec chmod u+x {} \\;"
        os.system(cmd)
        
        cmd = "find . -name \"configure\" -exec chmod u+x {} \\;"
        os.system(cmd)
        
        self.gui.refresh()
        
    def set_destination(self, dst):
        self.gui.current_destination = dst
        
        self.gui.entries["current_dst"].delete(0, tk.END)
        self.gui.entries["current_dst"].insert(0, self.gui.current_destination)
        
        self.gui.print("Current destination is " + self.gui.current_destination)
        
    def build_origin(self, ori):
        if self.gui.current_destination == "":
            self.gui.print("No destination is set.")
            return False
        
        self.gui.print("cd " + ori + "; ./build.sh " + self.gui.current_destination + " " + self.gui.current_build_conf)
        
    def build_origins(self):
        if self.gui.current_destination == "":
            self.gui.print("No destination is set.")
            return False
        
        cmd = "./build.sh " + self.gui.current_destination + " " + self.gui.current_build_conf
        self.gui.print(cmd)
        os.system(cmd)
        
    def build_origins_first_time(self):
        self.build_origins()
        self.gui.refresh()
        
    def set_setup(self, setup):
        self.gui.current_setups.append(setup)
        if len(self.gui.current_setups) == 1:
            self.gui.entries["current_setups"].insert(tk.END, self.gui.current_setups[-1])
        else:
            self.gui.entries["current_setups"].insert(tk.END, ", " + self.gui.current_setups[-1])
        
    def clear_setups(self):
        self.gui.current_setups = []
        self.gui.entries["current_setups"].delete(0, tk.END)
        
    def deploy_setups(self):
        if self.gui.current_destination == "":
            self.gui.print("No destination is set.")
            return False
        
        for setup in self.gui.current_setups:
            cmd = "./deploy_setups.sh " + self.gui.current_destination + " " + setup
            self.gui.print(cmd)
            os.system(cmd)
            
    def deploy_setups_first_time(self):
        self.deploy_setups()
        self.gui.refresh()
            
    def run(self):
        if self.gui.current_destination == "":
            self.gui.print("No destination is set.")
            return False 
        
        cmd = root_dir + "/run.sh " + self.gui.current_destination
        for setup in self.gui.current_setups:
            cmd = cmd + " " + setup
            
        self.gui.print(cmd)
        os.system(cmd)
        
    def store_file_from_tk_text(self, file_name, tk_text):
        content = tk_text.get("1.0", tk.END)
        with open(file_name, 'w') as file:
            file.write(content)
        file.close()
        
        self.gui.refresh()
        
class FunctionButton(tk.Button):
    def __init__(self, text, command, master=None):
        tk.Button.__init__(self,
            master=master,
            text=text,
            bg="blue",
            fg="yellow",
            command=command   
        )
        
class SetButton(tk.Button):
    def __init__(self, text, command, master=None):
        tk.Button.__init__(self,
            master=master,
            text=text,
            command=command   
        )
        
def read_iow_esm_configuration(file_name):
    
    config = {}
    with open(file_name, "r") as f:
        for line in f:
            (key, val) = line.split()
            config[key] = val
            
    return config

class IowEsmGui:
    def __init__(self):
        self.window = tk.Tk(className="IOW_ESM")
        #self.window.geometry("500x500")
        
        self.labels = {}
        self.entries = {}
        self.buttons = {}
        self.texts = {}
        self.frames = {}
        
        self.restart = False
        
        self.labels["greeting"] = tk.Label(text="Welcome to the IOW_ESM GUI!")
        self.labels["greeting"].pack()
        
        self.functions = IowEsmFunctions(self)
        
        self.texts["monitor"] = tk.Text()

        if not self._check_origins():
            cmd = "find . -name \"*.sh\" -exec chmod u+x {} \\;"
            os.system(cmd)
            self._build_window_clone_origins()
            return
        
        if not self._check_destinations():
            self._build_window_edit_destinations()
            return
        
        self.current_destination = ""
        self.current_build_conf = "release fast"
        
        if not self._check_last_build():
            self._build_frame_destinations()
            self._build_frame_build(True)
            return
        
        self.current_setups = []
        
        if not self._check_setups():
            self._build_window_edit_setups()
            return
        
        if not self._check_last_deployed_setups():
            self._build_frame_destinations()
            self._build_frame_setups(True)
            return
        
        self._build_window()
        
    def refresh(self):
        self.window.destroy()
        self.restart = True
        
    def print(self, text):
        self.texts["monitor"].insert(tk.END, str(text) + "\n")
        
    def _check_origins(self):
        self.origins = []
        try:
            available_origins = read_iow_esm_configuration(root_dir + "/ORIGINS").keys()
        except:
            self.print("There is no ORIGINS file. Abort.")
            exit()
        
        for ori in available_origins:
            if os.path.isdir(root_dir + "/" + ori):
                self.origins.append(root_dir + "/" + ori)

        self.print("Available origins:")
        self.print(self.origins)
        
        return self.origins != []
    
    def _check_destinations(self):
        try:
            self.destinations = read_iow_esm_configuration(root_dir + "/DESTINATIONS")
            self.print("Available destinations:")
            self.print(self.destinations)
            return True
        except:
            self.destinations = {}
            return False
        
    def _check_last_build(self):
        return glob.glob(root_dir + "/LAST_BUILD*") != []
    
    def _check_setups(self):
        try:
            self.setups = read_iow_esm_configuration(root_dir + "/SETUPS")
            self.print("Available setups:")
            self.print(self.setups)
            return True
        except:
            self.setups = {}
            return False
        
    def _check_last_deployed_setups(self):
        return glob.glob(root_dir + "/LAST_DEPLOYED_SETUPS*") != []
        
    def _edit_file(self, src_name, dst_name=""):
        
        if dst_name == "":
            dst_name = src_name
            
        with open(src_name, 'r') as file:
            src_content = file.read()
        file.close()
        
        self.texts["edit_" + dst_name] = tk.Text()
        self.texts["edit_" + dst_name].insert(tk.END, src_content)
        self.texts["edit_" + dst_name].pack()
        
        self.buttons["store_" + dst_name] = FunctionButton("Store " + dst_name, partial(self.functions.store_file_from_tk_text, dst_name, self.texts["edit_" + dst_name]))
        self.buttons["store_" + dst_name].pack()
        
    def _build_window_clone_origins(self):
        self.labels["clone_origins"] = tk.Label(
            text="You are using the IOW_ESM for the first time.",
        )
        self.labels["clone_origins"].pack()

        self.buttons["clone_origins"] = FunctionButton("Clone origins", self.functions.clone_origins)
        self.buttons["clone_origins"].pack()
        
        self.texts["monitor"].pack()
        
    def _build_window_edit_destinations(self):
        self.labels["edit_destinations"] = tk.Label(
            text="You have to edit your DESTINATIONS file",
        )
        self.labels["edit_destinations"].pack()
        
        self._edit_file(root_dir + "/DESTINATIONS.example", root_dir + "/DESTINATIONS")
        
        self.texts["monitor"].pack()
        
    def _build_window_edit_setups(self):
        self.labels["edit_setups"] = tk.Label(
            text="You have to edit your SETUPS file",
        )
        self.labels["edit_setups"].pack()
        
        self._edit_file(root_dir + "/SETUPS.example", root_dir + "/SETUPS")
        
        self.texts["monitor"].pack()
        
    def _build_frame_destinations(self):
        
        # create destinations frame
        self.frames["destinations"] = tk.Frame(master=self.window)
        
        # create objects of the frame
        self.labels["destinations"] = tk.Label(master=self.frames["destinations"], text="Destinations")
        
        for dst in self.destinations.keys():
            self.buttons["set_" + dst] = SetButton(dst, partial(self.functions.set_destination, dst), master=self.frames["destinations"])
            
        self.labels["current_dst"] = tk.Label(text="Current destination", master=self.frames["destinations"])
        self.entries["current_dst"] = tk.Entry(master=self.frames["destinations"])
        
        # pack everything on a grid
        columnspan = len(self.destinations)
        self.labels["destinations"].grid(row=0, columnspan=columnspan)
        
        for c, dst in enumerate(self.destinations.keys()):
            self.buttons["set_" + dst].grid(row=1, column=c)
            
        self.labels["current_dst"].grid(row=3, columnspan=columnspan)
        self.entries["current_dst"].grid(row=4, columnspan=columnspan)
        
        # pack the frame
        self.frames["destinations"].pack(padx='5', pady='5')
        
        
    def _build_frame_build(self, first_time):
        
        # create build frame
        self.frames["build"] = tk.Frame(master=self.window)
        
        # label
        self.labels["build"] = tk.Label(master=self.frames["build"], text="Build")
        
        if first_time:
            self.buttons["build_all"] = FunctionButton("Build all", self.functions.build_origins_first_time, master=self.frames["build"])

        else:
            self.buttons["build_all"] = FunctionButton("Build all", self.functions.build_origins, master=self.frames["build"])
        
            for ori in self.origins:
                ori_short = ori.split("/")[-1]
                self.buttons["build_" + ori_short] = FunctionButton(ori_short, partial(self.functions.build_origin, ori), master=self.frames["build"])
            
        # put everything on a grid
        columnspan = len(self.origins)
        self.labels["build"].grid(row=0, columnspan=columnspan)
        self.buttons["build_all"].grid(row=1, columnspan=columnspan)
        
        if not first_time:
            for c, ori in enumerate(self.origins):
                ori_short = ori.split("/")[-1]
                self.buttons["build_" + ori_short].grid(row=2, column=c)
        
        self.frames["build"].pack(padx='5', pady='5')        
        
        if first_time:
            self.texts["monitor"].pack()
        
        
    def _build_frame_setups(self, first_time):
        
        # create build frame
        self.frames["setups"] = tk.Frame(master=self.window)
        
        # title label
        self.labels["setups"] = tk.Label(master=self.frames["setups"], text="Setups")

        for setup in self.setups.keys():
            self.buttons["set_" + setup] = SetButton(setup, partial(self.functions.set_setup, setup), master=self.frames["setups"])
            
        self.labels["current_setups"] = tk.Label(text="Current setups", master=self.frames["setups"])
        self.entries["current_setups"] = tk.Entry(master=self.frames["setups"])        
        self.buttons["clear_setups"] = FunctionButton("Clear setups", self.functions.clear_setups, master=self.frames["setups"])
        
        if first_time:
            self.buttons["deploy_setups"] = FunctionButton("Deploy setups", self.functions.deploy_setups_first_time, master=self.frames["setups"])
        else:
            self.buttons["deploy_setups"] = FunctionButton("Deploy setups", self.functions.deploy_setups, master=self.frames["setups"])
            
        # put everything on a grid
        columnspan = len(self.setups)

        self.labels["setups"].grid(row=0, columnspan=columnspan)
        
        for c, setup in enumerate(self.setups.keys()):
            self.buttons["set_" + setup].grid(row=1, column=c)
            
        self.labels["current_setups"].grid(row=2, columnspan=columnspan)
        self.entries["current_setups"].grid(row=3, columnspan=columnspan)
        self.buttons["clear_setups"].grid(row=4, columnspan=columnspan)
        self.buttons["deploy_setups"].grid(row=5, columnspan=columnspan)
        
        self.frames["setups"].pack(padx='5', pady='5')
        
        if first_time:
            self.texts["monitor"].pack()
        
    def _build_window(self):
        
        self._build_frame_destinations()
        self._build_frame_build(False)
        self._build_frame_setups(False)
        
        self.labels["run"] = tk.Label(text="Run the model")
        self.labels["run"].pack()
        
        self.buttons["run"] = FunctionButton("Run", self.functions.run)
        self.buttons["run"].pack()
        
        self.texts["monitor"].pack()
        
        