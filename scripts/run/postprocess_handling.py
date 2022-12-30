import glob
import os

def start_postprocessing(IOW_ESM_ROOT, run_name, model, initial_start_date, end_date, task = "process_raw_output"):

    # no postprocessing for flux_calculator so far
    if model == "flux_calculator":
        return
    
    # directory of the postprocessing task for this model
    model_postprocess_dir = IOW_ESM_ROOT + "/postprocess/" + model.split("_")[0] + "/" + task
    
    # check if it exists
    if glob.glob(model_postprocess_dir) == []:
        print("No postprocessing task \"" + task + "\" could be found for model " + model.split("_")[0])
        return
    
    # build bash command (all in one line) to start the postprocessing
    command = "cd " + model_postprocess_dir + "; "
    
    # if file sbatch_header is present put the job into the SLURM queue 
    if glob.glob(model_postprocess_dir + "/sbatch_header"):
        command += "cat sbatch_header > postprocess_job; "
        command += "echo \"\" >> postprocess_job; "
        command += "echo \"source ../../load_modules.sh\" >> postprocess_job; "
        command += "echo \"./postprocess.sh " + IOW_ESM_ROOT+'/output/'+run_name+'/'+model + " " + str(initial_start_date) + " " + str(end_date) + "\" >> postprocess_job; "
        command += "chmod u+x postprocess_job; sbatch postprocess_job"
    # here could be the implementation for other queueing systems
    # if no header is there, start the script from where we are
    else:
        command += "source ../../load_modules.sh; ./postprocess.sh " + IOW_ESM_ROOT+'/output/'+run_name+'/'+model + " " + str(initial_start_date) + " " + str(end_date)
    
    # execute the command    
    os.system(command)

def postprocess_handling(global_settings, models, initial_start_date, end_date):
    
    #########################################################################################
    # STEP 4: JOB SUCCESSFULLY FINISHED - START PROCESSSING OF RAW OUTPUT (IF WANTED)       #
    #########################################################################################                                             
    # try if process_raw_output has been defined in global_settings.py
    try:
        process_raw_output = global_settings.process_raw_output
    # if not, set it to false
    except:
        process_raw_output = False
        
    if process_raw_output:
        print('Start postprocessing of raw output.', flush=True)
        for model in models:
            start_postprocessing(global_settings.root_dir, global_settings.run_name, model, initial_start_date, end_date)
    else:
        print("Raw output remains unprocessed.", flush=True)

    #########################################################################################
    # STEP 5: JOB SUCCESSFULLY FINISHED - START OTHER POSTPROCESSSING TASKS (IF WANTED)     #
    #########################################################################################   
    # try if postprocess_tasks has been defined in global_settings.py
    try:
        postprocess_tasks = global_settings.postprocess_tasks
    # if not, set it to empty dictionary
    except:
        postprocess_tasks = {}
     
    # go over models (keys of the dictionary) 
    for model in postprocess_tasks.keys():
        # check if value is a list (tasks are performed with defualt parameters)
        if type(postprocess_tasks[model]) is list:
            for task in postprocess_tasks[model]:
                print('Start postprocessing task ' + task + ' of model ' + model + ' with parameters: ', global_settings.run_name, initial_start_date, end_date, flush=True)
                start_postprocessing(global_settings.root_dir, global_settings.run_name, model, initial_start_date, end_date, task = task)
         
        # if there is a dictionary given, parameters can be customized
        elif type(postprocess_tasks[model]) is dict:
            for task in postprocess_tasks[model].keys():
            
                # see which parameters are given explicitely, if not use defaults
                try:
                    task_run_name = postprocess_tasks[model][task]["run_name"]
                except:
                    task_run_name = global_settings.run_name
                try:
                    task_init_date = postprocess_tasks[model][task]["init_date"]
                except:
                    task_init_date = initial_start_date

                try:
                    task_end_date = postprocess_tasks[model][task]["end_date"]
                except:
                    task_end_date = end_date 

                if type(task_init_date) is list:
                    if type(task_end_date) is not list:
                        print('Start postprocessing task ' + task + ' of model ' + model + ' not possible: Initial dates as list but final dates not!', flush=True)
                        continue

                    if end_date in task_end_date:
                        index = task_end_date.index(end_date)
                        print('Start postprocessing task ' + task + ' of model ' + model + ' with parameters: ', task_run_name, task_init_date[index], task_end_date[index], flush=True)
                        start_postprocessing(global_settings.root_dir, task_run_name, model, task_init_date, task_end_date, task = task)
                        continue

                    continue


                if type(task_end_date) is list:
                    if type(task_init_date) is not list:
                        print('Start postprocessing task ' + task + ' of model ' + model + ' not possible: Final dates as list but initial dates not!', flush=True)   
                        continue                     

                # check if this task should only be done when we reach the final date
                try:
                    task_only_at_end = postprocess_tasks[model][task]["only_at_end"]
                except:
                    task_only_at_end = False

                # check if this task should only be done when we reach the final date
                try:
                    task_only_at_start = postprocess_tasks[model][task]["only_at_start"]
                except:
                    task_only_at_start = False                    

                if task_only_at_end:
                    if int(end_date) == int(global_settings.final_date):
                        print('Start postprocessing task ' + task + ' of model ' + model + ' with parameters: ', task_run_name, task_init_date, task_end_date, flush=True)
                        start_postprocessing(global_settings.root_dir, task_run_name, model, task_init_date, task_end_date, task = task)
                        continue

                if task_only_at_start:
                    if int(initial_start_date) == int(global_settings.init_date):
                        print('Start postprocessing task ' + task + ' of model ' + model + ' with parameters: ', task_run_name, task_init_date, task_end_date, flush=True)
                        start_postprocessing(global_settings.root_dir, task_run_name, model, task_init_date, task_end_date, task = task)
                        continue                    

                print('Start postprocessing task ' + task + ' of model ' + model + ' with parameters: ', task_run_name, task_init_date, task_end_date, flush=True)
                start_postprocessing(global_settings.root_dir, task_run_name, model, task_init_date, task_end_date, task = task)