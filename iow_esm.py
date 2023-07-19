# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 13:51:29 2021

@author: Sven
"""

import sys
import glob

if not glob.glob('./gui'):
    print("This script would start the graphical user interface (GUI).")
    print("The GUI is not yet installed, please pull it from the repository or use the command-line interface.")
    sys.exit()

sys.path.append('./gui')
from gui import *

while True:
    gui = IowEsmGui()
    gui.window.mainloop()
    
    if not gui.restart:
        break