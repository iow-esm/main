# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 09:22:28 2021

@author: Sven
"""

import glob
import sys

from collections import Counter

def go_through_depencies(model, task, found_dependencies):
    # found_dependencies: to memorize found dependencies to avoid cyclic recursion 
    
    # avoid cyclic recursion
    if task in found_dependencies:
        return []

    ldict = {"dependencies" : []}
    
    # try to get dependencies from local task config
    try:
        exec(open(model + "/" + task + "/config.py").read(), globals(), ldict)
    except:
        pass
    
    # store content to local variable
    dependencies = ldict["dependencies"]
    
    # append newly found dependencies, next level of recursion can check if task itself is already in (-> cyclic dependency)
    found_dependencies += dependencies
    
    # go recursively into the dependencies and concatenate the results
    for dep in dependencies:
        dependencies += go_through_depencies(model, dep, found_dependencies)
    
    return dependencies

def get_dependency_ordered_list(model, tasks):
    
    number_of_deps = {}

    for task in tasks:

        # gather all dependencies
        dependencies = go_through_depencies(model, task, [])
        
        # sort according to occurence (the more occurences the more basis is the task)
        dependencies.sort(key=Counter(dependencies).get, reverse=False)
        
        # make list unique but preserve the order
        dependencies = list(dict.fromkeys(dependencies))
        
        # get the number of occurences
        number_of_deps[task] = len(dependencies)
    
    # return a list that is ordered accodring to occurences
    return [x for _, x in sorted(zip(number_of_deps.values(), number_of_deps.keys()))]

                
            
        
        
