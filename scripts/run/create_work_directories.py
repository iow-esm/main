# This script will create the work directories for all models and a given start date.
# The function will be called from within run.py

from datetime import datetime
import os
import shutil
import time

import change_in_namelist

def create_work_directories(IOW_ESM_ROOT,            # root directory of IOW ESM
                            work_directory_root,     # /path/to/work/directory for all models
                            create_links_only,       # True if links are sufficient or False if files shall be copied
                            start_date,              # 'YYYYMMDD'
                            end_date,                # 'YYYYMMDD'
                            debug_mode = False,      # False if executables compiled for production mode shall be used, 
                                                     # True if executables compiled for debug mode shall be used
                            which_model='',          # Create work directory for a single model only. Empty string '' means all models
                            global_workdir_base=''): # in case we create a local work directory, we still need the global one for sharing files


    # Read global options file
    exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read(), globals())# read in function change_in_namelist

    # Define the copy or link function
    if create_links_only:
        def copyfunc(src,dst):
            return os.symlink(src,dst)
    else:
        def copyfunc(src,dst):
            return shutil.copyfile(src,dst,follow_symlinks=True)

    # Get a list of all subdirectories in "input" folder -> these are the models
    models = [d for d in os.listdir(IOW_ESM_ROOT+'/input/') if os.path.isdir(os.path.join(IOW_ESM_ROOT+'/input/',d))]
    # we possibly need flux_calculator as additional model
    if flux_calculator_mode=='single_core_per_bottom_model':
        models = models + ['flux_calculator']    

    # Loop over the models
    for model in models:
        if (model==which_model) | (which_model==''):
            # STEP 1: CREATE THE WORK DIRECTORY FOR THIS MODEL
            # define work directory
            work_dir = work_directory_root+'/'+model
            # if it already exists, delete it
            if os.path.isdir(work_dir):
               os.system('rm -rf '+work_dir)
            while os.path.isdir(work_dir):
               time.sleep(1.0)
               os.system('rm -rf '+work_dir)
            # create it
            os.makedirs(work_dir)

            if model!='flux_calculator':    
                # STEP 2: COPY FILES WHICH ARE DIRECTLY IN THIS FOLDER
                # get a list of files, not directories, in that folder
                files = [d for d in os.listdir(IOW_ESM_ROOT+'/input/'+model+'/') if os.path.isfile(os.path.join(IOW_ESM_ROOT+'/input/'+model+'/',d))]
                for file in files:
                    # copy or link the file
                    copyfunc(IOW_ESM_ROOT+'/input/'+model+'/'+file, work_dir+"/"+file)
  
                # STEP 3: CREATE ALL SUBFOLDERS AND COPY FILES DIRECTLY IN THEM
                # get a list of directories in that folder
                folders = [d for d in os.listdir(IOW_ESM_ROOT+'/input/'+model+'/') if os.path.isdir(os.path.join(IOW_ESM_ROOT+'/input/'+model+'/',d))]
                for folder in folders:
                    if folder != "from": # a possible "from" folder will be treated later
                        # create that folder in workdir as well
                        os.makedirs(work_dir+'/'+folder)
                        os.system('sync')
                        # get a list of files, not folders, in this folder
                        files = [d for d in os.listdir(IOW_ESM_ROOT+'/input/'+model+'/'+folder+'/') 
                                         if os.path.isfile(os.path.join(IOW_ESM_ROOT+'/input/'+model+'/'+folder+'/',d))]
                        # copy these files
                        for file in files:
                            copyfunc(IOW_ESM_ROOT+'/input/'+model+'/'+folder+'/'+file, work_dir+"/"+folder+'/'+file)
      
                        # STEP 4: SEE IF "from" DIRECTORY EXISTS IN THIS FOLDER
                        # IF YES, IT CONTAINS SUBFOLDERS (YYYY or YYYYMMDD) STATING FROM WHEN ON THEIR CONTENTS ARE VALID
                        # FIND THE APPROPRIATE DATE AND COPY THE FILES IN THESE SUBFOLDERS
                        if os.path.isdir(IOW_ESM_ROOT+'/input/'+model+'/'+folder+'/from'):
                            # get the list of dates
                            dates = [d for d in os.listdir(IOW_ESM_ROOT+'/input/'+model+'/'+folder+'/from/')
                                         if os.path.isdir(os.path.join(IOW_ESM_ROOT+'/input/'+model+'/'+folder+'/from/',d))]
                            # we will now sort the dates alphabetically
                            # we add the start_date passed to this script to the list
                           # to find its position, we append the letter "a" behind it
                            # the entry before the start_date then gives the date from which we use the files
                            dates.append(str(start_date)+'a')
                            dates.sort()
                            start_date_index = dates.index(str(start_date)+'a')
                            if start_date_index>0:
                                # start_date is not the first one in the list
                                # select the date which precedes our start_date
                                our_date = dates[start_date_index-1]
                                # copy all contents of this folder
                                files = [d for d in os.listdir(IOW_ESM_ROOT+'/input/'+model+'/'+folder+'/from/'+our_date+'/')
                                         if os.path.isfile(os.path.join(IOW_ESM_ROOT+'/input/'+model+'/'+folder+'/from/'+our_date+'/',d))]
                                for file in files:
                                    if os.path.isfile(work_dir+'/'+folder+'/'+file): # if file exists in parent folder, delete it
                                        os.remove(work_dir+'/'+folder+'/'+file)      # then replace with the one from the new folder
                                    copyfunc(IOW_ESM_ROOT+'/input/'+model+'/'+folder+'/from/'+our_date+'/'+file,work_dir+'/'+folder+'/'+file)
                    else:  # the folder is called "from", so it works the same as in the subfolders containing a "from" folder
                        # get the list of dates
                        dates = [d for d in os.listdir(IOW_ESM_ROOT+'/input/'+model+'/from/')
                                     if os.path.isdir(os.path.join(IOW_ESM_ROOT+'/input/'+model+'/from/',d))]
                        # we will now sort the dates alphabetically
                        # we add the start_date passed to this script to the list
                        # to find its position, we append the letter "a" behind it
                        # the entry before the start_date then gives the date from which we use the files
                        dates.append(str(start_date)+'a')
                        dates.sort()
                        start_date_index = dates.index(str(start_date)+'a')
                        if start_date_index>0:
                            # start_date is not the first one in the list
                            # select the date which precedes our start_date
                            our_date = dates[start_date_index-1]
                            # copy all contents of this folder
                            files = [d for d in os.listdir(IOW_ESM_ROOT+'/input/'+model+'/from/'+our_date+'/')
                                     if os.path.isfile(os.path.join(IOW_ESM_ROOT+'/input/'+model+'/from/'+our_date+'/',d))]
                            for file in files:
                                if os.path.isfile(work_dir+'/'+file): # if file exists in parent folder, delete it
                                    os.remove(work_dir+'/'+file)      # then replace with the one from the new folder
                                copyfunc(IOW_ESM_ROOT+'/input/'+model+'/from/'+our_date+'/'+file,work_dir+'/'+file)
    
            # STEP 5: copy namcouple and change it according to run length
            if os.path.isfile(IOW_ESM_ROOT+'/input/namcouple'):
                copyfunc(IOW_ESM_ROOT+'/input/namcouple',work_dir+'/namcouple')
    
                my_startdate = datetime.strptime(start_date,'%Y%m%d')
                my_enddate = datetime.strptime(end_date,'%Y%m%d')
                runlength = (my_enddate - my_startdate).days*24*3600
                change_in_namelist.change_in_namelist(filename=work_dir+'/namcouple', 
                               after='$RUNTIME', before='$END', start_of_line='', 
                               new_value = str(runlength), add_if_needed=True)
            else:
                print("There is no " + IOW_ESM_ROOT + '/input/namcouple. \
                    It will be generated automatically if `generate_namcouple = True` in' + IOW_ESM_ROOT + '/input/global_settings.py')

            # STEP 6: We will probably not need the files areas.nc, grids.nc and masks.nc
            # We still copy them.
            # For the files areas.nc, grids.nc and masks.nc which are shared between models, create symbolic links to the parent directory
            # so they will be shared between all model components but not updated globally when changed
            if global_workdir_base=='':
                global_workdir_base = work_directory_root
            os.symlink(global_workdir_base+'/areas.nc',work_dir+'/areas.nc')
            os.symlink(global_workdir_base+'/grids.nc',work_dir+'/grids.nc')
            os.symlink(global_workdir_base+'/masks.nc',work_dir+'/masks.nc')

            # STEP 7: Do model-dependent tasks such as copying the executable or putting dates into namelists
            if model[0:5]=='CCLM_':
                exec(open('create_work_directory_CCLM.py').read(),globals()) # read in function create_work_directory_CCLM      
                create_work_directory_CCLM(IOW_ESM_ROOT,work_directory_root,model,str(start_date),str(end_date),str(init_date),
                                           coupling_time_step,run_name,debug_mode)
            if model[0:5]=='MOM5_':
                exec(open('create_work_directory_MOM5.py').read(),globals()) # read in function create_work_directory_MOM5                      
                create_work_directory_MOM5(IOW_ESM_ROOT,work_directory_root,model,str(start_date),str(end_date),str(init_date),
                                           coupling_time_step,run_name,debug_mode)
            if model=='flux_calculator':
                exec(open('create_work_directory_flux_calculator.py').read(),globals()) # read in function create_work_directory_MOM5                      
                create_work_directory_flux_calculator(IOW_ESM_ROOT,work_directory_root,model,str(start_date),str(end_date),str(init_date),
                                           coupling_time_step,run_name,debug_mode)
    return
