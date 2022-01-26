# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 16:47:30 2022

@author: Sven
"""

class IowEsmInfoTexts:
 
    clone_origins = """
#### Usage Information

By hitting the button "Cone all origins" you will clone all currently available repositories that form the IOW_ESM.
The program will go automatically to the next step. A list of all available origins is provided in the file "ORIGINS".

If you don't want to clone all origins but particular ones you can hit the "Advanced" button.
After you have everything you need, you have to hit the "Continue" button to go on.
"""

    edit_destinations = """
#### Usage Information
        
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
"""

    first_build = """
#### Usage Information
            
Each component of the IOW_ESM can be built individually. 
However, for the first build the order is important, since some components of the coupled model depend on each other.
Therefore, you should use the "Build all" functionality.
You first have to select the destination by using the drop down menu in the "Destinations" row of the window.
Then you have to hit the "Build all" button.
This will build the model on your selected target in release mode.
This might take quite a while.
Just have a look at the monitor and be sure that everything has been built correctly. 
If so, hit the "Continue" button to go on.
"""    
