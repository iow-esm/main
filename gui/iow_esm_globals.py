# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:43:44 2021

@author: Sven
"""

import tkinter as tk
import os
import glob
from functools import partial
import subprocess
import json

#root_dir = "."
root_dir = os.getcwd()

class IowColors:
    blue1 = "#10427a" 
    #"#0a2b5a"
    blue2 = "#305790"
    blue3 = "#6e85b5"
    blue4 = "#a1aed0"
    green1 = "#96d543"
    green2 = "#abdd64"
    green3 = "#cbe999"
    green4 = "#e0f2c0"
    grey1 = "#4c564c"
    grey2 = "#6b766b"
    grey3 = "#9ea89d"
    grey4 = "#c3cac2"
        
def read_iow_esm_configuration(file_name):
    
    config = {}
    with open(file_name, "r") as f:
        for line in f:
            try:
                (key, val) = line.split()
                config[key] = val
            except:
                pass
            
    return config