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

## 1.04.00 (latest release)

| date        | author(s)   | link      |
|---          |---          |---        |
| 2023-07-26  | SK          | [1.04.00](https://git.io-warnemuende.de/iow_esm/main/src/branch/1.04.00)       | 

<details>

### changes
* bias corrections can be applied to the `CCLM` and the `flux_calculator` components
* albedo for shortwave radiation is applied in the `MOM5` component instead of the `flux_calculator`
* several instqances of the IOW ESM can now run the same root folder
  * this can be done by creating subfolders in the `input` folder
  * the names of these input folder are then used as `run_name`
* output can be automatically archived and compressed (additinally monthly means are provided for fast access)
* output can automatically synchronized to a target while the model is running
* added patching and merging tool for publishing non-open-source code (uses Linux tools `diff` and `patch`)
* documentation is extended (but not yet complete)
* added build script templates and the script `add_target.sh` script to add new computing targets to the framework
* for all details see `Readme.md`'s of the components

### dependencies
* bash, git, (python for GUI) 
* uses `patch` 1.00.00
  
### known issues
* in coupled mode, this version leads to too cold summer temperatures 
  when evaluated from 1959-2019
  * tested bias corrections can improve on that but investigation is not yet finished

### tested with
* intensively tested on both HLRN machines
  * using example setups available under:
    (coupled, uncoupled MOM5, uncoupled CCLM, int2lm) /scratch/usr/mviowmod/IOW_ESM/setups/example/1.00.00   
    (coupled) https://zenodo.org/record/8167743/files/1.00.00.tar.gz (https://doi.org/10.5281/zenodo.8167743)                       
  * can be built and run on Haumea but output is not intensively tested

</details>


<details>
<summary><b><i>older versions</i></b></summary>

## 1.03.00 

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
</details>

# Usage

This part is intended to be a guide mainly for using the IOW ESM.
Although some hints for development are also given here, more implemetation details are given at  https://sven-karsten.github.io/iow_esm/intro.html.


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


## First use

In order to be able to use the IOW ESM, please follow the steps described at https://sven-karsten.github.io/iow_esm/getting_started/first_use.html#first-use