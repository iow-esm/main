# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:43:44 2021

@author: Sven
"""

from iow_esm_globals import *
from tkinter import ttk


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
            text=text+"...",
            command=command,
            bg = IowColors.green2,
            fg = "black"
        )
                
class CheckButton(tk.Checkbutton):
    def __init__(self, text, variable, master=None):
        if master is not None:
            bg = master["background"]
            fg = 'black'
        else:
            bg = IowColors.grey1
            fg = 'white'
        tk.Checkbutton.__init__(self,
            master=master,
            text=text,
            var=variable,
            fg = fg,
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
    def __init__(self, master=None, entries=[], function=None, bg = None, fg = None, default_entry = None):
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

        if default_entry is None:
            self.variable.set(entries[0]) # default value
        else:
            self.variable.set(default_entry)
            
        def callback(*args):
            if function is not None:
                function(self.variable.get())
         
        self.variable.trace("w", callback)

class Combobox(ttk.Combobox):
    def __init__(self, elements, master=None, update_function=None):
        self.elements = elements
        ttk.Combobox.__init__(self,
                        master,
                        state="readonly",
                        values=elements,
                        postcommand=update_function
                        )
counter = 0
class dummy(tk.Menu):
    def __init__(self, **kwargs):   
        global counter
        tk.Menu.__init__(self, **kwargs) 
        counter += 1
        self.counter = counter    

          
class MultipleChoice(tk.Menubutton):
    def __init__(self, master=None, entries=[], text="Multiple choice", update_entries=None):
        if master is not None:
            bg = master["background"]
        else:
            bg = None    

        tk.Menubutton.__init__(self, master=master, text=text, bg=bg, borderwidth=1, relief="raised")

        self.choices = {}

        self.bind("<Button-1>", lambda event : self.left_click())

        self.alive = False    
        self.menu_obj = None   
        self.entries = entries
        self.update_entries = update_entries

    def left_click(self):

        if self.update_entries is not None:
            if self.update_entries(self):
                if self.menu_obj is not None:
                    self.menu_obj.delete(0,tk.END)
                self.alive = False

        # use this function to keep the menu open
        def menu_click(menu):
            menu.post(menu.winfo_rootx(), menu.winfo_rooty())

        if not self.alive:
            if self.menu_obj is None:
                self.menu_obj = tk.Menu(master=self, tearoff=False)

            for i, choice in enumerate(self.entries):
                if choice not in self.choices.keys():
                    self.choices[choice] = tk.IntVar(value=1)
                self.menu_obj.insert_checkbutton(i, label=choice, variable=self.choices[choice], 
                                        onvalue=1, offvalue=0, command=lambda: menu_click(self.menu_obj), background=self["background"])
            self.config(menu=self.menu_obj)
            self.alive = True

        else:
            self.menu_obj.delete(0,tk.END)
            self.alive = False

    def get_current_choices(self):
        result = []
        for choice in self.choices.keys():
            if self.choices[choice].get():
                result.append(choice)
        return result
        
        


