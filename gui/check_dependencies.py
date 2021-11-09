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

def get_dependency_group(dependencies, groups, last_group):
    
    # start with empty current group
    current_group = []
   
    # go through all tasks
    for task in dependencies.keys():
        
        # if task is already listed do not consider it further
        if task in last_group:
            continue

        # check if the dependencies of this task are all present in the previously listed tasks
        if set(dependencies[task]).issubset(set(last_group)):
            # if yes add it to the current group
            current_group.append(task)
    
    # if all tasks are already listed we stop here      
    if current_group == []:
        return
            
    # add this group to the list of groups
    groups.append(current_group)
    
    # add it also to the flat list of groups
    last_group += current_group
    
    # go on with next group
    get_dependency_group(dependencies, groups, last_group) 
                
            
def get_dependency_ordered_groups(model, tasks):
    
    dependencies = {}

    for task in tasks:

        # gather all dependencies
        dependencies[task] = go_through_depencies(model, task, [])

    groups = []
    get_dependency_group(dependencies, groups, [])
    return groups        
        
