# HLRN uses Intel MPI and SLURM
mpi_run_command = 'mpirun -configfile mpmd_file'        # the shell command used to start the MPI execution described in a configuration file "mpmd_file"
                                                    # it may contain the following wildcards that will be replaced later:
                                                    #   _NODES_ total number of nodes
                                                    #   _CORES_ total number of cores to place threads on
                                                    #   _THREADS_ total number of mpi threads
                                                    #   _CORESPERNODE_ number of cores per node to use
                                                    #   Examples: Intel MPI: 'mpirun -configfile mpmd_file'
                                                    #             OpenMPI  : 'mpirun --app mpmd_file'
mpi_n_flag = '-n'                                       # the mpirun flag for specifying the number of tasks.
                                                    #   Examples: Intel MPI: '-n'
                                                    #             OpenMPI  : '-np'
bash_get_rank = 'my_id=${PMI_RANK}'                     # a bash expression that saves the MPI rank of this thread in the variable "my_id"
                                                    #   Examples: Intel MPI    : 'my_id=${PMI_RANK}'
                                                    #             OpenMPI+Slurm: 'my_id=${OMPI_COMM_WORLD_RANK}'
python_get_rank = 'my_id = int(os.environ["PMI_RANK"])' # a python expression that saves the MPI rank of this thread in the variable "my_id"
                                                    #   Examples: Intel MPI    : 'my_id = int(os.environ["PMI_RANK"])'
                                                    #             OpenMPI+Slurm: 'my_id = int(os.environ["OMPI_COMM_WORLD_RANK"])'

use_mpi_machinefile = "-machine machine_file"         

def machinefile_line(node, ntasks):
    return str(node)+':'+str(ntasks)

def get_node_list():
    # get SLURM's node list, can be in format bcn1001 or bcn[1009,1011,1013] or bcn[1009-1011,1013]
    import os
    nodes = os.environ["SLURM_NODELIST"]

    # just a single node -> there is no "[" in the srting
    if "[" not in nodes:
        return [nodes]

    # get machine name -> can be "bcn" or "gcn"
    machine = nodes[0:3]

    # get list of comma separated values (cut out machine name and last "]")
    nodes = [node for node in nodes[len(machine)+1:-1].split(",")]

    #list of individual nodes
    node_list = []

    # go through list of comma separated values
    for node in nodes:
        # if theres is no minus this ellemtn is a indivual node
        if "-" not in node:
            node_list.append(machine+node)
            continue

        # range of nodes
        min_max = node.split("-")
        for node in range(int(min_max[0]),int(min_max[1])+1):
            node_list.append(machine+str(node))

    return node_list
