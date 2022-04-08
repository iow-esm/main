import os
import re

todos = open('todos.rst', 'w')
todos.write("TODOs\n")
todos.write("=====\n")
for path, subdirs, files in os.walk("."):
    if "_build" in path or ".ipynb_checkpoints" in path or "autoapi" in path :
        continue
    for name in files:
        if name == "get_todos.py":
            continue
        if ".ipynb" in name or ".md" in name or ".rst" in name:
            with open(path + "/" + name, "r") as file:
                for i, line in enumerate(file):
                    if re.search("TODO", line):
                        todos.write(".. todo::\n")
                        todos.write("\n")
                        todos.write("   " + path + "/" + name + ":" + str(i+1) + " " + line + "\n")
                        todos.write("\n")
                        
todos.close()