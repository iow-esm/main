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


    



