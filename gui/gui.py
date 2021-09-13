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

class IowColors:
    blue1 = "#0a2b5a"
    green1 = "#74e40d"
    grey1 = "#4e584e"

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
            bg=IowColors.green1,
            fg=IowColors.blue1,
            command=command   
        )
        
class SetButton(tk.Button):
    def __init__(self, text, command, master=None):
        tk.Button.__init__(self,
            master=master,
            text=text,
            command=command,
            bg = IowColors.grey1,
            fg = "white"
        )
        
class FrameTitleLabel(tk.Label):
    def __init__(self, text, master=None):
        tk.Label.__init__(self,
            master=master,
            text=text, 
            bg = IowColors.blue1, 
            fg = 'white'
        )
        self.config(font=("Meat Plus", 24))
        
class Frame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,
            master=master,
            bg = IowColors.blue1
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
        self.window.configure(background=IowColors.blue1)
        #self.window.geometry("500x500")
        
        self.labels = {}
        self.entries = {}
        self.buttons = {}
        self.texts = {}
        self.frames = {}
        self.messages = {}
        
        self.restart = False
        
        self.functions = IowEsmFunctions(self)
        
        self.labels["greeting"] = tk.Label(text="Welcome to the IOW_ESM GUI!", bg = IowColors.blue1, fg = 'white')
        self.labels["greeting"].pack()
        
        #img = tk.PhotoImage(file=root_dir + "/gui/logo_iow_englisch_rgb.gif")
        #self.labels["logo"] = tk.Label(image=img)
        #self.labels["logo"].pack()
        
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
        
        self.frames["clone_origins"] = Frame(master=self.window)
        
        self.labels["clone_origins_title"] = FrameTitleLabel(master=self.frames["clone_origins"], text="You are using the IOW_ESM for the first time.")
        self.labels["clone_origins_title"].pack()
        
        self.labels["clone_origins"] = tk.Label(master=self.frames["clone_origins"], text="You have to clone the origins of the components first:", bg = IowColors.blue1, fg = 'white')
        self.labels["clone_origins"].pack()
        
        self.buttons["clone_origins"] = FunctionButton("Clone origins", self.functions.clone_origins, master=self.frames["clone_origins"])
        self.buttons["clone_origins"].pack()
        
        self.frames["clone_origins"].pack()
        
        self.texts["monitor"].pack()
        
    def _build_window_edit_destinations(self):
        
        self.frames["edit_destinations"] = Frame(master=self.window)
        
        self.labels["edit_destinations_title"] = FrameTitleLabel(master=self.frames["edit_destinations"], text="You are using the IOW_ESM for the first time.")
        self.labels["edit_destinations_title"].pack()
        
        self.labels["edit_destinations"] = tk.Label(master=self.frames["edit_destinations"],
            text="You have to edit your DESTINATIONS file:", bg = IowColors.blue1, fg = 'white'
        )
        self.labels["edit_destinations"].pack()
        
        self.frames["edit_destinations"].pack()
        
        self._edit_file(root_dir + "/DESTINATIONS.example", root_dir + "/DESTINATIONS")
        
        self.texts["monitor"].pack()
        
    def _build_window_edit_setups(self):
        
        self.frames["edit_setups"] = Frame(master=self.window)
        
        self.labels["edit_setups_title"] = FrameTitleLabel(master=self.frames["edit_setups"], text="You are using the IOW_ESM for the first time.")
        self.labels["edit_setups_title"].pack()
        
        self.labels["edit_setups"] = tk.Label(master=self.frames["edit_setups"],
            text="You have to edit your SETUPS file:",  bg = IowColors.blue1, fg = 'white'
        )
        self.labels["edit_setups"].pack()
        
        self.frames["edit_setups"].pack()
        
        self._edit_file(root_dir + "/SETUPS.example", root_dir + "/SETUPS")
        
        self.texts["monitor"].pack()
        
    def _build_frame_destinations(self):
        
        # create destinations frame
        self.frames["destinations"] = Frame(master=self.window)
        
        # create objects of the frame
        self.labels["destinations"] = FrameTitleLabel(master=self.frames["destinations"], text="Destinations")
        
        for dst in self.destinations.keys():
            self.buttons["set_" + dst] = SetButton(dst, partial(self.functions.set_destination, dst), master=self.frames["destinations"])
            
        self.labels["current_dst"] = tk.Label(text="Current destination:", master=self.frames["destinations"], bg = IowColors.blue1, fg = 'white')
        self.entries["current_dst"] = tk.Entry(master=self.frames["destinations"])
        
        # pack everything on a grid
        max_buttons_in_row = 6
        if len(self.destinations) < max_buttons_in_row:
            columnspan = len(self.destinations) 
        else:
            columnspan = max_buttons_in_row
        
        row = 0
        self.labels["destinations"].grid(row=0, columnspan=columnspan)
        
        row += 1
        for c, dst in enumerate(self.destinations.keys()):
            if (c % max_buttons_in_row) == 0:
                row += 1
            self.buttons["set_" + dst].grid(row=row, column=(c % max_buttons_in_row))
           
        row += 1
        self.labels["current_dst"].grid(row=row, columnspan=columnspan)
        
        row += 1
        self.entries["current_dst"].grid(row=row, columnspan=columnspan)
        
        row += 1
        blank = tk.Label(text="", master=self.frames["destinations"], bg = IowColors.blue1)
        blank.grid(row=row, columnspan=columnspan)
        
        # pack the frame
        self.frames["destinations"].pack(padx='5', pady='5')
        
        
    def _build_frame_build(self, first_time):
        
        # create build frame
        self.frames["build"] = Frame(master=self.window)
        
        # label
        self.labels["build"] = FrameTitleLabel(master=self.frames["build"], text="Build")
        
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
        
        blank = tk.Label(text="", master=self.frames["build"], bg = IowColors.blue1)
        blank.grid(row=3, columnspan=columnspan)
        
        self.frames["build"].pack(padx='5', pady='5')        
        
        if first_time:
            self.texts["monitor"].pack()
        
        
    def _build_frame_setups(self, first_time):
        
        # create build frame
        self.frames["setups"] = Frame(master=self.window)
        
        # title label
        self.labels["setups"] = FrameTitleLabel(master=self.frames["setups"], text="Setups")

        for setup in self.setups.keys():
            self.buttons["set_" + setup] = SetButton(setup, partial(self.functions.set_setup, setup), master=self.frames["setups"])
            
        self.labels["current_setups"] = tk.Label(text="Current setups:", master=self.frames["setups"], bg = IowColors.blue1, fg = 'white')
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
        
        blank = tk.Label(text="", master=self.frames["setups"], bg = IowColors.blue1)
        blank.grid(row=6, columnspan=columnspan)
        
        self.frames["setups"].pack(padx='5', pady='5')
        
        if first_time:
            self.texts["monitor"].pack()
            
    def _build_frame_run(self):
        
        self.frames["run"] = Frame(master=self.window)
        
        self.labels["run"] = FrameTitleLabel(master=self.frames["run"], text="Run the model")
        self.buttons["run"] = FunctionButton("Run", self.functions.run, master=self.frames["run"])

        self.labels["run"].grid(row=0)
        self.buttons["run"] .grid(row=1)
        
        blank = tk.Label(text="", bg = IowColors.blue1, master=self.frames["run"])
        blank.grid(row=2)
        
        self.frames["run"].pack()
        
    def _build_window(self):
        
        self._build_frame_destinations()
        
        self._build_frame_build(False)
        
        self._build_frame_setups(False)
        
        self._build_frame_run()

    
        self.texts["monitor"].pack()
        
        