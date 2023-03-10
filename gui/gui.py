# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 10:26:50 2021

@author: Sven
"""

from iow_esm_globals import *
from iow_esm_error_handler import *
from iow_esm_functions import *
import postprocess_window
import tkinter.ttk as ttk

from iow_esm_buttons_and_labels import *

from iow_esm_info_texts import *

import webbrowser

class IowEsmGui:
    def __init__(self):
        self.window = tk.Tk(className="IOW_ESM")
        self.window.configure(background=IowColors.blue1)
        
        self.icon = tk.PhotoImage(file = root_dir + "/gui/icon.png")
        self.window.iconphoto(True, self.icon)
        
        self.screen_width = self.window.winfo_screenwidth() # width of the screen
        self.screen_height = self.window.winfo_screenheight() # height of the screen
        
        self.x_offset = self.screen_width / 30
        self.y_offset = 0
        
        self.window.geometry('+%d+%d' % (self.x_offset, self.y_offset))
        
        self.labels = {}
        self.entries = {}
        self.buttons = {}
        self.texts = {}
        self.frames = {}
        self.messages = {}
        self.windows = {}
        self.menus = {}
        
        self.restart = False
        
        self.prepare_before_run = tk.IntVar(value=0)
        
        self.error_handler = IowEsmErrorHandler(self)
        self.functions = IowEsmFunctions(self)
        
        self.row = 0
        
        self._build_frame_greeting()
        
        self._build_window_monitor()
        
        self.print("Last error log:")
        self.print(self.error_handler.get_log())
        
        if not self._check_origins() or self.error_handler.check_for_error(*IowEsmErrors.clone_origins):
            
            self._build_window_clone_origins()
        
            # place monitor after everything is built up
            self.windows["monitor"].geometry('+%d+%d' % (self.window.winfo_width() + self.x_offset * (1.1), self.y_offset))

            return
        
        if not self._check_destinations():
            self._build_window_edit_destinations()
            
            # place monitor after everything is built up
            self.windows["monitor"].geometry('+%d+%d' % (self.window.winfo_width() + self.x_offset * (1.1), self.y_offset))

            return
        
        self.current_destination = ""
        self.current_sync_destination = ""
        self.current_build_conf = "release fast"
        
        if not self._check_last_build() or self.error_handler.check_for_error(*IowEsmErrors.build_origins_first_time):
            self._build_frame_destinations()
            self._build_frame_build(True)
            
            # place monitor after everything is built up
            self.windows["monitor"].geometry('+%d+%d' % (self.window.winfo_width() + self.x_offset * (1.1), self.y_offset))

            return
        
        self.current_setups = []

        self.available_inputs = []
        
        if not self._check_setups():
            self._build_window_edit_setups()
            
            # place monitor after everything is built up
            self.windows["monitor"].geometry('+%d+%d' % (self.window.winfo_width() + self.x_offset * (1.1), self.y_offset))

            return
        
        if not self._check_last_deployed_setups() or self.error_handler.check_for_error(*IowEsmErrors.deploy_setups_first_time):
            self._build_frame_destinations()
            self._build_frame_setups(True)
            
            # place monitor after everything is built up
            self.windows["monitor"].geometry('+%d+%d' % (self.window.winfo_width() + self.x_offset * (1.1), self.y_offset))

            return
        
        # everything is normal, remove old log
        self.error_handler.remove_from_log(IowEsmErrorLevels.fatal)
        self.error_handler.remove_from_log(IowEsmErrorLevels.warning)
        self.error_handler.remove_from_log(IowEsmErrorLevels.info)
        
        self._build_window()
        
        self.window.attributes('-topmost', 1)
        self.window.attributes('-topmost', 0)
        self.window.update_idletasks()
        
        # place monitor after everything is built up
        self.windows["monitor"].geometry('+%d+%d' % (self.window.winfo_width() * (1.01) + self.x_offset , self.y_offset))
        
    def _destroy_monitor_callback(self):
        self.monitor = False
        self.windows["monitor"].destroy()
        
    def refresh(self):
        self.window.destroy()
        self.restart = True
        
    def print(self, text):
        
        if not self.monitor:
            print(text)
            return
        
        self.windows["monitor"].attributes('-topmost', 1)
        self.windows["monitor"].attributes('-topmost', 0)
        
        self.texts["monitor"].insert(tk.END, str(text) + "\n")
        self.texts["monitor"].see(tk.END)
        self.window.update_idletasks()
        
    def _check_origins(self):
        self.origins = []
        try:
            available_origins = read_iow_esm_configuration(root_dir + "/ORIGINS").keys()
        except:
            self.print("There is no ORIGINS file. Abort.")
            exit()
        
        for ori in available_origins:
            if os.path.isdir(root_dir + "/" + ori + "/.git"):
                if glob.glob(root_dir + "/" + ori + "/build.sh") == []:
                    continue
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
        self.frames["greeting"] = Frame(master=self.window, bg=IowColors.blue4, tip_text = r"https://git.io-warnemuende.de/iow_esm/main")
        
        self.iow_logo = tk.PhotoImage(file=root_dir + '/gui/iow_logo_small.png')
        
        self.buttons["greeting"] = FunctionButton(master = self.frames["greeting"], text=None, image = self.iow_logo, bg = IowColors.blue4, command = partial(webbrowser.open_new, r"https://git.io-warnemuende.de/iow_esm/main"))
        self.buttons["greeting"].grid(sticky='w')
        
        self.frames["greeting"].grid(row=self.row, sticky='nsew')
        self.frames["greeting"].grid_columnconfigure(0, weight=1)
        self.frames["greeting"].grid_rowconfigure(0, weight=1)
        self.row += 1
        
    def _build_window_monitor(self):
        self.windows["monitor"] = tk.Toplevel(self.window)
        self.windows["monitor"].title('Monitor')
        self.windows["monitor"].configure(background=IowColors.blue3)
        self.windows["monitor"].protocol("WM_DELETE_WINDOW", self._destroy_monitor_callback)
        
        
        
        self.labels["monitor"] = FrameTitleLabel("Monitor:", master = self.windows["monitor"], bg = self.windows["monitor"]["background"])
        self.texts["monitor"] = tk.Text(master = self.windows["monitor"], 
                                        bg=IowColors.blue1, 
                                        fg="white", 
                                        width=self.screen_width // 15, 
                                        height=self.screen_height // 30)
        
        row=0
        
        self.labels["monitor"].grid(row=row, sticky='w')
        row += 1
        
        self.texts["monitor"].grid(row=row)
        row += 1
        
        self.monitor = True        
        
    def _build_window_clone_origins(self):
        
        self.frames["clone_origins"] = Frame(master=self.window, bg=IowColors.blue3)
        
        self.labels["clone_origins_title"] = FrameTitleLabel(master=self.frames["clone_origins"], text="Hello!")

        self.labels["clone_origins"] = tk.Label(master=self.frames["clone_origins"], text="You have to clone the origins of the components first:", bg = self.frames["clone_origins"]["background"], fg = 'white')

        self.buttons["clone_origins"] = FunctionButton("Clone all origins", self.functions.clone_origins, master=self.frames["clone_origins"])
        
        self.buttons["clone_origins_advanced"] = NewWindowButton("Advanced", self._build_window_clone_origins_advanced, master=self.frames["clone_origins"])

        
        ttk.Separator(master=self.window, orient=tk.HORIZONTAL).grid(row=self.row, sticky='ew')
        self.row += 1
        
        row = 0
        self.labels["clone_origins_title"].grid(row=row, sticky='w')
        row += 1
        
        self.labels["clone_origins"].grid(row=row, sticky='w')
        row += 1
        
        self.buttons["clone_origins"].grid(row=row, sticky='ew')
        row += 1
        
        self.buttons["clone_origins_advanced"].grid(row=row, sticky='ew')
        row += 1
        
        self.frames["clone_origins"].grid(row=self.row, sticky='nsew')
        self.frames["clone_origins"].grid_rowconfigure(0, weight=1)
        self.frames["clone_origins"].grid_columnconfigure(0, weight=1)
        self.row += 1

        self.print(IowEsmInfoTexts.clone_origins)
        
    def _build_frame_clone_origin(self):
        
        self.frames["clone_origin"] = Frame(master=self.windows["clone_origins_advanced"], bg=IowColors.blue2)
        
        self.labels["clone_origin_title"] = FrameTitleLabel("Clone individual origins:", self.frames["clone_origin"])
        
        self.labels["clone_origin"] = tk.Label(master=self.frames["clone_origin"], text="You can also clone the origins of individual components:", bg = self.frames["clone_origin"]["background"], fg = 'white')
        
        origins = read_iow_esm_configuration(root_dir + '/ORIGINS').keys()
        
        for origin in origins:
            self.buttons["clone_" + origin] = FunctionButton(origin, partial(self.functions.clone_origin, origin), master=self.frames["clone_origin"])        
        

        self.labels["continue"] = tk.Label(master=self.frames["clone_origin"], text="Continue, when you have everything you need:", bg = self.frames["clone_origin"]["background"], fg = 'white')
        
        self.buttons["continue"] = FunctionButton("Continue", self.refresh, master=self.frames["clone_origin"])

        row = 0
        
        max_buttons_in_row = 3
        if len(origins) < max_buttons_in_row:
            columnspan = len(origins) 
        else:
            columnspan = max_buttons_in_row
            
        self.labels["clone_origin_title"].grid(row=row, columnspan=columnspan, sticky='w')
        row += 1
        
        self.labels["clone_origin"].grid(row=row, columnspan=columnspan, sticky='w')
        row += 1
        
        for c, origin in enumerate(origins):
            if (c % max_buttons_in_row) == 0:
                row += 1
            self.buttons["clone_" + origin].grid(row=row, column=(c % max_buttons_in_row), sticky='ew')
        row += 1
        
        blank = tk.Label(text="", master=self.frames["clone_origin"], bg = self.frames["clone_origin"]["background"])
        blank.grid(row=row, columnspan=columnspan)
        row += 1
        
        self.labels["continue"].grid(row=row, columnspan=columnspan, sticky='w')
        row += 1
        
        self.buttons["continue"].grid(row=row, columnspan=columnspan, sticky='ew')
        row += 1
        
        self.frames["clone_origin"].grid(row=self.row, sticky='nsew')
        for i in range(0, columnspan):
            self.frames["clone_origin"].grid_columnconfigure(i, weight=1)
        self.frames["clone_origin"].grid_rowconfigure(0, weight=1)

        
    def _build_window_clone_origins_advanced(self):
        
        self.windows["clone_origins_advanced"] = tk.Toplevel(self.window)
        
        self._build_frame_clone_origin()
        
        self.windows["clone_origins_advanced"].geometry('+%d+%d' 
                                              % (self.x_offset, 
                                                 1.2*self.window.winfo_height()))
        
    def _build_window_edit_destinations(self):
        
        self.frames["edit_destinations"] = Frame(master=self.window, bg = IowColors.blue3)
        
        self.labels["edit_destinations"] = tk.Label(master=self.frames["edit_destinations"],
            text="You have to edit your DESTINATIONS file:", bg = self.frames["edit_destinations"]["background"], fg = 'white'
        )
        self.labels["edit_destinations"].grid(row=self.row, sticky = 'w')
        self.row += 1
        
        self.frames["edit_destinations"].grid(row=self.row, sticky='nsew')
        self.row += 1
        
        self._edit_file(root_dir + "/DESTINATIONS.example", root_dir + "/DESTINATIONS")
        
        self.print(IowEsmInfoTexts.edit_destinations)
        
    def _build_window_edit_setups(self):
        
        self.frames["edit_setups"] = Frame(master=self.window, bg = IowColors.blue3)
        
        self.labels["edit_setups"] = tk.Label(master=self.frames["edit_setups"],
            text="You have to edit your SETUPS file:",  bg = self.frames["edit_setups"]["background"], fg = 'white'
        )
        self.labels["edit_setups"].grid(row=self.row, sticky = 'w')
        self.row += 1
        
        self.frames["edit_setups"].grid(row=self.row, sticky='nsew')
        self.row += 1
        
        self._edit_file(root_dir + "/SETUPS.example", root_dir + "/SETUPS")
        
        self.print(IowEsmInfoTexts.edit_setups) 
        
    def _build_frame_destinations(self):
        
        ttk.Separator(self.window, orient=tk.HORIZONTAL).grid(row=self.row, sticky='ew')
        self.row += 1
        
        # create destinations frame
        self.frames["destinations"] = Frame(master=self.window, bg = IowColors.blue4)
        
        # create objects of the frame
        self.labels["destinations"] = FrameTitleLabel(master=self.frames["destinations"], text="Destinations:")
        
        self.menus["destinations"] = DropdownMenu(master=self.frames["destinations"], entries=[""] + list(self.destinations.keys()), function=self.functions.set_destination,
                                                tip_text="Choose one of the target configured in your DESTINATIONS file.")
        
        self.buttons["edit_destinations"] = NewWindowButton("Edit", self.functions.edit_destinations, master=self.frames["destinations"])
        
        # pack everything on a grid
        row =  0
        columnspan = 2
        
        self.labels["destinations"].grid(row=row, columnspan=columnspan, sticky='w')
        row += 1
        
        self.buttons["edit_destinations"].grid(row=row, column=columnspan-1)
        
        self.menus["destinations"].grid(row=row, column=0, sticky='ew')
                
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
        self.frames["build"] = Frame(master=self.window,  bg = IowColors.blue4)
        
        # label
        self.labels["build"] = FrameTitleLabel(master=self.frames["build"], text="Build:")      
        
        if first_time:
            self.buttons["build_all"] = FunctionButton("Build all", self.functions.build_origins_first_time, master=self.frames["build"])
            
            self.labels["build_continue"] = tk.Label(master=self.frames["build"], text="Continue, when build was successful", bg = self.frames["build"]["background"], fg = 'white')
            self.buttons["build_continue"] = FunctionButton("Continue", self.refresh, master=self.frames["build"])
        else:
            self.buttons["build_all"] = FunctionButton("Build all", self.functions.build_origins, master=self.frames["build"])
        
            for ori in self.origins:
                ori_short = ori.split("/")[-1]
                self.buttons["build_" + ori_short] = FunctionButton(ori_short, partial(self.functions.build_origin, ori), master=self.frames["build"])
            
            self.labels["build_configs"] = tk.Label(text="Build configurations:", master=self.frames["build"], bg = self.frames["build"]["background"], fg = 'black')
            
            build_modes = ["release", "debug", "fast", "rebuild"]
            
            self.menus["build_modes1"] = DropdownMenu(master=self.frames["build"], entries=build_modes[:2], function=self.functions.set_build_config)
            self.menus["build_modes2"] = DropdownMenu(master=self.frames["build"], entries=build_modes[2:], function=self.functions.set_build_config)
        
        # put everything on a grid
        
        if first_time:
            columnspan = len(self.origins)
        else:
            columnspan = max(len(self.origins), len(build_modes))
            
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
        
            self.labels["build_configs"].grid(row=row, column=0, sticky='w')
            row += 1
            
            self.menus["build_modes1"].grid(row=row, column=0, sticky='ew')
            self.menus["build_modes2"].grid(row=row, column=1, sticky='ew')
            row += 1
            
            blank = tk.Label(text="", master=self.frames["build"], bg = self.frames["build"]["background"])
            blank.grid(row=row, columnspan=columnspan)
            row += 1
        
        else:
            self.labels["build_continue"].grid(row=row, columnspan=columnspan, sticky='w')
            row += 1
        
            self.buttons["build_continue"].grid(row=row, columnspan=columnspan, sticky='ew')
            row += 1
            
            self.print(IowEsmInfoTexts.first_build)         
        
        self.frames["build"].grid(row=self.row, sticky='nsew')
        for i in range(0, columnspan):
            self.frames["build"].grid_columnconfigure(i, weight=1)
        self.frames["build"].grid_rowconfigure(0, weight=1)
        self.row += 1  

        ttk.Separator(self.window, orient=tk.HORIZONTAL).grid(row=self.row, sticky='ew')
        self.row += 1


        
    def _build_window_setups_advanced(self):
        self.windows["setups_advanced"] = tk.Toplevel(self.window)
        
        self._build_frame_archive_setup()
        
        self.windows["setups_advanced"].geometry('+%d+%d' % (1.1*self.window.winfo_width() + self.x_offset, 1.1*self.windows["monitor"].winfo_height()))
     
    def _build_frame_archive_setup(self):
        
        self.frames["archive_setup"] = Frame(master=self.windows["setups_advanced"], bg = self.frames["setups"]["background"])
  
        self.labels["archive_setup_title"] = FrameTitleLabel("Archive setup:", self.frames["archive_setup"])
        self.labels["archive_setup"] = tk.Label(text="You can archive the setup from your current destination:", master=self.frames["archive_setup"], bg = self.frames["archive_setup"]["background"], fg = 'white')

        self.entries["archive_setup"] = tk.Entry(master=self.frames["archive_setup"]) 
        self.buttons["archive_setup"] = FunctionButton("Archive setup", self.functions.archive_setup, self.frames["archive_setup"] )

        row=0
        
        self.labels["archive_setup_title"].grid(row=row, columnspan=3, sticky = 'w')
        row += 1
        
        self.labels["archive_setup"].grid(row=row, columnspan=3, sticky = 'w')
        row += 1
        
        self.entries["archive_setup"].grid(row=row, column=0)

        blank = tk.Label(text="  ", master=self.frames["archive_setup"], bg = self.frames["setups"]["background"])
        blank.grid(row=row, column=1)

        self.buttons["archive_setup"].grid(row=row, column=2)
        row += 1
        
        blank = tk.Label(text="", master=self.frames["archive_setup"], bg = self.frames["setups"]["background"])
        blank.grid(row=row, columnspan=3)
    
        self.frames["archive_setup"].grid(sticky='nesw')
        
    def _build_frame_setups(self, first_time):
        
        # create build frame
        if  first_time:
            self.frames["setups"] = Frame(master=self.window, bg = IowColors.blue4)
        else:
            self.frames["setups"] = Frame(master=self.windows["setups"], bg = IowColors.blue4)
            
        
        # title label
        self.labels["setups"] = FrameTitleLabel(master=self.frames["setups"], text="Setups:")
        
        self.menus["setups"] = DropdownMenu(master=self.frames["setups"], entries=[""] + list(self.setups.keys()), function=self.functions.set_setup)
            
        self.buttons["edit_setups"] = NewWindowButton("Edit", self.functions.edit_setups, master=self.frames["setups"])
        
        self.labels["current_setups"] = tk.Label(text="Current setups:", master=self.frames["setups"], bg = self.frames["setups"]["background"], fg = 'black')
        self.entries["current_setups"] = tk.Entry(master=self.frames["setups"])     
        
        self.frames["setups_function_buttons"] = Frame(master=self.frames["setups"])
        
        self.buttons["get_setups_info"] = FunctionButton("Get setups info", self.functions.get_setups_info, self.frames["setups_function_buttons"] )
        
        if first_time:
            self.buttons["deploy_setups"] = FunctionButton("Deploy setups", self.functions.deploy_setups_first_time, self.frames["setups_function_buttons"] )
            self.labels["setups_continue"] = tk.Label(master=self.frames["setups"], text="Continue, when deploying was successful", bg = self.frames["setups"]["background"], fg = 'white')
            self.buttons["setups_continue"] = FunctionButton("Continue", self.refresh, master=self.frames["setups"])
            
        else:
            self.buttons["deploy_setups"] = FunctionButton("Deploy setups", self.functions.deploy_setups, self.frames["setups_function_buttons"])
            self.buttons["setups_advanced"] = NewWindowButton("Advanced", self._build_window_setups_advanced, self.frames["setups"] )
        
        # put everything on a grid

        row = 0
        columnspan = 2
        
        self.labels["setups"].grid(row=row, columnspan=columnspan, sticky='w')
        row += 1
            
        self.menus["setups"].grid(row=row, column=0, sticky='ew')
            
        self.buttons["edit_setups"].grid(row=row, column=columnspan-1)
        row += 1
            
        self.labels["current_setups"].grid(row=row, columnspan=columnspan)
        row += 1
        
        self.entries["current_setups"].grid(row=row, columnspan=columnspan, sticky="ew")
        row += 1
        
        blank = tk.Label(text="", master=self.frames["setups"], bg = self.frames["setups"]["background"])
        blank.grid(row=row, columnspan=columnspan)
        row += 1
        
        self.buttons["get_setups_info"].grid(row=0, column=0, sticky='ew')
        self.buttons["deploy_setups"].grid(row=0, column=1, sticky='ew')
        
        self.frames["setups_function_buttons"].grid(row=row, columnspan=columnspan, sticky='ew')
        self.frames["setups_function_buttons"].grid_rowconfigure(0, weight=1)
        self.frames["setups_function_buttons"].grid_columnconfigure(0, weight=1)
        self.frames["setups_function_buttons"].grid_columnconfigure(1, weight=1)
        row += 1
        
        if not first_time:
            self.buttons["setups_advanced"].grid(row=row, columnspan=columnspan, sticky='ew')
            row += 1
            
            blank = tk.Label(text="", master=self.frames["setups"], bg = self.frames["setups"]["background"])
            blank.grid(row=row, columnspan=columnspan)
            row += 1
        else:
            self.labels["setups_continue"].grid(row=row, columnspan=columnspan, sticky='w')
            row += 1
        
            self.buttons["setups_continue"].grid(row=row, columnspan=columnspan, sticky='ew')
            row += 1
            
            self.print(IowEsmInfoTexts.first_deploy_setups) 
        
        self.frames["setups"].grid(row=self.row, sticky='nsew')
        for i in range(0, columnspan):
            self.frames["setups"].grid_columnconfigure(i, weight=1)
        self.frames["setups"].grid_rowconfigure(0, weight=1)
        self.row += 1
        
        ttk.Separator(self.window, orient=tk.HORIZONTAL).grid(row=self.row, sticky='ew')
        self.row += 1

    def _build_window_setups(self):
        self.windows["setups"] = tk.Toplevel(self.window)
        
        self._build_frame_setups(False)
        
        self.windows["setups"].geometry('+%d+%d' % (1.1*self.window.winfo_width() + self.x_offset, 1.1*self.windows["monitor"].winfo_height()))

    def update_function(self):
        print("abc")
        self.menus["inputs"]["values"] = self.available_inputs
            
    def _build_frame_run(self):
        
        self.frames["run"] = Frame(master=self.window, bg = IowColors.blue4)
        
        self.labels["run"] = FrameTitleLabel(master=self.frames["run"], text="Run the model:")

        self.buttons["prepare_before_run"] = CheckButton("Create mappings", self.prepare_before_run, master=self.frames["run"])
        self.labels["sync_destinations"] = tk.Label(master=self.frames["run"], text="Synchronize to:", bg = self.frames["run"]["background"], fg = 'black')
        self.menus["sync_destinations"] = DropdownMenu(master=self.frames["run"], entries=[""] + list(self.destinations.keys()), function=self.functions.set_sync_destination)
        self.buttons["sync_now"] = FunctionButton("Synchronize now", self.functions.sync_now, master=self.frames["run"], tip_text="This will start a synchronization from the current run target to the current sync target.")
        
        def update_available_inputs(obj):
            if set(obj.entries) == set(self.available_inputs):
                return False
            obj.entries = self.available_inputs
            return True
        
        self.labels["running"] = tk.Label(master=self.frames["run"], text="Run:", bg = self.frames["run"]["background"], fg = 'black')
        self.menus["inputs"] = MultipleChoice(master=self.frames["run"], entries=self.available_inputs, text="Choose input folders...", update_entries=update_available_inputs, 
        tip_text="You can choose multiple input folder or a single one.")

        self.buttons["run"] = FunctionButton("Run", self.functions.run, master=self.frames["run"])

        self.labels["postprocess"] = tk.Label(master=self.frames["run"], text="Postprocess:", bg = self.frames["run"]["background"], fg = 'black')
        self.buttons["postprocess"] = NewWindowButton("Postprocess", partial(postprocess_window.PostprocessWindow, self), master=self.frames["run"])
        
        row = 0
        
        self.labels["run"].grid(row=row, sticky='w')
        row += 1
        
        self.buttons["prepare_before_run"].grid(row=row, sticky="ew")
        row += 1

        self.labels["sync_destinations"].grid(row=row, sticky="w")
        row += 1

        self.menus["sync_destinations"].grid(row=row, sticky="ew")
        row += 1

        self.buttons["sync_now"].grid(row=row, sticky="ew")
        row += 1

        self.labels["running"].grid(row=row, sticky="w")
        row += 1

        self.menus["inputs"].grid(row=row, sticky="ew")
        row += 1
        
        self.buttons["run"].grid(row=row, sticky='ew')
        row += 1
        
        if glob.glob(root_dir + "/postprocess") != []:
            self.labels["postprocess"].grid(row=row, sticky="w")
            row += 1
            
            self.buttons["postprocess"].grid(row=row, sticky='ew')
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
        
        self.buttons["setups"] = NewWindowButton("Deploy setups", self._build_window_setups, self.window)
        self.buttons["setups"].grid(row=self.row, sticky='ew')
        self.row += 1
        
        self._build_frame_run()
        
        self.buttons["cancel"] = CancelButton("Cancel", self.functions.cancel_shell_cmd, master=self.window)
        self.buttons["cancel"].grid(row=self.row, sticky='ew')
        self.row += 1
        


        
        