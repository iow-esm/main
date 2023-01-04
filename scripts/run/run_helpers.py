
def write_machinefile(global_settings, parallelization_layout):
    # get a list of node names that are currently used
    node_list = global_settings.get_node_list()

    # find out which threads belong to which models
    threads_of_model = {}
    for i, model in enumerate(parallelization_layout["this_model"]):
        try:
            threads_of_model[model].append(i)
        except:
            threads_of_model[model] = [i]

    # write a machine file
    file_name = "machine_file"

    with open(file_name, "w") as file:
        # find out which model has how many threads on which node
        for model in threads_of_model.keys():
            threads_on_node = {}
            for thread in threads_of_model[model]:
                # get the node of this model thread from the parallelization layout
                node = node_list[parallelization_layout["this_node"][thread]]
                # add this thread to that node
                try:
                    threads_on_node[node] += 1
                except:
                    threads_on_node[node] = 1
            # write how many threads are used for this model on the corresponding nodes
            for node in threads_on_node.keys():
                file.write(global_settings.machinefile_line(node, threads_on_node[node])+'\n')