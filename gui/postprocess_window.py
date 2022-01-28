# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:43:44 2021

@author: Sven
"""
from iow_esm_globals import *
from iow_esm_buttons_and_labels import *
from check_dependencies import get_dependency_ordered_groups
import tkinter.ttk as ttk

class PostprocessWindow():
    
    def __init__(self, master):
        
        self.master = master
        
        self.window = tk.Toplevel(self.master.window)
        
        self.labels = {}
        self.buttons = {}
        self.frames = {}
        self.entries = {}
        self.menus = {}
        
        self.nframes = 0
        self.row = 0
        
        self.current_outdirs = {}
        self.current_from_dates = {}
        self.current_to_dates = {}
        
        self.run_name = ""
        self.init_date = ""
        self.final_date = ""
        self.model_domains = {}
        self.dependencies = {}
        
        self.get_global_settings()
        
        # get all directories in the postprocess directory
        posts = [post.replace("\\", "/").split("/")[-1] for post in glob.glob(root_dir + "/postprocess/*")]
        
        # get all available origins
        oris = [ori.split("/")[-1] for ori in self.master.origins]
    
        # find origins with supported postprocessing and create a frame
        for post in posts:
            if post in oris:
                self.build_postprocess_model_frame(post)
        
        self.window.geometry('+%d+%d' % (master.x_offset + 1.01*master.window.winfo_width(), 
                                         1.05*master.windows["monitor"].winfo_height()))
    
    def build_postprocess_model_frame(self, model):
        
        if self.model_domains != {}:
            if model not in self.model_domains.keys():
                return
            
        self.frames[model] = Frame(master=self.window, bg = getattr(IowColors, "blue" + str(4 - (self.nframes % 4))))
        
        self.labels[model] = FrameTitleLabel(text = model + ":", master=self.frames[model], bg = self.frames[model]["background"])
        
        tasks = [task.replace("\\", "/").split("/")[-2] for task in glob.glob(root_dir + "/postprocess/" + model + "/*/")] # list only directories!
 
        self.labels["current_outdir_" + model] = tk.Label(text = "Output directory", master=self.frames[model], bg = self.frames[model]["background"])
        self.labels["current_from_date_" + model] = tk.Label(text = "from (YYYYMMDD)", master=self.frames[model], bg = self.frames[model]["background"])
        self.labels["current_to_date_" + model] = tk.Label(text = "to (YYYYMMDD)", master=self.frames[model], bg = self.frames[model]["background"])

        
        self.entries["current_outdir_" + model] = tk.Entry(master=self.frames[model])
        
        try:
            self.entries["current_outdir_" + model].insert(0, self.run_name + "/" + model +"_" + self.model_domains[model])
        except:
            self.entries["current_outdir_" + model].insert(0, "")
        
        self.entries["current_from_date_" + model] = tk.Entry(master=self.frames[model])
        self.entries["current_from_date_" + model].insert(0, self.init_date)
        self.entries["current_to_date_" + model] = tk.Entry(master=self.frames[model])
        self.entries["current_to_date_" + model].insert(0, self.final_date)

        columnspan = 3
        row = 0
        
        self.labels[model].grid(row=row, sticky='w')
        row += 1
        
        ttk.Separator(master=self.frames[model], orient=tk.HORIZONTAL).grid(row=row, sticky='ew', columnspan=columnspan)
        row += 1
        
        
        model_task_list = []
        
        groups = get_dependency_ordered_groups(model, tasks, self.dependencies)
        for i, tasks in enumerate(groups):
            
            if len(groups) > 1:
                model_task_list.append("--------")
                
            for c, task in enumerate(tasks):
                model_task_list.append(task)
                
        row += 1
            
            
        def run_model_task(model_task):
            if "--------" == model_task:
                return
            
            self.run_task(model, model_task)
            
        self.menus[model + "_tasks"] = DropdownMenu(master=self.frames[model], entries=model_task_list, function=run_model_task, bg=IowColors.blue1, fg="white")
        self.menus[model + "_tasks"].grid(row=row, columnspan = columnspan, sticky='ew')
        row += 1
        
        self.labels["current_outdir_" + model].grid(row=row, column=0)
        self.labels["current_from_date_" + model].grid(row=row, column=1)
        self.labels["current_to_date_" + model].grid(row=row, column=2)
        row += 1
        
        self.entries["current_outdir_" + model].grid(row=row, column=0)
        self.entries["current_from_date_" + model].grid(row=row, column=1)
        self.entries["current_to_date_" + model].grid(row=row, column=2)
        row += 1
        
        self.frames[model].grid(row=self.row, sticky='nsew')
        for i in range(0, columnspan):
            self.frames[model].grid_columnconfigure(i, weight=1)
        self.frames[model].grid_rowconfigure(0, weight=1)
        self.row += 1
        
        self.nframes += 1
        

    
    def run_task(self, model, task):
        
        if self.master.current_destination == "":
            self.master.print("Destination not set.")
            return False
        
        
        self.current_outdirs[model] = self.entries["current_outdir_" + model].get()
        
        if self.current_outdirs[model] == "":
            self.master.print("Output directory not set.")
            return False
        
        self.current_from_dates[model] = self.entries["current_from_date_" + model].get()
        self.current_to_dates[model] = self.entries["current_to_date_" + model].get()
        
        if bool(self.current_from_dates[model] == "") != bool(self.current_to_dates[model] == ""): # this mimics xor: either both are defined or both are undefined
            self.master.print("Time range is not set correctly. Define either both limits or none (all is processed)")    
            return False
        
        cmd = "./postprocess.sh " + self.master.current_destination + " " + model + "/" + task + " "
        cmd  += self.current_outdirs[model]
            
        if  self.current_from_dates[model] != "" and self.current_to_dates[model] != "":
            cmd += " " + self.current_from_dates[model] + " " + self.current_to_dates[model]
        
        self.master.functions.execute_shell_cmd(cmd)
        
        return True
    
    def get_global_settings(self):
        if self.master.current_destination == "":
            return False
    
        file_content = ""
        
        user_at_host, path = self.master.destinations[self.master.current_destination].split(":")
        cmd = "ssh " + user_at_host + " \\\"if [ -f " + path +  "/input/global_settings.py ]; then cat " + path + "/input/global_settings.py; fi; \\\""
        file_content = self.master.functions.execute_shell_cmd(cmd, print=False)
                
        ldict = {"run_name" : "", "init_date" : "", "final_date" : "", "model_domains" : {}, "dependencies" : {}}
        
        try:
            exec(file_content, globals(), ldict)
            self.run_name = ldict["run_name"]
            self.init_date = ldict["init_date"]
            self.final_date = ldict["final_date"]
        except:
            pass
        
        file_content = ""
        if self.run_name != "":
            cmd = "ssh " + user_at_host + " ' echo model_domains = {}; for d in \`ls " + path + "/output/" + self.run_name + "\`; do model=\${d%_*}; dom=\${d#*_}; echo model_domains[\\\\\\\"\$model\\\\\\\"] = \\\\\\\"\$dom\\\\\\\"; done'"
            file_content = self.master.functions.execute_shell_cmd(cmd, print=False)
        
        try:
            exec(file_content, globals(), ldict)
            self.model_domains = ldict["model_domains"]
        except:
            pass
        
        cmd = "ssh " + user_at_host + " 'for c in " + path + "/postprocess/*/*/config.py; do echo \$c \`cat \$c | grep \"dependencies\"\`; done\'"
        file_content = self.master.functions.execute_shell_cmd(cmd, print=False)
        
        lines = file_content.splitlines()
        
        file_content = "dependencies = {}\n"
        for line in lines:
            try:
                line = line.split("dependencies")
                model = line[0].split("/")[-3]
                task = line[0].split("/")[-2]
                dependencies = line[1]
    
                file_content += "try:\n"
                file_content += " dependencies[\"" + model + "\"][\"" + task + "\"]" + dependencies + "\n"
                file_content += "except:\n"
                file_content += " dependencies[\"" + model + "\"]={}\n"    
                file_content += " dependencies[\"" + model + "\"][\"" + task + "\"]" + dependencies+ "\n"          
            except:
                pass
            
        try:
            exec(file_content, globals(), ldict)
            self.dependencies = ldict["dependencies"]
        except:
            pass

                
                