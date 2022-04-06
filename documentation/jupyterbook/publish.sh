#!/bin/bash

# The directory _build should be a repository that can be pushed 
# to a github repository that has github-pages enabled.
# The the book can be published as:

cd _build
git add .
git commit -a -m "Published book at `date`" 
git push -u origin master

# Other publish mechanisms could be used here, 
# like syncing to some folder which is used to create a website in the intranet
