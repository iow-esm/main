# IOW Earth system model

This is the main repository for this project.
Further information will follow.

**!!!ATTENTION!!! This not yet a working project and cannot be used at the moment**


## First steps


### Prerequisites


#### Local

Your local machine has to provide:

* bash
* configured git instance

If you work on Windows, you can use e.g. `Git for Windows` which already provides these prerequisites.
If you work on Linux you will most probably have a `bash` and you can install `git` with the package manager of your distribution.


#### Remote

You need accounts on the target servers, where you want to run the model.
**TODO:** How to setup correctly `.bashrc`and `.bash_profile`?


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

* `hlrnb`
* `hlrng`
* `haumea`
* `phy-2`

where 

* `hlrnb` refers to the HLRN IV cluster located in Berlin
* `hlrng` refers to the HLRN IV cluster located in Göttingen
* `haumea` is the cluster of the of the Rostock University
* `phy-2` is one of the IOW's physics department computing servers (**ATTENTION: currently the model is not running here**)

At the moment there are running build scripts only for these targets. 
If you want to add more, it will be explained later how this can be done.
The second element in a line of `DESTINATIONS.example` corresponds to the *path on the target*, where the model will be deployed, built and run.
This path corresponds to the root directory where this `Readme.md` file is located. The path on the target has to already exist.
**Now it is up to you, to create your own file `DESTINATIONS` in your local root directory, but do not commit it!**


### Build the coupled model for the first time

The components of the copled model cannot be built indepently on each other.
For the first build you should probably use the `build.sh` script in the root directory.
If you want to build the model e.g. on the university's cluster, you can run, e.g.

``` bash
./build.sh haumea release rebuild
``` 

This will build the model on `haumea` in release mode.
If you want to start with debug confiuration replace `release` by `debug`.
The `rebuild` option is is obligatory for the first build, since that way necessary directories for some of the components are created.


### Deploy dependencies for running (setups)


#### Configure your setups

In order to run the model, you need input files which define a certain setup.
What exactly a setup consits of, you can find out by looking at **Available setups**.
The setups you want to use can be registered in a special file named `SETUPS` (this name is obligatory), 
which is in the root directory.
Since this file specific for certain users and individual runs of the model it is not part of the repository and *you have to create one.*
However, there is an example `SETUPS.example`, please have a look.
You see that each line consists of two elements.
The first is the *keyword for the setup*. 
This keyword can be chosen by you almost freely.
It should be unique and a single word without spaces and special characters.
In order to update from one or several setups you can call the run script `run.sh` with a second, third, etc. argument representing your setup keys in the `SETUP`.
The files from these setups are then synchronized to the target in the order they appear as arguments.
That is, the last setup will overwrite the ones before if files are overlapping.

The second element of a line in `SETUPS` represents the location of this setup. 
This can be local on your machine or on a remote computer.
Be sure that the remote computer knows your targets and can copy files to them. 


#### Available setups


#### Copy files to target

After creating the file `SETUPS` you can run in the root directory

``` bash
./deploy_setup.sh haumea testing
``` 

### Prepare the first run

On the target you have to go to the preparation-script directory

``` bash
cd scripts/prepare
```

and execute

``` bash
python create_mappings.py
```

Be sure that the correct python module is loaded.

**TODO:** to be changed such that this can be done from local computer.


### Run the coupled model for the first time

``` bash
./run.sh haumea
``` 

## Ongoing development

### Building during development


#### Build tagging
`LAST_BUILD_haumea`


### Running during development


#### Update the setup before running

``` bash
./run.sh haumea setup1 setup2 setup3...
```

## Extending the project

### Register new destinations

1. Add a new keyword and the corresponding remote directory to your `DESTINATIONS` file.
Let's call the new target keyword in this example `new-target`.
Then the new line in your `DESTINATIONS` file could look like `new-target user@new-target:/data/user/IOW_ESM`.
2. Add a build script for each component that should be build on the new target. 
For the example this must be called `build_new-target.sh`.
In general the name has to be `build_` followed by the keyword and `.sh`.
In most cases you can probably copy the build script from another target and simply adapt the loaded modules or paths.
You have to find out on your own which modification are to be done here.
3. Add a script that starts the build script on the target. 
For the example this must be called `start_build_new-target.sh`.
In general the name has to be `start_build_` followed by the keyword and `.sh`.
On some targets the build is performed using the queuing system on others it can be performed on directly the login node.
Find out which is true for your new target.
The existing `start_build_haumea.sh` is an example for using the queue, whereas `start_build_hlrnb.sh` is an example for direct compilation on the login node.

### Add new models