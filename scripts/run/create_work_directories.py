# This script will create the work directories for all models and a given start date.
# The function will be called from within run.py

from datetime import datetime
import os
import shutil
import time

import change_in_namelist


def create_work_directories(global_settings,            # global_settings
                            work_directory_root,     # /path/to/work/directory for all models
                            start_date,              # 'YYYYMMDD'
                            end_date,                # 'YYYYMMDD'
                            model_handler):           # model handler which implements the model specific steps for creating the workdir


    # Define the copy or link function
    if global_settings.link_files_to_workdir:
        def copyfunc(src,dst):
            return os.symlink(src,dst)
    else:
        def copyfunc(src,dst):
            return shutil.copyfile(src,dst,follow_symlinks=True)
    
    # get the name of the model's input folder
    model = model_handler.my_directory

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
        files = [d for d in os.listdir(global_settings.input_dir+'/'+model+'/') if os.path.isfile(os.path.join(global_settings.input_dir+'/'+model+'/',d))]
        for file in files:
            # copy or link the file
            copyfunc(global_settings.input_dir+'/'+model+'/'+file, work_dir+"/"+file)

        # STEP 3: CREATE ALL SUBFOLDERS AND COPY FILES DIRECTLY IN THEM
        # get a list of directories in that folder
        folders = [d for d in os.listdir(global_settings.input_dir+'/'+model+'/') if os.path.isdir(os.path.join(global_settings.input_dir+'/'+model+'/',d))]
        for folder in folders:
            if folder != "from": # a possible "from" folder will be treated later
                # create that folder in workdir as well
                os.makedirs(work_dir+'/'+folder)
                os.system('sync')
                # get a list of files, not folders, in this folder
                files = [d for d in os.listdir(global_settings.input_dir+'/'+model+'/'+folder+'/') 
                                 if os.path.isfile(os.path.join(global_settings.input_dir+'/'+model+'/'+folder+'/',d))]
                # copy these files
                for file in files:
                    copyfunc(global_settings.input_dir+'/'+model+'/'+folder+'/'+file, work_dir+"/"+folder+'/'+file)

                # STEP 4: SEE IF "from" DIRECTORY EXISTS IN THIS FOLDER
                # IF YES, IT CONTAINS SUBFOLDERS (YYYY or YYYYMMDD) STATING FROM WHEN ON THEIR CONTENTS ARE VALID
                # FIND THE APPROPRIATE DATE AND COPY THE FILES IN THESE SUBFOLDERS
                if os.path.isdir(global_settings.input_dir+'/'+model+'/'+folder+'/from'):
                    # get the list of dates
                    dates = [d for d in os.listdir(global_settings.input_dir+'/'+model+'/'+folder+'/from/')
                                 if os.path.isdir(os.path.join(global_settings.input_dir+'/'+model+'/'+folder+'/from/',d))]
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
                        files = [d for d in os.listdir(global_settings.input_dir+'/'+model+'/'+folder+'/from/'+our_date+'/')
                                 if os.path.isfile(os.path.join(global_settings.input_dir+'/'+model+'/'+folder+'/from/'+our_date+'/',d))]
                        for file in files:
                            if os.path.isfile(work_dir+'/'+folder+'/'+file): # if file exists in parent folder, delete it
                                os.remove(work_dir+'/'+folder+'/'+file)      # then replace with the one from the new folder
                            copyfunc(global_settings.input_dir+'/'+model+'/'+folder+'/from/'+our_date+'/'+file,work_dir+'/'+folder+'/'+file)
            else:  # the folder is called "from", so it works the same as in the subfolders containing a "from" folder
                # get the list of dates
                dates = [d for d in os.listdir(global_settings.input_dir+'/'+model+'/from/')
                             if os.path.isdir(os.path.join(global_settings.input_dir+'/'+model+'/from/',d))]
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
                    files = [d for d in os.listdir(global_settings.input_dir+'/'+model+'/from/'+our_date+'/')
                             if os.path.isfile(os.path.join(global_settings.input_dir+'/'+model+'/from/'+our_date+'/',d))]
                    for file in files:
                        if os.path.isfile(work_dir+'/'+file): # if file exists in parent folder, delete it
                            os.remove(work_dir+'/'+file)      # then replace with the one from the new folder
                        copyfunc(global_settings.input_dir+'/'+model+'/from/'+our_date+'/'+file,work_dir+'/'+file)

    # STEP 5: copy namcouple and change it according to run length
    if os.path.isfile(global_settings.input_dir+'/namcouple'):
        copyfunc(global_settings.input_dir+'/namcouple',work_dir+'/namcouple')

        my_startdate = datetime.strptime(start_date,'%Y%m%d')
        my_enddate = datetime.strptime(end_date,'%Y%m%d')
        runlength = (my_enddate - my_startdate).days*24*3600
        change_in_namelist.change_in_namelist(filename=work_dir+'/namcouple', 
                       after='$RUNTIME', before='$END', start_of_line='', 
                       new_value = str(runlength), add_if_needed=True)
    else:
        print("There is no " + global_settings.input_dir + '/namcouple. \
            It will be generated automatically if `generate_namcouple = True` in' + global_settings.input_dir + '/global_settings.py')

    # STEP 6: We will probably not need the files areas.nc, grids.nc and masks.nc
    # We still copy them.
    # For the files areas.nc, grids.nc and masks.nc which are shared between models, create symbolic links to the parent directory
    # so they will be shared between all model components but not updated globally when changed
    os.symlink(global_settings.global_workdir_base+'/areas.nc',work_dir+'/areas.nc')
    os.symlink(global_settings.global_workdir_base+'/grids.nc',work_dir+'/grids.nc')
    os.symlink(global_settings.global_workdir_base+'/masks.nc',work_dir+'/masks.nc')

    model_handler.create_work_directory(work_directory_root, start_date, end_date)
                                           

    return
