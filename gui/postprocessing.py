# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:43:44 2021

@author: Sven
"""
from iow_esm_globals import *
from iow_esm_buttons_and_labels import *

class PostprocessingWindow():
    
    def __init__(self, master):
        
        self.master = master
        
        self.window = tk.Toplevel(self.master.window)
        
        self.labels = {}
        self.buttons = {}
        
        self.nframes = 0
        
        # get all directories in the postprocess directory
        posts = [post.replace("\\", "/").split("/")[-1] for post in glob.glob(root_dir + "/postprocess/*")]
        
        # get all available origins
        oris = [ori.split("/")[-1] for ori in self.master.origins]
    
        # find origins with supported postprocessing and create a frame
        for post in posts:
            if post in oris:
                self.build_model_frame(post)
        
        #master.windows["postprocessing"].geometry('+%d+%d' 
                                              #% (master.x_offset, 
                                              #   1.2*master.window.winfo_height()))
    
    def build_model_frame(self, model):
        self.nframes += 1
        self.labels[model] = FrameTitleLabel(text = model, master=self.window, bg = getattr(IowColors, "blue" + str(5 - (self.nframes % 4))))
        self.labels[model].pack()
        
        tasks = [task.replace("\\", "/").split("/")[-1] for task in glob.glob(root_dir + "/postprocess/" + model + "/*")]
        for task in tasks:
            self.buttons["run_" + task] = FunctionButton(task, partial(self.run_task, task), master=self.window)
            self.buttons["run_" + task].pack()

    
    def run_task(self, task):
        print(task)