# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 16:47:30 2022

@author: Sven
"""

class IowEsmInfoTexts:
    
    header = """
####################################
#         Usage Information        #
####################################
    """
 
    clone_origins = header + """
    ### Get the component sources
    
    By hitting the button "Cone all origins" you will clone all currently available repositories that form the IOW_ESM.
    The program will go automatically to the next step. A list of all available origins is provided in the file "ORIGINS".
    
    If you don't want to clone all origins but particular ones you can hit the "Advanced" button.
    After you have everything you need, you have to hit the "Continue" button to go on.
    
    Note that for downloading repositories related to the COSMO community you need to be part of this community.
    In case of questions please contact sven.karsten@io-warnemuende.de before you start cloning.
    """

    edit_destinations = header + """
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
    If you want to add more, it will be explained in [Register new destinations](#register-new-destinations).

    The second element in a line of `DESTINATIONS.example` corresponds to the *root directory on the target*, the path, where the whole model will be deployed, built and run.
    If the path on the target does not exist, it will be created.
    Be sure that you have write permissions.
    Importantly, the location _must_ have the following format `user@host:/path/to/rootdirectory`.
    Both user and host name are use in the script and cannot be omitted although you might have some shortcuts and aliases for your accounts.
    **Now it is up to you, to create your own file `DESTINATIONS` in your local root directory, but do not commit it!**
    Note that there is also the possibility to give more advanced keywords to run several instances on the same target, see [Advanced destination keywords](#advanced-destination-keywords)
    """

    first_build = header + """ 
    ### Build the coupled model for the first time
    
    Each component of the IOW_ESM can be built individually. 
    However, for the first build the order is important, since some components of the coupled model depend on each other.
    Therefore, you should use the "Build all" functionality.
    You first have to select the destination by using the drop down menu in the "Destinations" frame of the window.
    Then you have to hit the "Build all" button.
    This will build the model on your selected target in release mode.
    This might take quite a while.
    Just have a look at the monitor and be sure that everything has been built correctly. 
    If so, hit the "Continue" button to go on.
    """    
    
    edit_setups = header + """     
    ### Deploy dependencies for running (setups)
    
    
    #### Configure your setups
    
    In order to run the model, you need input files which define a certain setup..
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
    You can find an example setup for a MOM5 for the Baltic sea coupled to a CCLM model for the Eurocordex domain under `/scratch/usr/mviowmod/IOW_ESM/setups/MOM5_Baltic-CCLM_Eurocordex/example_8nm_0.22deg/1.00.00`.
    The corresponding line in the `SETUPS` file could then look like
    `coupled_example user@glogin:/scratch/usr/mviowmod/IOW_ESM/setups/MOM5_Baltic-CCLM_Eurocordex/example_8nm_0.22deg/1.00.00`,
    where `user` should be replaced by your user name on the HLRN in Göttingen.
    It might be also necessary to add the full domain to the hostname, depending on your ssh configuration.
    Other example setups (also for uncoupled runs) can be found in `SETUPS.example` in this directory.
    """  
    
    first_deploy_setups = header + """     
    #### Copy setup files to target

    After creating the file `SETUPS` you can have to specify your desired target (in the "Destiantions" frame) first.
    Subsequently, you have to choose the setup you want to deploy via the dropdown menu in the "Setups" frame.
    You can now get information on the chosen setup by hitting "Get setups info".
    If you are sure you want to deploy the setup, hit the "Deploy setups" button.
    Look at the monitor what happens and if there are no errors hit "Continue".
    
    Before running the model you should have a look at the deployed folders on your target.
    Especially you should go to the `input` folder and open the file `global_settings.py`.
    Please enter your name and email here.
    Moreover you should have a look at the file `jobscript_*`. 
    Here you may adjust the account which you will use for running the model.
    """
