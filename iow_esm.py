# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 13:51:29 2021

@author: Sven
"""
import sys
sys.path.append('./gui')
from gui import *

while True:
    gui = IowEsmGui()
    gui.window.mainloop()
    
    if not gui.restart:
        break