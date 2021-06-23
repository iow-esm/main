####################################################
# Global settings for the IOW-ESM model run        #
####################################################

###################################
# STEP 1: Info about the modeller #
###################################
modeller        = "Hagen Radtke"                                               # name of the modeller who is responsible
email           = "hagen.radtke@io-warnemuende.de"                             # contact of the responsible modeller
institution     = "Leibniz Institute for Baltic Sea Research Warnemunde (IOW)" # name of the institute

###############################
# STEP 2: Info about the run  #
###############################
run_name        = "RUN04"        # name of the current run
run_description = "getting flux_calculator running"     # description: what is this run good for?
init_date       = "19790201"           # date when model is/was cold-started
final_date      = "19800701"           # when will the model run finally end? (YYYYMMDD) 
                                       # choose final_date<init_date to make model run as long as forcing is available
debug_mode      = False                # whether or not to use executables compiled with debugging options (slow)

#################################################
# STEP 3: Time stepping info                    #
#################################################
coupling_time_step = 600               # time step when fluxes are calculated and exchanged (s)
run_duration = "1 month"               # duration of one model run (day/days, month/months, year/years)
runs_per_job = 1                       # how many runs will be done in one job script
max_attempts = 1                       # if a run fails, you can have new attempts with modified settings

#################################################
# STEP 4: Working directory options             #
#################################################
workdir_base = "work"                  # base directory where individual model work dirs are located. 
                                       # if it does not start with "/", it is interpreted relative to IOW_ESM_ROOT
local_workdir_base = "" # If you want the workdirs to be created locally on the nodes, give an absolute path here.
                                       # This can also be an environment variable, e.g. "${LOCAL_TMPDIR}".
copy_to_global_workdir = True          # If local_workdir_base is given, use this flag to specify whether the 
                                       # entire content of the local workdir will be copied to workdir_base.
                                       # Output and restarts will be collected anyway.
link_files_to_workdir = True           # TRUE: input files will be linked to the working directory.
                                       # FALSE: input files will be copied to the working directory.

################################################
# STEP 5: Two-way coupling options             #
################################################
flux_calculator_mode = "single_core_per_bottom_model"   # "single_core_per_bottom_model": For each bottom model, one instance of flux_calulator will be
#flux_calculator_mode = "none"                           # started in an MPI task on its own core.
                                                        # "on_bottom_model_cores": (not available yet) The flux_calculator executable runs on the 
                                                        # same cores as the bottom models while they wait (some sort of hyperthreading).
                                                        # "none": no flux_calculator executable is started

################################################
# STEP 6: Parallel execution options           #
################################################
mpi_run_command = 'mpirun --app mpmd_file'        # the shell command used to start the MPI execution described in a configuration file "mpmd_file"
                                                        # it may contain the following wildcards that will be replaced later:
                                                        #   _NODES_ total number of nodes
                                                        #   _CORES_ total number of cores to place threads on
                                                        #   _THREADS_ total number of mpi threads
                                                        #   _CORESPERNODE_ number of cores per node to use
                                                        #   Examples: Intel MPI: 'mpirun -configfile mpmd_file'
                                                        #             OpenMPI  : 'mpirun --app mpmd_file'
mpi_n_flag = '-np'                                      # the mpirun flag for specifying the number of tasks.
                                                        #   Examples: Intel MPI: '-n'
                                                        #             OpenMPI  : '-np'
bash_get_rank = 'my_id=${OMPI_COMM_WORLD_RANK}'                     # a bash expression that saves the MPI rank of this thread in the variable "my_id"
                                                        #   Examples: Intel MPI    : 'my_id=${PMI_RANK}'
                                                        #             OpenMPI+Slurm: 'my_id=${OMPI_COMM_WORLD_RANK}'
python_get_rank = 'my_id = int(os.environ["OMPI_COMM_WORLD_RANK"])' # a python expression that saves the MPI rank of this thread in the variable "my_id"
                                                        #   Examples: Intel MPI    : 'my_id = int(os.environ["PMI_RANK"])'
                                                        #             OpenMPI+Slurm: 'my_id = int(os.environ["OMPI_COMM_WORLD_RANK"])'
cores_per_node = 40                                     # maximum number of cores per node that shall be used
jobscript_template = 'scripts/run/jobscript_haumea'     # path to a template file which will become the job script to run the model
                                                        # may contain the same wildcards as mpi_run_command, plus _IOW_ESM_ROOT_
check_layout_only = True                                # if set to True, will not run the models but only print which model runs on which node

################################################
# STEP 7 (optional): generate namcouple file automatically  #
################################################
generate_namcouple = True