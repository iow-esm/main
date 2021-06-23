# IOW Earth system model

This is the main repository for this project.
Further information will follow.

## First steps

### Get the component sources

After cloning this repository to your local machine you have to get the component repositories as well.
For this purpose there is the bash script `local_scripts/clone_origins.sh` which uses the file `ORIGINS`.
By executing in the root directory (where this Readme.md is located)

``` bash
./local_scripts/clone_origins.sh
```

you clone all individual components which have their own repositories to your local machine.
If there will be some you don't need you can later remove them. 
However, be sure that you can still build and run the model properly.

