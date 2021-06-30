# IOW Earth system model

This is the main repository for this project.
Further information will follow.

**!!!ATTENTION!!! This not yet a working project and not be used at the moment**

## First steps

### Prerequisites

#### Local

Your local machine has to provide:

* bash
* configured git instance

If you work on Windows, you can use e.g. `Git for Windows` which already provides these prerequisites.

#### Remote

You need accounts on the target servers, where you want to run the model

### Get the component sources

After cloning this repository to your local machine you have to get the component repositories as well.
For this purpose there is the bash script `local_scripts/clone_origins.sh` which uses the file `ORIGINS`. 
**This file should not be edited and commited unless you really know what you are doing.**
By executing in the root directory (where this `Readme.md` is located)

``` bash
./clone_origins.sh
```

you clone all individual components which have their own repositories to your local machine.
If there will be some you don't need you can later remove them. 
However, be sure that you can still build and run the model properly.

### Configure your destinations (targets)

You will not build (or run) the model on your local computer.
Instead you have to specify a destination or a target, where your sources are copied and compiled.
This is done a file `DESTINATIONS` (this name is obligatory). 
Since this file very user-specific it is not part of the repository and *you have to create one.*
However, there is an example `DESTINATIONS.example`, please have a look.
You see that each line consists of two elements.
The first is the *keyword for the target*. This keyword has to be one of the following

* haumea
* phy-2

where 

* `haumea` is the cluster of the of the Rostock University
* `phy-2` is one of the IOW's physics department computing servers

At the moment there are running build scripts only for these targets. 
If you want to add more, it will be explained later how this can be done.
The second element in a line of `DESTINATIONS.example` corresponds to the *path on the target*, where the model will be deployed, built and run.
This path corresponds to the root directory where this `Readme.md` file is located. The path on the target has to already exist.
**Now it is up to you, to create your own file `DESTINATIONS` in your local root directory, but do not commit it!**

## Deploy dependencies

### Depdendencies for building

### Dependencies for running

## Build the coupled model

### First build

The components of the copled model cannot be built indepently on each other.
For the first build you should probably use the `build.sh` script in the root directory.
If you want to build the model e.g. on the university's cluster, you can run

``` bash
./build.sh haumea
``` 

### Building during development

#### Build tagging
`LAST_BUILD_haumea`

## Run the coupled