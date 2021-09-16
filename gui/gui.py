# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 10:26:50 2021

@author: Sven
"""

import tkinter as tk
import os
import glob
from functools import partial
import subprocess
import json

root_dir = "."

class IowColors:
    blue1 = "#0a2b5a"
    green1 = "#74e40d"
    grey1 = "#4e584e"

class IowEsmErrorHandler():
    def __init__(self, gui):
        self.gui = gui
        
        self.levels = {
            "fatal" : 0,
            "warning" : 1,
            "info" : 2
            }
        
        self.errors = {}
        for level in self.levels.keys():
            self.errors[level] = []
            
        self.log_file = root_dir + "/gui_error.log"
        
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

class IowEsmFunctions:
    def __init__(self, gui):
        self.gui = gui
                
    def clone_origins(self):
        cmd = root_dir + "/clone_origins.sh"
        self.gui.print(cmd)
        os.system(cmd)
        
        for ori in read_iow_esm_configuration(root_dir + '/ORIGINS').keys():
            if glob.glob(root_dir + "/" + ori + "/.git") == []:
                self.gui.error_handler.report_error("fatal", "Not all origins could be cloned!")
                self.gui.refresh()
                return
        
        self.gui.error_handler.remove_from_log("fatal", "Not all origins could be cloned!")
            
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
        
        self.gui.print("Current destination is " + self.gui.current_destination)
        
    def build_origin(self, ori):
        if self.gui.current_destination == "":
            self.gui.print("No destination is set.")
            return False
        
        cmd = "cd " + ori + "; ./build.sh " + self.gui.current_destination + " " + self.gui.current_build_conf
        self.gui.print(cmd)
        os.system(cmd)
        
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
            self.gui.print("No destination is set.")
            return False
        
        if len(self.gui.current_setups) > 1:
            self.gui.print("More than one setup is selected. Take the last one as base.")

        archive = self.gui.entries["archive_setup"].get()
        cmd = "./archive_setups.sh " + self.gui.current_destination + " " + self.gui.current_setups[-1] + " " + archive
        self.gui.print(cmd)
        os.system(cmd)
            
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
            try:
                (key, val) = line.split()
                config[key] = val
            except:
                pass
            
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
        self.error_handler = IowEsmErrorHandler(self)
        
        self.labels["greeting"] = tk.Label(text="Welcome to the IOW_ESM GUI!", bg = IowColors.blue1, fg = 'white')
        self.labels["greeting"].pack()
        
        #img = tk.PhotoImage(file=root_dir + "/gui/logo_iow_englisch_rgb.gif")
        #self.labels["logo"] = tk.Label(image=img)
        #self.labels["logo"].pack()
        
        self.texts["monitor"] = tk.Text()
        
        self.print("Last error log:")
        self.print(self.error_handler.get_log())

        if not self._check_origins() or self.error_handler.check_for_error("fatal", "Not all origins could be cloned!"):

            cmd = "find . -name \"*.sh\" -exec chmod u+x {} \\;"
            os.system(cmd)
            self._build_window_clone_origins()
            self.texts["monitor"].pack()
            return
        
        if not self._check_destinations():
            self._build_window_edit_destinations()
            return
        
        self.current_destination = ""
        self.current_build_conf = "release fast"
        
        if not self._check_last_build():
            self._build_frame_destinations()
            self._build_frame_build(True)
            self.texts["monitor"].pack()
            return
        
        self.current_setups = []
        
        if not self._check_setups():
            self._build_window_edit_setups()
            return
        
        if not self._check_last_deployed_setups():
            self._build_frame_destinations()
            self._build_frame_setups(True)
            self.texts["monitor"].pack()
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
            if os.path.isdir(root_dir + "/" + ori + "/.git"):
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
        
    def _edit_file(self, src_name, dst_name="", master=None):
        
        if dst_name == "":
            dst_name = src_name
            
        if master == None:
            master=self.window
            
        with open(src_name, 'r') as file:
            src_content = file.read()
        file.close()
        
        self.texts["edit_" + dst_name] = tk.Text(master=master)
        self.texts["edit_" + dst_name].insert(tk.END, src_content)
        self.texts["edit_" + dst_name].pack()
        
        self.buttons["store_" + dst_name] = FunctionButton("Store " + dst_name, partial(self.functions.store_file_from_tk_text, dst_name, self.texts["edit_" + dst_name]), master=master)
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
        
    def _build_frame_destinations(self):
        
        # create destinations frame
        self.frames["destinations"] = Frame(master=self.window)
        
        # create objects of the frame
        self.labels["destinations"] = FrameTitleLabel(master=self.frames["destinations"], text="Destinations")
        
        for dst in self.destinations.keys():
            self.buttons["set_" + dst] = SetButton(dst, partial(self.functions.set_destination, dst), master=self.frames["destinations"])
        
        self.buttons["edit_destinations"] = FunctionButton("Edit", self.functions.edit_destinations, master=self.frames["destinations"])
        
        self.labels["current_dst"] = tk.Label(text="Current destination:", master=self.frames["destinations"], bg = IowColors.blue1, fg = 'white')
        self.entries["current_dst"] = tk.Entry(master=self.frames["destinations"])
        
        # pack everything on a grid
        max_buttons_in_row = 6
        if len(self.destinations) < max_buttons_in_row:
            columnspan = len(self.destinations) 
        else:
            columnspan = max_buttons_in_row
            
        columnspan += 1
        
        row = 0
        self.labels["destinations"].grid(row=0, columnspan=columnspan)
        
        row += 1
        for c, dst in enumerate(self.destinations.keys()):
            if (c % max_buttons_in_row) == 0:
                row += 1
            self.buttons["set_" + dst].grid(row=row, column=(c % max_buttons_in_row))
           
        self.buttons["edit_destinations"].grid(row=row, column=columnspan-1)
        
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
            
        self.buttons["edit_setups"] = FunctionButton("Edit", self.functions.edit_setups, master=self.frames["setups"])
        
        self.labels["current_setups"] = tk.Label(text="Current setups:", master=self.frames["setups"], bg = IowColors.blue1, fg = 'white')
        self.entries["current_setups"] = tk.Entry(master=self.frames["setups"])     
        
        self.frames["setups_function_buttons"] = Frame(master=self.frames["setups"])
        
        self.frames["archive_setup"] = Frame(master=self.frames["setups"])
        
        self.buttons["get_setups_info"] = FunctionButton("Get setups info", self.functions.get_setups_info, self.frames["setups_function_buttons"] )
        self.buttons["clear_setups"] = FunctionButton("Clear setups", self.functions.clear_setups, self.frames["setups_function_buttons"] )
        
        if first_time:
            self.buttons["deploy_setups"] = FunctionButton("Deploy setups", self.functions.deploy_setups_first_time, self.frames["setups_function_buttons"] )
        else:
            self.buttons["deploy_setups"] = FunctionButton("Deploy setups", self.functions.deploy_setups, self.frames["setups_function_buttons"])
         
        if not first_time:
            self.entries["archive_setup"] = tk.Entry(master=self.frames["archive_setup"]) 
            self.buttons["archive_setup"] = FunctionButton("Archive setup", self.functions.archive_setup, self.frames["archive_setup"] )
        
        # put everything on a grid
        columnspan = len(self.setups) + 1

        self.labels["setups"].grid(row=0, columnspan=columnspan)
        
        for c, setup in enumerate(self.setups.keys()):
            self.buttons["set_" + setup].grid(row=1, column=c)
            
        self.buttons["edit_setups"].grid(row=1, column=columnspan-1)
            
        self.labels["current_setups"].grid(row=2, columnspan=columnspan)
        self.entries["current_setups"].grid(row=3, columnspan=columnspan)
        
        self.buttons["get_setups_info"].grid(row=0, column=0)
        self.buttons["clear_setups"].grid(row=0, column=1)
        self.buttons["deploy_setups"].grid(row=0, column=2)
        
        self.frames["setups_function_buttons"].grid(row=4, rowspan=1, columnspan=columnspan)
        
        if not first_time:
            blank = tk.Label(text="", master=self.frames["archive_setup"], bg = IowColors.blue1)
            blank.grid(row=0, columnspan=3)
            
            self.entries["archive_setup"].grid(row=1, column=0)
            blank = tk.Label(text="  ", master=self.frames["archive_setup"], bg = IowColors.blue1)
            blank.grid(row=1, column=1)
            self.buttons["archive_setup"].grid(row=1, column=2)
            
            blank = tk.Label(text="  ", master=self.frames["archive_setup"], bg = IowColors.blue1)
            blank.grid(row=2, columnspan=3)
        
            self.frames["archive_setup"].grid(row=6, rowspan=3, columnspan=columnspan)
        
        self.frames["setups"].pack(padx='5', pady='5')
            
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
        
        