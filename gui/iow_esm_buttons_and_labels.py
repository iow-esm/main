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
            bg=IowColors.blue1,
            fg="white",
            command=command   
        )
        
class CancelButton(tk.Button):
    def __init__(self, text, command, master=None):
        tk.Button.__init__(self,
            master=master,
            text=text,
            bg='#ff9300',#"darkred",
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
            bg = IowColors.green2,
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
            fg = 'black'
        )
        self.config(font=("TkDefaultFont", 20))
        
        
class Frame(tk.Frame):
    def __init__(self, master=None, bg=IowColors.blue1):
        tk.Frame.__init__(self,
            master=master,
            bg = bg,
        )

 
class DropdownMenu(tk.OptionMenu):
    def __init__(self, master=None, entries=[], function=None, bg = None, fg = None):
        self.variable = tk.StringVar(master)
                
        tk.OptionMenu.__init__(self,
                               master,
                               self.variable,
                               *entries
                               )
        
        if bg is None:
            bg = IowColors.grey2
            
        self.config(bg = bg)
        self["menu"].config(bg=bg)
        
        if fg is None:
            fg = "white"
            
        self.config(fg = fg)
        self["menu"].config(fg=fg)

        self.variable.set(entries[0]) # default value
        
        def callback(*args):
            if function is not None:
                function(self.variable.get())
         
        self.variable.trace("w", callback)
