# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 10:26:50 2021

@author: Sven
"""

from iow_esm_globals import *
from iow_esm_error_handler import *
from iow_esm_functions import *

import tkinter.ttk as ttk

class FunctionButton(tk.Button):
    def __init__(self, text, command, master=None):
        tk.Button.__init__(self,
            master=master,
            text=text,
            bg=IowColors.green1,
            fg="black",#IowColors.grey1,
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
    def __init__(self, text, master=None, bg=""):
        
        if master is not None and bg == "":
            bg=master["background"]
            
        tk.Label.__init__(self,
            master=master,
            text=text, 
            bg = bg, 
            fg = 'white'
        )
        self.config(font=("Meat Plus", 20))
        
        
class Frame(tk.Frame):
    def __init__(self, master=None, bg=IowColors.blue1):
        tk.Frame.__init__(self,
            master=master,
            bg = bg,
            #width = 400,
            #height = 200
        )


class IowEsmGui:
    def __init__(self):
        self.window = tk.Tk(className="IOW_ESM")
        self.window.configure(background=IowColors.blue1)
        #self.window.geometry("500x900")
        
        self.labels = {}
        self.entries = {}
        self.buttons = {}
        self.texts = {}
        self.frames = {}
        self.messages = {}
        self.windows = {}
        
        self.restart = False
        
        self.error_handler = IowEsmErrorHandler(self)
        self.functions = IowEsmFunctions(self)
        
        self.row = 0
        
        self._build_frame_greeting()
        
        self._build_window_monitor()
        
        self.print("Last error log:")
        self.print(self.error_handler.get_log())
        
        if not self._check_origins() or self.error_handler.check_for_error(*IowEsmErrors.clone_origins):

            cmd = "find . -name \"*.sh\" -exec chmod u+x {} \\;"
            os.system(cmd)
            self._build_window_clone_origins()
            return
        
        if not self._check_destinations():
            self._build_window_edit_destinations()
            return
        
        self.current_destination = ""
        self.current_build_conf = "release fast"
        
        if not self._check_last_build() or self.error_handler.check_for_error(*IowEsmErrors.build_origins_first_time):
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
        
        # everything is normal, remove old log
        self.error_handler.remove_from_log(IowEsmErrorLevels.fatal)
        self.error_handler.remove_from_log(IowEsmErrorLevels.warning)
        self.error_handler.remove_from_log(IowEsmErrorLevels.info)
        
        self._build_window()
        
    def _destroy_monitor_callback(self):
        self.monitor = False
        self.windows["monitor"].destroy()
        
    def refresh(self):
        self.window.destroy()
        self.restart = True
        
    def print(self, text):
        if not self.monitor:
            print(text)
            #self.windows["monitor"] = tk.Toplevel(self.window)
            #self.windows["monitor"].protocol("WM_DELETE_WINDOW", self._destroy_monitor_callback)
            #self.texts["monitor"] = tk.Text(master = self.windows["monitor"], bg = IowColors.blue1, fg='white')
            #self.texts["monitor"].grid(row=0)
            #self.monitor = True
            return
            
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
        self.texts["edit_" + dst_name].grid(row=self.row)
        self.row += 1
        
        self.buttons["store_" + dst_name] = FunctionButton("Store " + dst_name, partial(self.functions.store_file_from_tk_text, dst_name, self.texts["edit_" + dst_name]), master=master)
        self.buttons["store_" + dst_name].grid(row=self.row)
        self.row += 1
        
        
    def _build_frame_greeting(self):
        self.frames["greeting"] = Frame(master=self.window, bg=IowColors.blue4)
        
        self.iow_logo = tk.PhotoImage(file=root_dir + '/gui/iow_logo_small.png')
        self.labels["greeting"] = tk.Label(master=self.frames["greeting"], image=self.iow_logo, bg = IowColors.blue4)
        self.labels["greeting"].grid(sticky='w')
        
        self.frames["greeting"].grid(row=self.row, sticky='nsew')
        self.frames["greeting"].grid_columnconfigure(0, weight=1)
        self.frames["greeting"].grid_rowconfigure(0, weight=1)
        self.row += 1
        
    def _build_window_monitor(self):
        self.windows["monitor"] = tk.Toplevel(self.window)
        self.windows["monitor"].configure(background=IowColors.blue2)
        self.windows["monitor"].protocol("WM_DELETE_WINDOW", self._destroy_monitor_callback)
        self.labels["monitor"] = FrameTitleLabel("Monitor:", master = self.windows["monitor"], bg = self.windows["monitor"]["background"])
        self.texts["monitor"] = tk.Text(master = self.windows["monitor"], bg=IowColors.blue1, fg="white")
        
        row=0
        
        self.labels["monitor"].grid(row=row, sticky='w')
        row += 1
        
        self.texts["monitor"].grid(row=row)
        row += 1
        
        self.monitor = True        
        
    def _build_window_clone_origins(self):
        
        self.frames["clone_origins"] = Frame(master=self.window)
        
        self.labels["clone_origins_title"] = FrameTitleLabel(master=self.frames["clone_origins"], text="You are using the IOW_ESM for the first time.")
        self.labels["clone_origins_title"].grid(row=self.row)
        self.row += 1
        
        self.labels["clone_origins"] = tk.Label(master=self.frames["clone_origins"], text="You have to clone the origins of the components first:", bg = IowColors.blue1, fg = 'white')
        self.labels["clone_origins"].grid(row=self.row)
        self.row += 1
        
        self.buttons["clone_origins"] = FunctionButton("Clone origins", self.functions.clone_origins, master=self.frames["clone_origins"])
        self.buttons["clone_origins"].grid(row=self.row)
        self.row += 1
        
        self.frames["clone_origins"].grid(row=self.row)
        self.row += 1
        
    def _build_window_edit_destinations(self):
        
        self.frames["edit_destinations"] = Frame(master=self.window)
        
        self.labels["edit_destinations_title"] = FrameTitleLabel(master=self.frames["edit_destinations"], text="You are using the IOW_ESM for the first time.")
        self.labels["edit_destinations_title"].pack()
        self.row += 1
        
        self.labels["edit_destinations"] = tk.Label(master=self.frames["edit_destinations"],
            text="You have to edit your DESTINATIONS file:", bg = IowColors.blue1, fg = 'white'
        )
        self.labels["edit_destinations"].pack()
        self.row += 1
        
        self.frames["edit_destinations"].grid(row=self.row, sticky='nsew')
        self.row += 1
        
        self._edit_file(root_dir + "/DESTINATIONS.example", root_dir + "/DESTINATIONS")
        
    def _build_window_edit_setups(self):
        
        self.frames["edit_setups"] = Frame(master=self.window)
        
        self.labels["edit_setups_title"] = FrameTitleLabel(master=self.frames["edit_setups"], text="You are using the IOW_ESM for the first time.")
        self.labels["edit_setups_title"].grid(row=self.row)
        self.row += 1
        
        self.labels["edit_setups"] = tk.Label(master=self.frames["edit_setups"],
            text="You have to edit your SETUPS file:",  bg = IowColors.blue1, fg = 'white'
        )
        self.labels["edit_setups"].grid(row=self.row)
        self.row += 1
        
        self.frames["edit_setups"].grid(row=self.row)
        self.row += 1
        
        self._edit_file(root_dir + "/SETUPS.example", root_dir + "/SETUPS")
        
    def _build_frame_destinations(self):
        
        ttk.Separator(self.window, orient=tk.HORIZONTAL).grid(row=self.row, sticky='ew')
        self.row += 1
        
        # create destinations frame
        self.frames["destinations"] = Frame(master=self.window, bg=IowColors.blue4)
        
        # create objects of the frame
        self.labels["destinations"] = FrameTitleLabel(master=self.frames["destinations"], text="Destinations:")
        
        for dst in self.destinations.keys():
            self.buttons["set_" + dst] = SetButton(dst, partial(self.functions.set_destination, dst), master=self.frames["destinations"])
        
        self.buttons["edit_destinations"] = FunctionButton("Edit", self.functions.edit_destinations, master=self.frames["destinations"])
        
        self.labels["current_dst"] = tk.Label(text="Current destination:", master=self.frames["destinations"], bg = self.frames["destinations"]["background"], fg = 'white')
        self.entries["current_dst"] = tk.Entry(master=self.frames["destinations"])
        
        # pack everything on a grid
        max_buttons_in_row = 3
        if len(self.destinations) < max_buttons_in_row:
            columnspan = len(self.destinations) 
        else:
            columnspan = max_buttons_in_row
            
        columnspan += 1
        
        row =  0
        self.labels["destinations"].grid(row=row, columnspan=columnspan, sticky='w')
        row += 1
        
        for c, dst in enumerate(self.destinations.keys()):
            if (c % max_buttons_in_row) == 0:
                row += 1
            
            self.buttons["set_" + dst].grid(row=row, column=(c % max_buttons_in_row), sticky='we')
           
        self.buttons["edit_destinations"].grid(row=row, column=columnspan-1)
        
        row += 1
        self.labels["current_dst"].grid(row=row, columnspan=columnspan)
        
        row += 1
        self.entries["current_dst"].grid(row=row, columnspan=columnspan)
                
        row += 1
        blank = tk.Label(text="", master=self.frames["destinations"], bg = self.frames["destinations"]["background"])
        blank.grid(row=row, columnspan=columnspan)
        
        # pack the frame
        self.frames["destinations"].grid(row=self.row, sticky='nsew')
        for i in range(0, columnspan):
            self.frames["destinations"].grid_columnconfigure(i, weight=1)
        self.frames["destinations"].grid_rowconfigure(0, weight=1)
        self.row += 1
        
        ttk.Separator(self.window, orient=tk.HORIZONTAL).grid(row=self.row, sticky='ew')
        self.row += 1
        
        
    def _build_frame_build(self, first_time):
        
        # create build frame
        self.frames["build"] = Frame(master=self.window, bg=IowColors.blue3)
        
        # label
        self.labels["build"] = FrameTitleLabel(master=self.frames["build"], text="Build:")      
        if first_time:
            self.buttons["build_all"] = FunctionButton("Build all", self.functions.build_origins_first_time, master=self.frames["build"])

        else:
            self.buttons["build_all"] = FunctionButton("Build all", self.functions.build_origins, master=self.frames["build"])
        
            for ori in self.origins:
                ori_short = ori.split("/")[-1]
                self.buttons["build_" + ori_short] = FunctionButton(ori_short, partial(self.functions.build_origin, ori), master=self.frames["build"])
            
        # put everything on a grid
        columnspan = len(self.origins)
        
        row = 0
        self.labels["build"].grid(row=row, columnspan=columnspan, sticky='w')
        row += 1
        
        self.buttons["build_all"].grid(row=row, columnspan=columnspan, sticky='ew')
        row += 1
        
        if not first_time:
            for c, ori in enumerate(self.origins):
                ori_short = ori.split("/")[-1]
                self.buttons["build_" + ori_short].grid(row=row, column=c, sticky='we')
            row += 1
        
        blank = tk.Label(text="", master=self.frames["build"], bg = self.frames["build"]["background"])
        blank.grid(row=row, columnspan=columnspan)
        row += 1
        
        self.frames["build"].grid(row=self.row, sticky='nsew')
        for i in range(0, columnspan):
            self.frames["build"].grid_columnconfigure(i, weight=1)
        self.frames["build"].grid_rowconfigure(0, weight=1)
        self.row += 1  
        
        ttk.Separator(self.window, orient=tk.HORIZONTAL).grid(row=self.row, sticky='ew')
        self.row += 1
        
        
    def _build_frame_setups(self, first_time):
        
        # create build frame
        self.frames["setups"] = Frame(master=self.window, bg=IowColors.blue2)
        
        # title label
        self.labels["setups"] = FrameTitleLabel(master=self.frames["setups"], text="Setups:")

        for setup in self.setups.keys():
            self.buttons["set_" + setup] = SetButton(setup, partial(self.functions.set_setup, setup), master=self.frames["setups"])
            
        self.buttons["edit_setups"] = FunctionButton("Edit", self.functions.edit_setups, master=self.frames["setups"])
        
        self.labels["current_setups"] = tk.Label(text="Current setups:", master=self.frames["setups"], bg = self.frames["setups"]["background"], fg = 'white')
        self.entries["current_setups"] = tk.Entry(master=self.frames["setups"])     
        
        self.frames["setups_function_buttons"] = Frame(master=self.frames["setups"])
        
        self.frames["archive_setup"] = Frame(master=self.frames["setups"], bg = self.frames["setups"]["background"])
        
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

        row = 0
        
        self.labels["setups"].grid(row=row, columnspan=columnspan, sticky='w')
        row += 1
        
        for c, setup in enumerate(self.setups.keys()):
            self.buttons["set_" + setup].grid(row=row, column=c, sticky='ew')
            
        self.buttons["edit_setups"].grid(row=row, column=columnspan-1)
        row += 1
            
        self.labels["current_setups"].grid(row=row, columnspan=columnspan)
        row += 1
        
        self.entries["current_setups"].grid(row=row, columnspan=columnspan)
        row += 1
        
        blank = tk.Label(text="", master=self.frames["setups"], bg = self.frames["setups"]["background"])
        blank.grid(row=row, columnspan=columnspan)
        row += 1
        
        self.buttons["get_setups_info"].grid(row=0, column=0, sticky='ew')
        self.buttons["clear_setups"].grid(row=0, column=1, sticky='ew')
        self.buttons["deploy_setups"].grid(row=0, column=2, sticky='ew')
        
        self.frames["setups_function_buttons"].grid(row=row, columnspan=columnspan, sticky='ew')
        self.frames["setups_function_buttons"].grid_rowconfigure(0, weight=1)
        self.frames["setups_function_buttons"].grid_columnconfigure(0, weight=1)
        self.frames["setups_function_buttons"].grid_columnconfigure(1, weight=1)
        self.frames["setups_function_buttons"].grid_columnconfigure(2, weight=1)
        row += 1
        
        blank = tk.Label(text="", master=self.frames["setups"], bg = self.frames["setups"]["background"])
        blank.grid(row=row, columnspan=columnspan)
        row += 1
        
        if not first_time:
            
            ttk.Separator(self.frames["setups"], orient=tk.HORIZONTAL).grid(row=row, columnspan=columnspan, sticky='ew')
            row += 1
            
            blank = tk.Label(text="", master=self.frames["archive_setup"], bg = self.frames["setups"]["background"])
            blank.grid(row=0, columnspan=3)
            
            self.entries["archive_setup"].grid(row=1, column=0)
            blank = tk.Label(text="  ", master=self.frames["archive_setup"], bg = self.frames["setups"]["background"])
            blank.grid(row=1, column=1)
            self.buttons["archive_setup"].grid(row=1, column=2)
            
            blank = tk.Label(text="", master=self.frames["archive_setup"], bg = self.frames["setups"]["background"])
            blank.grid(row=2, columnspan=3)
        
            self.frames["archive_setup"].grid(row=row, columnspan=columnspan)
            row += 1
        
        self.frames["setups"].grid(row=self.row, sticky='nsew')
        for i in range(0, columnspan):
            self.frames["setups"].grid_columnconfigure(i, weight=1)
        self.frames["setups"].grid_rowconfigure(0, weight=1)
        self.row += 1
        
        ttk.Separator(self.window, orient=tk.HORIZONTAL).grid(row=self.row, sticky='ew')
        self.row += 1
            
    def _build_frame_run(self):
        
        self.frames["run"] = Frame(master=self.window, bg = IowColors.blue1)
        
        self.labels["run"] = FrameTitleLabel(master=self.frames["run"], text="Run the model:")
        self.buttons["run"] = FunctionButton("Run", self.functions.run, master=self.frames["run"])

        row = 0
        
        self.labels["run"].grid(row=row, sticky='w')
        row += 1
        
        self.buttons["run"].grid(row=row, sticky='ew')
        row += 1
        
        blank = tk.Label(text="", bg = self.frames["run"]["background"], master=self.frames["run"])
        blank.grid(row=row)
        row += 1
        
        self.frames["run"].grid(row=self.row, sticky='nsew')
        self.frames["run"].grid_columnconfigure(0, weight=1)
        self.frames["run"].grid_rowconfigure(0, weight=1)
        self.row += 1
        
    def _build_window(self):
        
        self._build_frame_destinations()
        
        self._build_frame_build(False)
        
        self._build_frame_setups(False)
        
        self._build_frame_run()

        
        