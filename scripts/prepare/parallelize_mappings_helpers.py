from itertools import permutations
from netCDF4 import Dataset
import os
import numpy as np
import glob

def add_exchange_grid_task_vector(global_settings, model, model_tasks, grid, work_dir):

    # get source addresses of model grid cells that correspond to exchage grid cells
    remap_file = global_settings.root_dir + "/input/" + model + "/mappings/remap_" + grid + "_" + model + "_to_exchangegrid.nc"

    if not (os.path.isfile(remap_file)):
        print("There is no file " + remap_file + ". Cannot get exchange grid task vector.")
        return []

    nc = Dataset(remap_file,"r")
    src_address = nc.variables['src_address'][:]    # model grid cell indices
    dst_address = nc.variables['dst_address'][:]    # exchange grid cell indices
    num_links = nc.variables['num_links'][:]        # running index for links (is currently identical to dst_address)
    nc.close()

    #print(src_address)
    # find out which exchangegrid cells correspond to which model grid cells, dictionary: {"src_address" : ["dst_address1", "dst_address2", ...]}
    src_address_dict = {}
    for link in num_links-1:    # minus one since nc format starts from 1 and python starts from 0
        try:
            src_address_dict[src_address[link]].append(dst_address[link]) 
        except:
            src_address_dict[src_address[link]] = [dst_address[link]]

    # map model tasks onto exchange grid tasks
    eg_tasks = [-1]*len(dst_address)
    for link in num_links-1:
        for j in src_address_dict[src_address[link]]:
            eg_tasks[j-1] = model_tasks[src_address[link]-1]

    eg_file = work_dir + "/" + grid + "_" + "exchangegrid.nc"
    os.system("cp " +  global_settings.root_dir + "/input/" + model + "/mappings/" + grid + "_" + "exchangegrid.nc " + eg_file)

    nc = Dataset(eg_file,"a")
    try:
        nc.renameVariable("task", "task2")
    except:
        pass
    task_var = nc.createVariable("task","i4",("grid_size",)); task_var[:]=eg_tasks
    nc.close()

    return eg_tasks

def get_halo_cells(global_settings, model, grid, work_dir):
    
    # get task vector of  source grid
    src_eg_file = work_dir + "/" + grid + "_exchangegrid.nc"
    nc = Dataset(src_eg_file,"r")
    src_tasks = nc.variables['task'][:]
    nc.close()

    # preprare halo cells as dictionary with halo_cells["task1"] = [cell1, cell2, ...]
    halo_cells = {}
    for task in src_tasks:
        halo_cells[task] = []

    # find out to which grid this grid is regridded
    regrid_files = glob.glob(global_settings.root_dir + "/input/" + model + "/mappings/regrid_" + grid + "_" + model + "_to_*.nc")

    dst_grids = []
    for file in regrid_files:
        dst_grids.append(file.split("_to_")[-1].split(".nc")[0])

    for dst_grid in dst_grids:

        # get task vector of destiantion grid
        dst_eg_file = work_dir + "/" + dst_grid + "_exchangegrid.nc"
        nc = Dataset(dst_eg_file,"r")
        dst_tasks = nc.variables['task'][:]
        nc.close()

        # get regridding file
        regrid_file = global_settings.root_dir + "/input/" + model + "/mappings/regrid_" + grid + "_" + model + "_to_" + dst_grid + ".nc"
        
        nc = Dataset(regrid_file,"r")
        num_links = nc.variables['num_links'][:]    # links for mapping from t grid to other grid
        src_address = nc.variables['src_address'][:]    # cells on t grid
        dst_address = nc.variables['dst_address'][:]    # cells on other grid
        nc.close()

        # go through all the links
        for link in num_links - 1:          # minus one since nc format starts from 1 and python starts from 0
            src = src_address[link] - 1     # minus one since nc format starts from 1 and python starts from 0
            dst = dst_address[link] - 1     # minus one since nc format starts from 1 and python starts from 0

            # get tasks of the addresses
            src_task = src_tasks[src]
            dst_task = dst_tasks[dst]

            # if the tasks differ we get a halo cell for the destination cell task
            if src_task != dst_task:
                try:
                    halo_cells[dst_task].append(src)
                except:
                    halo_cells[dst_task] = [src]

        # make halo cells unique for the individual tasks  
        for task in halo_cells.keys():
            halo_cells[task]=list(set(halo_cells[task]))

    return halo_cells

def sort_exchange_grid(global_settings, model, grid, halo_cells, work_dir):

    # read the current unsorted exchange grid
    eg_file = work_dir + "/" + grid + "_" + "exchangegrid.nc"

    nc = Dataset(eg_file,"r")
    grid_size = nc.variables['grid_size'][:]
    grid_corners = nc.variables['grid_corners'][:]
    grid_rank = nc.variables['grid_rank'][:]
    grid_dims = nc.variables['grid_dims'][:]
    grid_center_lat = nc.variables['grid_center_lat'][:]
    grid_center_lon = nc.variables['grid_center_lon'][:]
    grid_imask = nc.variables['grid_imask'][:]
    grid_corner_lat = nc.variables['grid_corner_lat'][:][:]
    grid_corner_lon = nc.variables['grid_corner_lon'][:][:]
    grid_area = nc.variables['grid_area'][:]
    task = nc.variables['task'][:]
    nc.close()

    #create a dictionary for finding the exchange grid cells that correspond to a task,
    # i.e. eg_tasks_dict = {"task1" : [cell1, cell2,...], "task2" : [cell3, cell4,...]}
    eg_tasks_dict = {}
    for i, t in enumerate(task):    
        try:
            eg_tasks_dict[t].append(i)   
        except:
            eg_tasks_dict[t] = [i]

    # add halo cells
    for t in halo_cells.keys():
        try:
            eg_tasks_dict[t] += halo_cells[t]
        except:
            eg_tasks_dict[t] = halo_cells[t]

    # sort the dictionary according to the task index
    eg_tasks_dict = dict(sorted(eg_tasks_dict.items()))

    # find the permutation from unsorted to sorted exchange grid
    permutation = []
    # get the task vector for the sorted exchange grid (will be stored in the exchange grid nc-file)
    sorted_tasks = []
    # mark which cells are halo cells (=1) and which are original cells (=0)
    halo = []
    for task in eg_tasks_dict.keys():
        permutation += eg_tasks_dict[task]
        sorted_tasks += [task]*len(eg_tasks_dict[task])
        halo += [0]*(len(eg_tasks_dict[task]) - len(halo_cells[task]))
        halo += [1]*len(halo_cells[task])

    grid_size = [*range(1, len(sorted_tasks) + 1)]
    ncells = len(grid_size)
    grid_dims[0] = ncells

    # sort other quantities according to new order
    sorted_grid_center_lat = [-1]*ncells
    for i, old_index in enumerate(permutation):
        sorted_grid_center_lat[i] = grid_center_lat[old_index-1]    # minus one since nc format starts from 1 and python starts from 0

    sorted_grid_center_lon = [-1]*ncells
    for i, old_index in enumerate(permutation):
        sorted_grid_center_lon[i] = grid_center_lon[old_index-1]     

    sorted_grid_imask = [-1]*ncells
    for i, old_index in enumerate(permutation):
        sorted_grid_imask[i] = grid_imask[old_index-1]           

    sorted_grid_corner_lat = [-1]*ncells
    for i, old_index in enumerate(permutation):
        sorted_grid_corner_lat[i] = grid_corner_lat[old_index-1]

    sorted_grid_corner_lon = [-1]*ncells
    for i, old_index in enumerate(permutation):
        sorted_grid_corner_lon[i] = grid_corner_lon[old_index-1]      

    sorted_grid_area = [-1]*ncells
    for i, old_index in enumerate(permutation):
        sorted_grid_area[i] = grid_area[old_index-1]                 

    sorted_eg_file = work_dir + "/" + grid + "_" + "exchangegrid.nc"

    nc = Dataset(sorted_eg_file,"w")
    nc.title = sorted_eg_file
    nc.createDimension("grid_size"   ,len(grid_size)  ); grid_size_var    = nc.createVariable("grid_size"   ,"i4",("grid_size"   ,)); grid_size_var[:]    = grid_size
    nc.createDimension("grid_corners",len(grid_corners)); grid_corners_var = nc.createVariable("grid_corners","i4",("grid_corners",)); grid_corners_var[:] = grid_corners
    nc.createDimension("grid_rank"   ,len(grid_rank)   ); grid_rank_var    = nc.createVariable("grid_rank"   ,"i4",("grid_rank"   ,)); grid_rank_var[:]    = grid_rank
    grid_dims_var       = nc.createVariable("grid_dims"      ,"i4",("grid_rank",               )); grid_dims_var.missval=np.int32(-1) ; grid_dims_var[:]      =grid_dims
    grid_center_lat_var = nc.createVariable("grid_center_lat","f8",("grid_size",               )); grid_center_lat_var.units="degrees"; grid_center_lat_var[:]=sorted_grid_center_lat
    grid_center_lon_var = nc.createVariable("grid_center_lon","f8",("grid_size",               )); grid_center_lon_var.units="degrees"; grid_center_lon_var[:]=sorted_grid_center_lon
    grid_imask_var      = nc.createVariable("grid_imask"     ,"i4",("grid_size",               )); grid_imask_var.missval=np.int32(-1); grid_imask_var[:]     =sorted_grid_imask
    grid_corner_lat_var = nc.createVariable("grid_corner_lat","f8",("grid_size","grid_corners",)); grid_corner_lat_var.units="degrees"; grid_corner_lat_var[:]=sorted_grid_corner_lat
    grid_corner_lon_var = nc.createVariable("grid_corner_lon","f8",("grid_size","grid_corners",)); grid_corner_lon_var.units="degrees"; grid_corner_lon_var[:]=sorted_grid_corner_lon
    grid_area_var       = nc.createVariable("grid_area"      ,"f8",("grid_size",               )); grid_area_var.units      ="square radians"; grid_area_var[:]=sorted_grid_area
    task_var = nc.createVariable("task","i4",("grid_size",)); task_var[:] = sorted_tasks
    halo_var = nc.createVariable("halo","i4",("grid_size",)); halo_var[:] = halo
    permutation_var = nc.createVariable("permutation","i4",("grid_size",)); permutation_var[:]=(np.array(permutation) + 1) # plus one since nc format starts from 1 and python starts from 0
    nc.sync()
    nc.close()

    return permutation

def update_remapping(global_settings, model, grid, work_dir):
    update_remapping_from_model_to_exchange(global_settings, model, grid, work_dir)
    update_remapping_from_exchange_to_model(global_settings, model, grid, work_dir)

def update_remapping_from_model_to_exchange(global_settings, model, grid, work_dir):

    # 1. update remapping from model grid to exchange grid
    # src = model grid, dst = exchange grid

    # read in information from updated exchange grid file
    eg_file  = work_dir + "/" + grid + "_exchangegrid.nc"
    nc = Dataset(eg_file,"r")
    permutation =  nc.variables['permutation'][:]
    
    dst_grid_size = nc.variables['grid_size'][:]
    dst_grid_corners = nc.variables['grid_corners'][:]
    dst_grid_rank = nc.variables['grid_rank'][:]
    dst_grid_dims = nc.variables['grid_dims'][:]

    # the permutation has been applied to these variables in sort_exchange_grid so just use them
    sorted_dst_grid_center_lat = nc.variables['grid_center_lat'][:]
    sorted_dst_grid_center_lon = nc.variables['grid_center_lon'][:]
    sorted_dst_grid_imask = nc.variables['grid_imask'][:]
    sorted_dst_grid_area = nc.variables['grid_area'][:]
    nc.close()

    # read in current remapping
    remap_file = global_settings.root_dir + "/input/" + model + "/mappings/remap_" + grid + "_" + model + "_to_exchangegrid.nc"

    nc = Dataset(remap_file,"r")
    num_wgts = nc.variables['num_wgts'][:]
    src_grid_size = nc.variables['src_grid_size'][:]
    src_grid_corners = nc.variables['src_grid_corners'][:]
    src_grid_rank = nc.variables['src_grid_rank'][:]
    src_grid_dims = nc.variables['src_grid_dims'][:]
    src_address = nc.variables['src_address'][:]
    src_grid_center_lat = nc.variables['src_grid_center_lat'][:]
    src_grid_center_lon = nc.variables['src_grid_center_lon'][:]
    src_grid_imask = nc.variables['src_grid_imask'][:]
    src_grid_area = nc.variables['src_grid_area'][:]
    src_grid_frac = nc.variables['src_grid_frac'][:]
    dst_grid_frac = nc.variables['dst_grid_frac'][:]
    remap_matrix = nc.variables['remap_matrix'][:][:]
    nc.close()

    # do the update
    num_links = dst_grid_size  
    ncells = len(num_links)

    # new exchange grid adresses are just from 1 to len(dst_grid_size)
    sorted_dst_address = dst_grid_size

    # apply permutation
    sorted_dst_grid_frac = [-1]*ncells
    for i, old_index in enumerate(permutation):
        sorted_dst_grid_frac[i] = dst_grid_frac[old_index-1] 

    sorted_src_address = [-1]*ncells
    for i, old_index in enumerate(permutation):
        sorted_src_address[i] = src_address[old_index-1]               

    sorted_remap_matrix = np.full((len(num_links), len(num_wgts)), -1.0)
    for i, old_index in enumerate(permutation):
        sorted_remap_matrix[i, 0] = remap_matrix[old_index-1, 0]               

    model_grid_title       = model+'_'+grid
    exchangegrid_title      = model+'_'+grid+'_exchangegrid' 

    # write new remapping
    remap_file = work_dir + "/remap_" + grid + "_" + model + "_to_exchangegrid.nc"

    write_remap_file(remap_file, model_grid_title, exchangegrid_title,
                    src_grid_size=src_grid_size, dst_grid_size=dst_grid_size,
                    src_grid_corners=src_grid_corners, dst_grid_corners=dst_grid_corners,
                    src_grid_rank=src_grid_rank, dst_grid_rank=dst_grid_rank,
                    num_links=num_links,
                    num_wgts=num_wgts,
                    src_grid_dims=src_grid_dims, dst_grid_dims=dst_grid_dims,
                    src_grid_center_lat=src_grid_center_lat, dst_grid_center_lat=sorted_dst_grid_center_lat,
                    src_grid_center_lon=src_grid_center_lon, dst_grid_center_lon=sorted_dst_grid_center_lon,
                    src_grid_imask=src_grid_imask, dst_grid_imask=sorted_dst_grid_imask,
                    src_grid_area=src_grid_area,  dst_grid_area=sorted_dst_grid_area,
                    src_grid_frac=src_grid_frac,  dst_grid_frac=sorted_dst_grid_frac,
                    src_address=sorted_src_address, dst_address=sorted_dst_address,
                    remap_matrix=sorted_remap_matrix)

def update_remapping_from_exchange_to_model(global_settings, model, grid, work_dir):

    ################## 2. update remapping from exchange grid to model grid
    # src = exchange grid, dst = model grid

    # read in information from updated exchange grid file
    eg_file  = work_dir + "/" + grid + "_exchangegrid.nc"
    nc = Dataset(eg_file,"r")
    permutation =  nc.variables['permutation'][:]
    
    src_grid_size = nc.variables['grid_size'][:]
    src_grid_corners = nc.variables['grid_corners'][:]
    src_grid_rank = nc.variables['grid_rank'][:]
    src_grid_dims = nc.variables['grid_dims'][:]

    # the permutation has been applied to these variables in sort_exchange_grid so just use them
    sorted_src_grid_center_lat = nc.variables['grid_center_lat'][:]
    sorted_src_grid_center_lon = nc.variables['grid_center_lon'][:]
    sorted_src_grid_imask = nc.variables['grid_imask'][:]
    sorted_src_grid_area = nc.variables['grid_area'][:]
    halo = nc.variables['halo'][:]
    nc.close()

    # read in current remapping
    remap_file = global_settings.root_dir + "/input/" + model + "/mappings/remap_" + grid + "_exchangegrid_to_" + model + ".nc"

    nc = Dataset(remap_file,"r")
    num_wgts = nc.variables['num_wgts'][:]
    num_links = nc.variables['num_links'][:]
    dst_grid_size = nc.variables['dst_grid_size'][:]
    dst_grid_corners = nc.variables['dst_grid_corners'][:]
    dst_grid_rank = nc.variables['dst_grid_rank'][:]
    dst_grid_dims = nc.variables['dst_grid_dims'][:]
    dst_address = nc.variables['dst_address'][:]
    dst_grid_center_lat = nc.variables['dst_grid_center_lat'][:]
    dst_grid_center_lon = nc.variables['dst_grid_center_lon'][:]
    dst_grid_imask = nc.variables['dst_grid_imask'][:]
    dst_grid_area = nc.variables['dst_grid_area'][:]
    dst_grid_frac = nc.variables['dst_grid_frac'][:]
    src_grid_frac = nc.variables['src_grid_frac'][:]
    remap_matrix = nc.variables['remap_matrix'][:][:]
    nc.close()    

    # keep num_links as is
    # number of exchange grid cells
    ncells = len(src_grid_size)

    # new exchange grid addresses should be without halo cells, thus the length is the original num_links
    sorted_src_address = [-1]*len(num_links)
    # get all exchange grid (src) cells that are not halo cells
    j = 0 # counter for non-halo cells
    for i, src in enumerate(src_grid_size):
        if halo[i] != 1:
            sorted_src_address[j] = src
            j += 1

    # apply permutation to field array that is not present in the exchange grid file
    sorted_src_grid_frac = [-1]*ncells
    for i, old_index in enumerate(permutation):
        sorted_src_grid_frac[i] = src_grid_frac[old_index-1] 

    # apply permutation but leave out halo cells
    sorted_dst_address = [-1]*num_links # take length of num_links since halo cells are excluded
    j = 0 # counter for non-halo cells
    for i, old_index in enumerate(permutation):
        if halo[i] != 1:
            sorted_dst_address[j] = dst_address[old_index-1]   
            j += 1            

    sorted_remap_matrix = np.full((len(num_links), len(num_wgts)), -1.0)
    j = 0 # counter for non-halo cells
    for i, old_index in enumerate(permutation):
        if halo[i] != 1:
            sorted_remap_matrix[j, 0] = remap_matrix[old_index-1, 0] 
            j += 1

    model_grid_title       = model+'_'+grid
    exchangegrid_title      = model+'_'+grid+'_exchangegrid' 

    # write new remapping
    remap_file = work_dir + "/remap_" + grid + "_exchangegrid_to_" + model + ".nc"            

    write_remap_file(remap_file, exchangegrid_title, model_grid_title,
                    src_grid_size=src_grid_size, dst_grid_size=dst_grid_size,
                    src_grid_corners=src_grid_corners, dst_grid_corners=dst_grid_corners,
                    src_grid_rank=src_grid_rank, dst_grid_rank=dst_grid_rank,
                    num_links=num_links,
                    num_wgts=num_wgts,
                    src_grid_dims=src_grid_dims, dst_grid_dims=dst_grid_dims,
                    src_grid_center_lat=sorted_src_grid_center_lat, dst_grid_center_lat=dst_grid_center_lat,
                    src_grid_center_lon=sorted_src_grid_center_lon, dst_grid_center_lon=dst_grid_center_lon,
                    src_grid_imask=sorted_src_grid_imask, dst_grid_imask=dst_grid_imask,
                    src_grid_area=sorted_src_grid_area,  dst_grid_area=dst_grid_area,
                    src_grid_frac=sorted_src_grid_frac,  dst_grid_frac=dst_grid_frac,
                    src_address=sorted_src_address, dst_address=sorted_dst_address,
                    remap_matrix=sorted_remap_matrix)
    
def write_remap_file(file_name, src_grid_name, dst_grid_name,
                    src_grid_size=None, dst_grid_size=None,
                    src_grid_corners=None, dst_grid_corners=None,
                    src_grid_rank=None, dst_grid_rank=None,
                    num_links=None,
                    num_wgts=None,
                    src_grid_dims=None, dst_grid_dims=None,
                    src_grid_center_lat=None, dst_grid_center_lat=None,
                    src_grid_center_lon=None, dst_grid_center_lon=None,
                    src_grid_imask=None, dst_grid_imask=None,
                    src_grid_area=None,  dst_grid_area=None,
                    src_grid_frac=None,  dst_grid_frac=None,
                    src_address=None, dst_address=None,
                    remap_matrix=None):

    nc = Dataset(file_name,"w")
    nc.title = file_name
    nc.normalization = 'no norm' 
    nc.map_method = 'Conservative remapping'
    nc.conventions = "SCRIP" 
    nc.source_grid = src_grid_name
    nc.dest_grid = dst_grid_name
    nc.createDimension("src_grid_size"   ,len(src_grid_size) ); src_grid_size_var    = nc.createVariable("src_grid_size"   ,"i4",("src_grid_size"   ,)); src_grid_size_var[:]    = src_grid_size
    nc.createDimension("dst_grid_size"   ,len(dst_grid_size)  ); dst_grid_size_var    = nc.createVariable("dst_grid_size"   ,"i4",("dst_grid_size"   ,)); dst_grid_size_var[:]    = dst_grid_size
    nc.createDimension("src_grid_corners"   ,len(src_grid_corners)); src_grid_corners_var    = nc.createVariable("src_grid_corners"   ,"i4",("src_grid_corners"   ,)); src_grid_corners_var[:]  = src_grid_corners
    nc.createDimension("dst_grid_corners"   ,len(dst_grid_corners)  ); dst_grid_corners_var    = nc.createVariable("dst_grid_corners"   ,"i4",("dst_grid_corners"   ,)); dst_grid_corners_var[:]    = dst_grid_corners
    nc.createDimension("src_grid_rank"   ,len(src_grid_rank)   ); src_grid_rank_var    = nc.createVariable("src_grid_rank"   ,"i4",("src_grid_rank"   ,)); src_grid_rank_var[:]    = src_grid_rank
    nc.createDimension("dst_grid_rank"   ,len(dst_grid_rank)   ); dst_grid_rank_var    = nc.createVariable("dst_grid_rank"   ,"i4",("dst_grid_rank"   ,)); dst_grid_rank_var[:]    = dst_grid_rank
    nc.createDimension("num_links"   , len(num_links)   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = num_links
    nc.createDimension("num_wgts"   , len(num_wgts)   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = num_wgts
    src_grid_dims_var       = nc.createVariable("src_grid_dims"      ,"i4",("src_grid_rank",               )); src_grid_dims_var.missval=np.int32(-1)  ; src_grid_dims_var[:]      = src_grid_dims
    dst_grid_dims_var       = nc.createVariable("dst_grid_dims"      ,"i4",("dst_grid_rank",               )); dst_grid_dims_var.missval=np.int32(-1)  ; dst_grid_dims_var[:]      = dst_grid_dims
    src_grid_center_lat_var = nc.createVariable("src_grid_center_lat","f8",("src_grid_size",               )); src_grid_center_lat_var.units='radians' ; src_grid_center_lat_var[:]= src_grid_center_lat
    dst_grid_center_lat_var = nc.createVariable("dst_grid_center_lat","f8",("dst_grid_size",               )); dst_grid_center_lat_var.units='radians' ; dst_grid_center_lat_var[:]= dst_grid_center_lat
    src_grid_center_lon_var = nc.createVariable("src_grid_center_lon","f8",("src_grid_size",               )); src_grid_center_lon_var.units='radians' ; src_grid_center_lon_var[:]= src_grid_center_lon
    dst_grid_center_lon_var = nc.createVariable("dst_grid_center_lon","f8",("dst_grid_size",               )); dst_grid_center_lon_var.units='radians' ; dst_grid_center_lon_var[:]= dst_grid_center_lon
    src_grid_imask_var      = nc.createVariable("src_grid_imask"     ,"i4",("src_grid_size",               )); src_grid_imask_var.units='unitless'     ; src_grid_imask_var[:]     = src_grid_imask
    dst_grid_imask_var      = nc.createVariable("dst_grid_imask"     ,"i4",("dst_grid_size",               )); dst_grid_imask_var.units='unitless'     ; dst_grid_imask_var[:]     = dst_grid_imask
    src_grid_area_var       = nc.createVariable("src_grid_area"      ,"f8",("src_grid_size",               )); src_grid_area_var.units='square radians'; src_grid_area_var[:]      = src_grid_area
    dst_grid_area_var       = nc.createVariable("dst_grid_area"      ,"f8",("dst_grid_size",               )); dst_grid_area_var.units='square radians'; dst_grid_area_var[:]      = dst_grid_area
    src_grid_frac_var       = nc.createVariable("src_grid_frac"      ,"f8",("src_grid_size",               )); src_grid_frac_var.units='unitless'      ; src_grid_frac_var[:]      = src_grid_frac
    dst_grid_frac_var       = nc.createVariable("dst_grid_frac"      ,"f8",("dst_grid_size",               )); dst_grid_frac_var.units='unitless'      ; dst_grid_frac_var[:]      = dst_grid_frac
    src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   ));                                           src_address_var[:]        = src_address
    dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   ));                                           dst_address_var[:]        = dst_address
    remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        ));                                           remap_matrix_var[:,:]     = remap_matrix
    nc.close()

def update_regridding(global_settings, model, grid, work_dir):
    # get task vector of t_grid
    src_eg_file = work_dir + "/" + grid + "_exchangegrid.nc"

    nc = Dataset(src_eg_file,"r")
    src_tasks = nc.variables['task'][:]
    src_permutation = nc.variables['permutation'][:]
    src_halo = nc.variables['halo'][:]
    nc.close()

    # find out to which grid this grid is regridded
    regrid_files = glob.glob(global_settings.root_dir + "/input/" + model + "/mappings/regrid_" + grid + "_" + model + "_to_*.nc")

    dst_grids = []
    for file in regrid_files:
        dst_grids.append(file.split("_to_")[-1].split(".nc")[0])

    for dst_grid in dst_grids:

        # get task vector of other grid (let's call it here just u grid)
        dst_eg_file = work_dir + "/" + dst_grid + "_exchangegrid.nc"
        nc = Dataset(dst_eg_file,"r")
        dst_tasks = nc.variables['task'][:]
        dst_permutation = nc.variables['permutation'][:]
        dst_halo = nc.variables['halo'][:]
        nc.close()

        # get current regridding file
        regrid_file = global_settings.root_dir + "/input/" + model + "/mappings/regrid_" + grid + "_" + model + "_to_" + dst_grid + ".nc"
        #os.system("cp " +  global_settings.root_dir + "/input/" + model + "/mappings/" + regrid_file + " " + work_dir + "/" + regrid_file)
        
        nc = Dataset(regrid_file,"r")
        num_links = nc.variables['num_links'][:]
        num_wgts = nc.variables['num_wgts'][:]
        src_address = nc.variables['src_address'][:]    # cells on t grid
        dst_address = nc.variables['dst_address'][:]    # cells on other grid
        remap_matrix = nc.variables['remap_matrix'][:][:]
        nc.close()

        # get inverse permutation of core cells (non-halo cells)
        # inv_src_permutation[old_index] = new_index
        inv_src_permutation = {}
        for i, per in enumerate(src_permutation):
            if src_halo[i] != 1:
                inv_src_permutation[per] = i

        # get inverse permutation of core cells (non-halo cells)
        # inv_src_permutation[old_index] = new_index
        inv_dst_permutation = {}
        for i, per in enumerate(dst_permutation):
            if dst_halo[i] != 1:
                inv_dst_permutation[per] = i     

        # find the inverse permutation for the task specific halo cells 
        # inv_src_halo_permutation[task] = { old_index : new_index }
        inv_src_halo_permutation = {}
        for i, per in enumerate(src_permutation):
            if src_halo[i] == 1:
                try:
                    inv_src_halo_permutation[src_tasks[i]][per] = i
                except:
                    inv_src_halo_permutation[src_tasks[i]] = {per : i}

        sorted_src_address = []
        sorted_dst_address = []
        for link in num_links-1:
            # get old indices for this link
            old_src = src_address[link]
            old_dst = dst_address[link]
            # map old indices to new ones
            new_src = inv_src_permutation[old_src]
            new_dst = inv_dst_permutation[old_dst]
            # get the task indeces for these cells
            src_task = src_tasks[new_src]
            dst_task = dst_tasks[new_dst]
            # src and dst cell are from different tasks, tkae the corresponding halo cell instead
            if src_task != dst_task:
                # get src from halo of this task
                new_src = inv_src_halo_permutation[dst_task][old_src]
                sorted_src_address.append(new_src)
            else:
                sorted_src_address.append(new_src)
            
            sorted_dst_address.append(new_dst)

        # write updated regridding file
        regrid_file = work_dir + "/regrid_" + grid + "_" + model + "_to_" + dst_grid + ".nc"

        nc = Dataset(regrid_file,'w')
        nc.createDimension("num_links"   ,len(num_links)   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = num_links
        nc.createDimension("num_wgts"   , len(num_wgts)   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = num_wgts
        src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   )); src_address_var[:]        = np.array(sorted_src_address) + 1 # plus one since nc format starts from 1 and python starts from 0
        dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   )); dst_address_var[:]        = np.array(sorted_dst_address) + 1 # plus one since nc format starts from 1 and python starts from 0
        remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        )); remap_matrix_var[:,:]     = remap_matrix
        nc.close()    
        

def visualize_domain_decomposition(global_settings, model, model_tasks, eg_tasks, grid, halo_cells=None):
    import matplotlib.pyplot as plt
    from shapely.geometry import Polygon
    from scipy.spatial import ConvexHull

    def sort_xy(x, y):

        x0 = np.mean(x)
        y0 = np.mean(y)

        r = np.sqrt((x-x0)**2 + (y-y0)**2)

        angles = np.where((y-y0) > 0, np.arccos((x-x0)/r), 2*np.pi-np.arccos((x-x0)/r))

        mask = np.argsort(angles)

        x_sorted = x[mask]
        y_sorted = y[mask]

        return x_sorted, y_sorted
    
    # grid of ocean model
    nc_file = global_settings.root_dir + "/input/" + model + "/mappings/" + grid + ".nc"
    nc = Dataset(nc_file, 'r')
    grid_corner_lat = nc.variables['grid_corner_lat'][:][:]
    grid_corner_lon = nc.variables['grid_corner_lon'][:][:]
    imask = nc.variables['grid_imask'][:]
    nc.close()

    for i in range(0, np.shape(grid_corner_lon)[0]):

        if imask[i] == 0: 
            continue

        lons = [l for l in grid_corner_lon[i] if l != -1000.0]
        lats = [l for l in grid_corner_lat[i] if l != -1000.0]

        lons, lats = sort_xy(np.array(lons), np.array(lats))

        points = np.array([lons, lats]).transpose()
        hull = ConvexHull(points)

        x_hull = list(points[hull.vertices,0]) + [points[hull.vertices,0][0]]
        y_hull = list(points[hull.vertices,1]) + [points[hull.vertices,1][0]]

        plt.plot(x_hull, y_hull, 'b-', linewidth=0.5)
        plt.fill(x_hull, y_hull, 'b', alpha=0.2)

    # ocean domain decomposition
    model_tasks_dict = {}
    for i, task in enumerate(model_tasks):
        try:
            model_tasks_dict[task].append(i)
        except:
            model_tasks_dict[task]=[i]

    for task in model_tasks_dict.keys():

        if task == -1:
            continue

        lons=[]
        lats=[]
        
        for i in model_tasks_dict[task]:

            lons += [l for l in grid_corner_lon[i] if l != -1000.0]
            lats += [l for l in grid_corner_lat[i] if l != -1000.0]

        lons, lats = sort_xy(np.array(lons), np.array(lats))

        points = np.array([lons, lats]).transpose()
        hull = ConvexHull(points)

        x_hull = list(points[hull.vertices,0]) + [points[hull.vertices,0][0]]
        y_hull = list(points[hull.vertices,1]) + [points[hull.vertices,1][0]]

        plt.plot(x_hull, y_hull, 'r-', linewidth=1)
        plt.fill(x_hull, y_hull, 'r', alpha=0.2)

    nc_file = global_settings.root_dir + "/input/" + model + "/mappings/" + grid + "_exchangegrid.nc"
    nc = Dataset(nc_file, 'r')
    grid_corner_lat = nc.variables['grid_corner_lat'][:][:]
    grid_corner_lon = nc.variables['grid_corner_lon'][:][:]
    imask = nc.variables['grid_imask'][:]
    nc.close()
    
    # exchange grid domain decomposition
    eg_tasks_dict = {}
    for i, task in enumerate(eg_tasks):
        try:
            eg_tasks_dict[task].append(i)
        except:
            eg_tasks_dict[task]=[i]

    if halo_cells is not None:
        for task in eg_tasks_dict.keys():
            eg_tasks_dict[task] += halo_cells[task]

    for task in eg_tasks_dict.keys():

        if task == -1:
            continue

        lons=[]
        lats=[]
        
        for i in eg_tasks_dict[task]:

            lons += [l for l in grid_corner_lon[i] if l != -1000.0]
            lats += [l for l in grid_corner_lat[i] if l != -1000.0]

        lons, lats = sort_xy(np.array(lons), np.array(lats))

        points = np.array([lons, lats]).transpose()
        hull = ConvexHull(points)

        x_hull = list(points[hull.vertices,0]) + [points[hull.vertices,0][0]]
        y_hull = list(points[hull.vertices,1]) + [points[hull.vertices,1][0]]

        plt.plot(x_hull, y_hull, 'g--', linewidth=0.5)
        plt.fill(x_hull, y_hull, 'g', alpha=0.4)

    plt.savefig('domain_decomposition_' + model + "_" + grid + '.pdf')
    plt.close()
    #plt.show()