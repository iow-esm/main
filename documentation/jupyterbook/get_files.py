import os
import pathlib
root = "."

toc = []

for path, subdirs, files in os.walk(root):
    if "_build" in path:
        continue

    if not "usage" in path and not "development" in path:
        continue

    for name in files:
        if ".ipynb" in name or ".md" in name or ".rst" in name:
            print(name)
            currentFile = str(pathlib.PurePath(path, name))
            toc.append(currentFile)

f = open('_toc.yml', 'w')

header = """format: jb-book
root: intro.md
parts:
- caption: getting_started
  chapters:
  - file: getting_started/first_use.md
- caption: background
  chapters:
  - file: background/coupling_concept.md
  - file: background/details_on_fluxes.md
"""

f.write(header)

Chapter = ""

for element in toc:
    filename = os.path.basename(element)
    chapter = element.split("/")[0]
    if chapter != Chapter:
        Chapter = chapter
        f.write(f"- caption: {Chapter}\n")
        f.write("  chapters:\n")
    f.write(f"  - file: {element}\n")

footer = """- caption: scripts
  chapters:
  - file: autoapi/index.rst
- caption: general
  chapters:
  - file: general/history.md
- caption: todos
  chapters:
  - file: todos.rst
 """

f.write(footer)

f.close() 
