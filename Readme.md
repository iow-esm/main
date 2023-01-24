# Purpose, Description

This is the main repository for the IOW earth system model (ESM) project. 
It is the entry point for using and developing this model.

This Readme will guide you through the very first steps to start your first example run.

Further information is available at https://sven-karsten.github.io/iow_esm/intro.html.
**Note that the documentation is work in progress.**


# Authors

* SK      (sven.karsten@io-warnemuende.de)
* HR      (hagen.radtke@io-warnemuende.de)


# Versions

## 1.04.00 (in preparation)

| date        | author(s)   | link      |
|---          |---          |---        |
| 2023-01-24  | SK          | [1.04.00](https://git.io-warnemuende.de/iow_esm/main/src/branch/1.04.00)       | 

<details>

### changes
* several instqances of the IOW ESM can now run the same root folder
  * this can be done by creating subfolders in the `input` folder
  * the names of these input folder are then used as `run_name`
* output can be automatically archived and compressed (additinally monthly means are provided for fast access)
* output can automatically synchronized to a target while the model is running

### dependencies
* bash, git, (python for GUI) 
  
### known issues
* none

### tested with
* intensively tested on both HLRN machines
  * using example setups available under:
    (coupled, uncoupled MOM5, uncoupled CCLM, int2lm) /scratch/usr/mviowmod/IOW_ESM/setups/example/1.00.00                         
  * can be built and run on Haumea but output is not intensively tested

</details>


## 1.03.00 (latest release)

| date        | author(s)   | link      |
|---          |---          |---        |
| 2022-12-22  | SK          | [1.03.00](https://git.io-warnemuende.de/iow_esm/main/src/branch/1.03.00)       | 

<details>

### changes
* substiantial changes in postprocessing component, see Readme.md therein
* breaking changes in MOM5 component, see Readme.md therein
* new features in the flux_calculator component, see Readme.md therein
* some smaller corrections in other parts

### dependencies
* bash, git, (python for GUI) 
  
### known issues
* none

### tested with
* intensively tested on both HLRN machines
  * using example setups available under:
    (coupled) /scratch/usr/mviowmod/IOW_ESM/setups/
              MOM5_Baltic-CCLM_Eurocordex/example_3nm_0.22deg/1.00.00
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                CCLM_Eurocordex/example_0.22deg/1.00.00
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                MOM5_Baltic/example_3nm/1.00.00 
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                I2LM_Eurocordex/example_0.22deg/1.00.00                              
  * can be built and run on Haumea but output is not intensively tested
  
</details>

## 1.02.00

| date        | author(s)   | link      |
|---          |---          |---        |
| 2022-05-31  | SK          | [1.02.00](https://git.io-warnemuende.de/iow_esm/main/src/branch/1.02.00)       | 

<details>

### changes
* flux calculator can now run in parallel
  * see documentation/jupyterbook/usage/parallelize_flux_calculator.md for details
* factored out machine-dependent settings from global settings
  * machine settings are now implemented in machine_settings_*
  * one of these files is chosen by keyword "machine" global settings
  * these settings can be overwritten by explicitly putting the variables in global settings

### dependencies
* bash, git, (python for GUI) 
  
### known issues
* none

### tested with
* intensively tested on both HLRN machines
  * using example setups available under:
    (coupled) /scratch/usr/mviowmod/IOW_ESM/setups/
              MOM5_Baltic-CCLM_Eurocordex/example_8nm_0.22deg/1.00.00
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                CCLM_Eurocordex/example_0.22deg/1.00.00
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                MOM5_Baltic/example_8nm/1.00.00 
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                I2LM_Eurocordex/example_0.22deg/1.00.00                              
  * can be built and run on Haumea but output is not intensively tested
  
</details>


## 1.01.00 

| date        | author(s)   | link      |
|---          |---          |---        |
| 2022-04-27  | SK          | [1.01.00](https://git.io-warnemuende.de/iow_esm/main/src/branch/1.01.00)        | 

<details>

### changes
* worked on GUI
  * added cancel button
  * polished appearence
* enabled attempt handling
  * user can add own attempt hanlder with prepare and evaluate
    attempt methods
* intensive restructuring of run and prepare scripts
  * most scripts are now model-independent
  * model-dependent part is now restricted to one module
    * such a model has to be added for a new model
* fixed:
  * #19 Timeout for waiting for creating work directory, set to 60s
* worked on documentation 
  * added sources for jupyterbook
  * added link to built book on github-pages in Readme
    
### dependencies
* bash, git, (python for GUI) 
  
### known issues
* none

### tested with
* intensively tested on both HLRN machines
  * using example setups available under:
    (coupled) /scratch/usr/mviowmod/IOW_ESM/setups/
              MOM5_Baltic-CCLM_Eurocordex/example_8nm_0.22deg/1.00.00
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                CCLM_Eurocordex/example_0.22deg/1.00.00
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                MOM5_Baltic/example_8nm/1.00.00 
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                I2LM_Eurocordex/example_0.22deg/1.00.00                              
  * can be built and run on Haumea but output is not intensively tested
  
</details>


## 1.00.00 

| date        | author(s)   | link      |
|---          |---          |---        |
| 2022-01-31  | SK, HR      | [1.00.00](https://git.io-warnemuende.de/iow_esm/main/src/branch/1.00.00)  |  

<details> 

### changes
* initial release
  * scripts for running the model
  * scripts for creating mapping files and exchange grid
  * scripts for getting the sources and building them on target machines
    * supported are `hlrng`, `hlrnb`, `haumea`, (`phy-2` not running here)
  * scripts for deploying setups to a destiantion path
  * examples for user configurations
  * graphical user interface for running these scripts

### dependencies
* bash, git, (python for GUI) 

### known issues
* none

### tested with
* intensively tested on both HLRN machines
  * using example setups available under:
    (coupled) /scratch/usr/mviowmod/IOW_ESM/setups/
              MOM5_Baltic-CCLM_Eurocordex/example_8nm_0.22deg/1.00.00
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                CCLM_Eurocordex/example_0.22deg/1.00.00
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                MOM5_Baltic/example_8nm/1.00.00 
    (uncoupled) /scratch/usr/mviowmod/IOW_ESM/setups/
                I2LM_Eurocordex/example_0.22deg/1.00.00                              
  * can be built and run on Haumea but output is not intensively tested

</details>

# Usage

This part is intended to be a guide mainly for using the IOW ESM.
Although some hints for development are also given here, the concrete implemetation details are given at  https://sven-karsten.github.io/iow_esm/intro.html. and in the file `documentation/developers_documentation.pdf`.
**Note that the documentation is work in progress.**

## Prerequisites

Before doing anything with the IOW ESM some requirements have to be fulfilled.


### Local

Your local machine has to provide:

* `bash`
* configured `git` instance
* optional: `python` (with the [`tkinter`](https://docs.python.org/3/library/tkinter.html) module) for using the graphical user interface 


#### Windows

**!!!ATTENTION!!! It might not correctly work on Windows yet**

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


### Get the main project


#### As a user

If you just want to use the latest released version of the IOW ESM you have to execute the following in a shell (`MSYS2` on Windows or `bash` on Linux)

``` bash
cd /to/your/favorite/directory
git clone --branch X.XX.XX https://git.io-warnemuende.de/iow_esm/main.git .
```

where the `X.XX.XX` stands for the version you prefer.
Which versions are available can be found out by looking at the available Git branches that have names structured as "X.XX.XX".

The place holder `/to/your/favorite/directory` will become the _root directory_ of this project so choose it reasonably.


#### As a developer

If you intent to develop the IOW ESM and modify it you have to execute

``` bash
cd /to/your/favorite/directory
git clone https://git.io-warnemuende.de/iow_esm/main.git .
```

This will checkout the master (development) branch.

The place holder `/to/your/favorite/directory` will become the _root directory_ of this project so choose it reasonably.

Note, if you started as user but decide later to develop you can always check out the master branch manually.


#### Key agent recommended

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

**The GUI will guide you step by step throught the first steps that are described in the following for the command line application.**


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
For instance, if you want to run the models uncoupled from the other you still have to build the OASIS coupler first, 
see `documentation/developers_documentation.pdf` for details.

Note that depending on your choice from above, i.e. you cloned the main project as a user or as a developer, 
you will clone the latest release branches or the master (development) branches, respectively.
However, if you started as user but decide later to develop you can always check out the individual master branches manually.


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

At the moment there are running build scripts only for these targets, which can be found the file `AVAILABLE_TARGETS` as well.
Do not edit or commit this file unless you really know what you are doing.
If you want to add more targets, it will be explained in [Enable new destinations](https://sven-karsten.github.io/iow_esm/development/new_destinations.html#enable-new-destinations).

The second element in a line of `DESTINATIONS.example` corresponds to the *root directory on the target*, the path, where the whole model will be deployed, built and run.
If the path on the target does not exist, it will be created.
Be sure that you have write permissions.
Importantly, the location _must_ have the following format `user@host:/path/to/rootdirectory`.
Both user and host name are use in the script and cannot be omitted although you might have some shortcuts and aliases for your accounts.
**Now it is up to you, to create your own file `DESTINATIONS` in your local root directory, but do not commit it!**
Note that there is also the possibility to give more advanced keywords to run several instances on the same target, see [Advanced destination keywords](https://sven-karsten.github.io/iow_esm/usage/advanced_use.html#advanced-destination-keywords)


### Build the coupled model for the first time

Each component can be built individually by executing the build scripts in the component's directory, see [Build single components in a different modes and configurations](https://sven-karsten.github.io/iow_esm/usage/advanced_use.html#build-single-components-in-a-different-modes-and-configurations).
However, for the first build the order is important, since some components of the coupled model depend on each other.
Therefore, you should use the `build.sh` script in the root directory.
If you want to build the model e.g. on the HLRN cluster located in Berlin, you can run, e.g.

``` bash
./build.sh hlrng
``` 

This will build the model on `hlrng` in release mode.
Note that we will stick to this specific target throughout this Readme.
Nevertheless, if you want to work with another target for your first tests, just replace `hlrng` with another valid keyword.
Note further that the first argument is non-optional, whereas there are two others which can be omitted, 
see [Build single components in a different modes and configurations](https://sven-karsten.github.io/iow_esm/usage/advanced_use.html#build-single-components-in-a-different-modes-and-configurations).


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
You can find an example setup for a MOM5 (3 nm horizontal resolution) for the Baltic sea coupled to a CCLM model for the Eurocordex domain (0.22° horizontal resolution) under `/scratch/usr/mviowmod/IOW_ESM/setups/example/1.00.00`.
Here are also examples for uncoupled runs.
The corresponding line in the `SETUPS` file could then look like
`example user@glogin:/scratch/usr/mviowmod/IOW_ESM/setups/example/1.00.00`,
where `user` should be replaced by your user name on the HLRN in Göttingen.
It might be also necessary to add the full domain to the hostname, depending on your ssh configuration.
Other example setups (also for uncoupled runs) can be found in `SETUPS.example` in this directory.

**TODO:** Explain strucutre of the setup folder (= root directoy)


#### Copy setup files to target

After creating the file `SETUPS` you can run in the root directory

``` bash
./deploy_setup.sh hlrng example
``` 

Before running the model you should have a look at the deployed folders on your target.
Especially you should go to the folder `input/coupled` and open the file `global_settings.py`.
Please enter your name and email here.
Moreover you should have a look at the file `jobscript_*`. 
Here you may adjust the account which you will use for running the model.
More details on the preparation of the `input` folder is given in the file `documentation/developers_documentation.pdf`.  
 

### Run the coupled model for the first time

If everything is set up on your remote computer of choice, you can run the model for the first time by executing this in the root directory:

``` bash
./run.sh hlrng prepare-before-run coupled
``` 

The first argument of the run script is always the target keyword as specified in your `DESTINATIONS` file.
By executing the run script all files from `scripts` directory will be transferred to the target.

The second argument stands for creating necessary mappinng files that are used for the coupling, see `documentation/developers_documentation.pdf`.
If these mapping files already exist or you want to start an uncoupled run, this argument can be left out 

The third argument corresponds to the name of input subfolder that you want to run.
If you want to run from several input folders, you can list all of them here.
If you just have a single input folder witout subfolders, this argument can be left out.

In general the run command can look like

``` bash
./run.sh <destination1> prepare-before-run sync_to=<destination2> input1 input2 input3 ...
``` 
where destination1 corresponds to the run target machine and destination2 to a target, where you want to transfer the output to.

After all the scripts are transferred from your local computer to the target machine, the model is started on the target.