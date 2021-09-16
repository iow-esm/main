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

root_dir = "."

class IowColors:
    blue1 = "#0a2b5a"
    green1 = "#74e40d"
    grey1 = "#4e584e"
        
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