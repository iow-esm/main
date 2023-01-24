# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:43:44 2021

@author: Sven
"""

from iow_esm_globals import *
from tkinter import ttk


class FunctionButton(tk.Button):
    def __init__(self, text, command, master=None, image=None, bg=None, fg=None, tip_text=None):
        if bg is None:
            bg=IowColors.blue1
        if fg is None:
            fg="white"
        tk.Button.__init__(self,
            master=master,
            text=text,
            bg=bg,
            fg=fg,
            command=command,
            image = image  
        )
        if tip_text is not None:
            CreateToolTip(self, text)
        
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
    def __init__(self, text, master=None, bg="", tip_text=None):
        
        if master is not None and bg == "":
            bg=master["background"]
            
        tk.Label.__init__(self,
            master=master,
            text=text, 
            bg = bg, 
            fg = 'black'
        )
        self.config(font=("TkDefaultFont", 20))

        if tip_text is not None:
            CreateToolTip(self, tip_text)
        
        
class Frame(tk.Frame):
    def __init__(self, master=None, bg=IowColors.blue1, tip_text=None):
        tk.Frame.__init__(self,
            master=master,
            bg = bg,
        )

        if tip_text is not None:
            CreateToolTip(self, tip_text)

 
class DropdownMenu(tk.OptionMenu):
    def __init__(self, master=None, entries=[], function=None, bg = None, fg = None, default_entry = None, tip_text = None):
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

        if tip_text is not None:
            CreateToolTip(self, tip_text)

          
class MultipleChoice(tk.Menubutton):
    def __init__(self, master=None, entries=[], text="Multiple choice", update_entries=None, tip_text=None):

        bg = IowColors.blue4
        fg = "black"

        tk.Menubutton.__init__(self, master=master, text=text, bg=bg, fg=fg, borderwidth=1, relief="raised")

        self.choices = {}

        self.bind("<Button-1>", lambda event : self.click(create=True))
        self.bind("<Button-3>", lambda event : self.click(create=False))

        self.alive = False    
        self.menu_obj = None  
        self.entries = entries
        self.update_entries = update_entries

        # initialize everything
        self.click(create=True)

        if tip_text is not None:
            CreateToolTip(self, tip_text+" (Click right to close the menu.)")

    def click(self, create=True):

        if not create:
            self.menu_obj.delete(0,tk.END)
            self.alive = False
            return

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

    def get_current_choices(self):
        result = []
        for choice in self.choices.keys():
            if self.choices[choice].get():
                result.append(choice)
        return result
    
    def clear_choices(self):
        self.choices = {}

class ToolTip(object):

    def __init__(self, widget, text):
        self.widget = widget
        self.tipwindow = None

        self.text = text
        self.tipwindow = tk.Toplevel(self.widget)
        self.label = tk.Label(self.tipwindow, text=self.text, justify=tk.LEFT,
                      background=IowColors.blue1, relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"), fg="white")
        self.label.pack(ipadx=1) 

        self.tipwindow.withdraw()

        self.inside = False

    def showtip(self):
        self.inside = True
        self.tipwindow.after(1000, self._show)

    def _show(self):
        if not self.inside:
            return

        # update coordinates of parent widget
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        
        self.tipwindow.wm_overrideredirect(1)
        self.tipwindow.wm_geometry("+%d+%d" % (x, y))
       
        self.tipwindow.deiconify()
        self.tipwindow.attributes('-topmost', 1)
        self.tipwindow.attributes('-topmost', 0)

    def hidetip(self):
        self.inside = False
        self.tipwindow.withdraw()


def CreateToolTip(widget, text):
    toolTip = ToolTip(widget, text)
    def enter(event):
        toolTip.showtip()
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)