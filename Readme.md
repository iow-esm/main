# IOW Earth system model

This is the main repository for this project.
Further information will follow.

**!!!ATTENTION!!! This not yet a working project and cannot be used at the moment**


## Prerequisites


### Local

Your local machine has to provide:

* `bash`
* configured `git` instance
* optional: `python` (with the [`tkinter`](https://docs.python.org/3/library/tkinter.html) module) for using the graphical user interface 


#### Windows

If you work on Windows, you can use e.g. the [`MSYS2`](https://www.msys2.org/) software distribution and building platform. 
For installation, follow the instructions given on the project web site.
After successful installation you can open an `MSYS2` shell via hitting the Windows key on your keyboard, typing "msys" and opening the installed app.
In the opnend shell you can then install `git` and `rsync` which are needed by executing

``` bash
pacman -S git
pacman -S rsync
```


#### Linux

If you work on Linux you will most probably have a `bash` and you can install `git` with the package manager of your distribution.


### Remote

You need accounts on the target servers, where you want to run the model.

**TODO:** How to setup correctly `.bashrc`and `.bash_profile`?


### Get the main project

Open a shell (`MSYS2` on Windows or `bash` on Linux) and execute

``` bash
cd /to/your/favorite/directory
git clone https://git.io-warnemuende.de/iow_esm/main.git .
```

The place holder `/to/your/favorite/directory` will become the _root directory_ of this project so choose it resonably.

Note that it is strongly recommended to use a [key agent](https://www.ssh.com/academy/ssh/agent) for connecting to the target servers.
Otherwise you will have to type in your account password very often.
Assuming you have generated RSA key pairs for the target machines as described in the [phywiki](http://phywiki.io-warnemuende.de/do/view/Server/GenerateRsakeys) or as required for the HLRN, you can start a key agent via

``` bash
eval `ssh-agent`
ssh-add ~/.ssh/<private-key>
```

where the `<private-key>` should be the private key generated for the desired target.

### Working with the GUI

If you would like to work with graphical user interface you have to start corresponding python script from a shell
(`MSYS2` on Windows or `bash` on Linux) by executing the following in the root directory (where this `Readme.md` is located)

``` bash
/path/to/python iow_esm.py
```

The shell where this is executed should be the same as where the key agent is running.

The GUI will guide you step by step throught the first steps that are described in the following for the command line application.


## First steps


### Get the component sources

After cloning this repository to your local machine you have to get the component repositories as well.
For this purpose there is the bash script `clone_origins.sh` which uses the file `ORIGINS`. 
The one you have cloned right now contains all available components.
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
The first is the *keyword for the target*. This keyword has to match one of the following

* `hlrng`
* `hlrnb`
* `haumea`
* `phy-2`

where 

* `hlrng` refers to the HLRN IV cluster located in Göttingen
* `hlrnb` refers to the HLRN IV cluster located in Berlin
* `haumea` is the cluster of the of the Rostock University
* `phy-2` is one of the IOW's physics department computing servers (**ATTENTION: currently the model is not running here**)

At the moment there are running build scripts only for these targets. 
If you want to add more, it will be explained later how this can be done.

The second element in a line of `DESTINATIONS.example` corresponds to the *root directory on the target*, the path, where the whole model will be deployed, built and run.
If the path on the target does not exist, it will be created.
Be sure that you have write permissions.
Importantly, the location _must_ have the following format `user@host:/path/to/rootdirectory`.
Both user and host name are use in the script and cannot be omitted although you might have some shortcuts and aliases for your accounts.
**Now it is up to you, to create your own file `DESTINATIONS` in your local root directory, but do not commit it!**
Note that there is also the possibility to give more advanced keywords to run several instances on the same target, see [Advanced destination keywords](#advanced-destination-keywords)


### Build the coupled model for the first time

Each component can be built individually by executing the build scripts in the component's directory, see [Build single components in a different modes and configurations](#build-single-components-in-a-different-modes-and-configurations).
However, for the first build the order is important, since some components of the coupled model depend on each other.
Therefore, you should use the `build.sh` script in the root directory.
If you want to build the model e.g. on the HLRN cluster located in Berlin, you can run, e.g.

``` bash
./build.sh hlrng
``` 

This will build the model on `hlrng` in release mode.
Note that we will stick to this specific target throughout this Readme.
Nevertheless, if you want to work with another target for your first tests, just replace `hlrng` with another valid keyword.
Note that the first argument is non-optional, whereas there are two others which can be omitted, 
see [Build single components in a different modes and configurations](#build-single-components-in-a-different-modes-and-configurations).


### Deploy dependencies for running (setups)


#### Configure your setups

In order to run the model, you need input files which define a certain setup.
What exactly a setup consits of, you can find out by looking at [Available setups](#available-setups).
The setups you want to use can be registered in a special file named `SETUPS` (this name is obligatory), 
which is in the root directory.
Since this file specific for certain users and individual runs of the model it is not part of the repository and *you have to create one.*
However, there is an example `SETUPS.example`, please have a look.
You see that each line consists of two elements.
The first is the *keyword for the setup*. 
This keyword can be chosen by you almost freely.
It should be unique and a single word without spaces.
In order to update from one or several setups you can call the run script `run.sh` with a second, third, etc. argument representing your setup keys in the `SETUP`.
The files from these setups are then synchronized to the target in the order they appear as arguments.
That is, the last setup will overwrite the ones before if files are overlapping.

The second element of a line in `SETUPS` represents the location of this setup. 
This can be local on your machine or on a remote computer.
Be sure that the remote computer knows your targets and can copy files to them. 


#### Available setups

##### HLRN in Göttingen
You can find an example setup for a MOM5 for the Baltic sea coupled to a CCLM model for the Eurocordex domain under `/scratch/usr/mviowmod/IOW_ESM/setups/MOM5_Baltic-CCLM_Eurocordex/example_8nm_0.22deg`.
The corresponding line in the `SETUPS` file could then look like
`coupled_example user@glogin:/scratch/usr/mviowmod/IOW_ESM/setups/MOM5_Baltic-CCLM_Eurocordex/example_8nm_0.22deg`,
where `user` should be replaced by your user name on the HLRN in Göttingen.
It might be also necessary to add the full domain to the hostname, depending on your ssh configuration.
Other example setups (also for uncoupled runs) can be found in `SETUPS.example` in this directory.

**TODO:** Explain strucutre of the setup folder (= root directoy)


#### Copy setup files to target

After creating the file `SETUPS` you can run in the root directory

``` bash
./deploy_setup.sh hlrng coupled_example
``` 


### Run the coupled model for the first time

If everything is set up on your remote computer of choice, you can run the model for the first time by executing this in the root directory:

``` bash
./run.sh hlrng prepare-before-run
``` 

The first argument of the run script is always the target keyword as specified in your `DESTINATIONS` file.
By executing the run script all files from `scripts` directory will be transferred to the target.
The second argument `prepare-before-run` is obligatory for the very first run.
This will create necessary mapping files in the destination directories.
However, for all following runs *this is an optional argument and should be omitted*, unless you really want to re-create the mapping files.

After the scripts are transferred and the preparation script has finished (this can take a bit time),
the model is started on the target.

**Note that for an uncoupled run there is no need for the preparation.**

#### Examine the output of the first run


## Ongoing development


### Advanced destination keywords

It is possible to use not only the destination keywords given in [Configure your destinations (targets)](#configure-your-destinations-(targets)).
You can also use something like e.g. `hlrng_XXX` and `hlrng_YYY` if you want to run two independent instances on the target `hlrng`.
However, the string before the *first* underscore *must* be one of the keywords given above.

### Building during development


#### Build single components in a different modes and configurations

If you are developing only one component at a time, it is not necessary to call the global build script from the root directory.
There are also build scripts in each components subdirectory which can be called directly, e.g.

``` bash
cd components/flux_calculator
./build.sh hlrng debug rebuild 
``` 

This would rebuild the flux_calculator on the `hlrng` in debug mode.
The defaults for the second and third argument are `release` and `fast` (which is the opposite of `rebuild`).
The same applies likewise to the other components.


#### Build tagging

Once you execute a build command, e.g. 

``` bash
./build.sh hlrng
``` 

a file `LAST_BUILD_hlrng_release` is created, 
where the strings `hlrng` and `release` depend on the arguments, you give to the build script.
This file contains information on the state the source code of the components is in.
In particular, it contains the unique commit ID, the build mode (fast/rebuild) and a time stamp of the build.
Moreover, if the source code exhibits uncommited changes when the build script was executed,
these diffrences are logged within that file.
By executing the run script later on, the same tagging will be done for the main repository and this file is transferred to the destination.
That way, you can always identify with which version of the code your working on the target. 


### Running during development


#### Update the setup before running

During development it usual to modify the setup, i.e. parameters in input files.
It is not intended to do this directly on the target, 
because then it is hard to keep track of the changes (still it is possible of course).
However, the run script in the root directory offers the possibility to update the setup directly before running the model.
Before running, you have to prepare a setup used for updating.
The idea is, that you create a local folder where you put the input files that you want to modify.
This folder, e.g. `./local_setup`, must have the same directory structure as a normal setup folder.
For instance, if you want to have a modified `input/global_settings.py` at your destination, 
you create `./local_setup/input/global_settings.py`, make your changes in the file and then register this folder in the `SETUPS` file, 
e.g. by adding the line `update ./local_setup`.
Then you can run the model by calling

``` bash
./run.sh hlrng update
```

This will start the model on the `hlrng` but beforehand it will synchronize the contents of the `./local_setup` to the destination.
Moreover, in `./local_setup` there is file `UPDATE_SETUP_INFO` created, which is also transferred to the target 
and contains information and time stamp of the updating.

In general the run script can be called like

``` bash
./run.sh hlrng [prepare-before-run] update1 update2 update3...
```

where `prepare-before-run` is optional and can be omitted, which is usually the case if it is not the very first run on a target.
The setup updates are transferred in the order they appear, where the last one can, in principle, overwrite the ones before.
*Note that you should not use the keyword `prepare-before-run` for a setup, otherwise the script will be confused.*


## Archiving


### Archiving the employed setup

Imagine you have started your development on `hlrng` from the setup with the keyword `testing`, this can be viewed as the base of your current setup.
Now you made changes to some input files and you want to conserve the current state.
This can be done by using the script

``` bash
./archive_setup.sh hlrng testing archive
```

First, this would produce a copy of the base setup corresponding to the keyword `testing` in the very same destination (you need write permissions there).
The new folder has the same name as `testing` supplemented by `_archive` and it contains only symbolic links to the base setup.
Second, it is checked where the base setup and the one residing on the `hlrng` differ.
Third, only files that are different will be updated from the `hlrng` and put into the created archive folder.
If you want to create your archive in a different directory then your base, you can specifiy a keyword and the corresponding destination in the `SETUPS` file.
You can then call the setup archiving script with that keyword as the third argument.
Note that the base setup and the archive must be available via the same machine since we are using symbolic links here. 

Once you have archived your setup, the `SETUP_INFO` file on your target server will be updated as well.

### Archiving the obtained output


## Extending the project

### Register new destinations

1. Add a new keyword and the corresponding remote directory to your `DESTINATIONS` file.
Let's call the new target keyword in this example `new-target`.
Then the new line in your `DESTINATIONS` file could look like `new-target user@new-target:/data/user/IOW_ESM`.
Add `new_target` to the `available_targets` in `local_scripts/identify_target.sh`.

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
The existing `start_build_haumea.sh` is an example for using the queue, whereas `start_build_hlrng.sh` is an example for direct compilation on the login node.

### Add new models