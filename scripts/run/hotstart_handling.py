import os

def check_for_hotstart_folders(global_settings, models):
    
    # find out what is the latest date of each model's hotstart
    last_complete_hotstart_date = -1000
    for model in models:
    
        # so far no hotstart files for flux_calculator
        if model == 'flux_calculator':
            continue
            
        my_hotstart_dir = global_settings.root_dir+'/hotstart/'+global_settings.run_name+'/'+model
        # if hotstart dir does not exist yet, create it
        if (not os.path.isdir(my_hotstart_dir)):
            os.makedirs(my_hotstart_dir)
        # list folders in this directory
        my_hotstart_dates = [d for d in os.listdir(my_hotstart_dir) if os.path.isdir(os.path.join(my_hotstart_dir,d))]
        separator=','
        print('my_hotstart_dates for '+model+':'+separator.join(my_hotstart_dates))
        my_hotstart_dates = [int(i) for i in my_hotstart_dates] # integer in format YYYYMMDD
        # see if there are any hotstarts at all for this model
        if my_hotstart_dates:
            new_hotstart_date = max(my_hotstart_dates)  # get the latest one
            if (last_complete_hotstart_date < -1):
                last_complete_hotstart_date = new_hotstart_date
            if new_hotstart_date < last_complete_hotstart_date:
                last_complete_hotstart_date = new_hotstart_date
        else:
            last_complete_hotstart_date = -1      # at least one model has no hotstart at all

    # delete all those output and hotstart files after the last common (=successful) hotstart
    for model in models:
    
        # so far no hotstart files for flux_calculator
        if model == 'flux_calculator':
            continue
            
        my_hotstart_dir = global_settings.root_dir+'/hotstart/'+global_settings.run_name+'/'+model
        my_hotstart_dates = [d for d in os.listdir(my_hotstart_dir) if os.path.isdir(os.path.join(my_hotstart_dir,d))]
        my_hotstart_dates = [int(i) for i in my_hotstart_dates]
        for my_hotstart_date in my_hotstart_dates:
            if my_hotstart_date > last_complete_hotstart_date:
                os.system('rm -rf '+my_hotstart_dir+'/'+str(my_hotstart_date))

    # if there is no hotstart, use the initial date as starting date
    if last_complete_hotstart_date < 0:
        start_date = int(global_settings.init_date)
    else:
        start_date = last_complete_hotstart_date

    return start_date