#!/bin/bash

module load miniconda3
# necessary steps for first time
#conda create --name jupyterbook python=3.7
conda activate jupyterbook
#pip install --target=${CONDA_PREFIX}/lib/python3.7/site-packages --upgrade jupyter-book importlib-metadata==4.13.0 sphinx-autoapi
#export PATH=${PATH}:${CONDA_PREFIX}/lib/python3.7/site-packages/bin

# clean last build
rm -r _build/docs _build/.doctrees _build/jupyter_execute autoapi

# gather todos in source files and make a list
python get_todos.py

# build _toc.yml
#python get_files.py

# build book
jupyter-book build -v --keep-going --all .

# prepare folder for github-pages
mv _build/html _build/docs
touch _build/docs/.nojekyll

# using github pages:
# created _build folder should be a git repository that should be pushed to https://github.com/sven-karsten/iow_esm.git
# this github repository must have github-pages enabled
# html content of the docs folder is then available under https://sven-karsten.github.io/iow_esm/intro.html

