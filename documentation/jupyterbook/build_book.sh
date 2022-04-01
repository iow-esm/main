#!/bin/bash

module load miniconda3
# necessary steps for first time
#conda create --name jupyterbook
conda activate jupyterbook
#conda install -c conda-forge jupyter-book
#pip install sphinx-autoapi

rm -r _build autoapi

python get_todos.py

# build _toc.yml
python get_files.py

# build book
jupyter-book build -v --keep-going --all .

mv _build/html _build/docs

