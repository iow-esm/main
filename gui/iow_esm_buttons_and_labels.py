# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:43:44 2021

@author: Sven
"""

from iow_esm_globals import *


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
        
class NewWindowButton(tk.Button):
    def __init__(self, text, command, master=None):
        tk.Button.__init__(self,
            master=master,
            text=text,
            command=command,
            bg = IowColors.grey4,
            fg = "black"
        )
                
class CheckButton(tk.Checkbutton):
    def __init__(self, text, variable, master=None):
        #if master is not None:
        #    bg = master["background"]
        #else:
        bg = IowColors.grey1,
        tk.Checkbutton.__init__(self,
            master=master,
            text=text,
            var=variable,
            fg = "white",
            bg = bg,
            #activebackground = bg,
            #activeforeground = "white",
            selectcolor=bg,
            #bd=5
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
        self.config(font=("Meta Plus", 20))
        
        
class Frame(tk.Frame):
    def __init__(self, master=None, bg=IowColors.blue1):
        tk.Frame.__init__(self,
            master=master,
            bg = bg,
            #width = 400,
            #height = 200
        )

    
