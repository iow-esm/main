from netCDF4 import Dataset
import os
import numpy as np

def get_exchange_grid_task_vector(global_settings, model, model_tasks, grid="t_grid"):

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

    return eg_tasks


def sort_exchange_grid(global_settings, model, eg_tasks, grid="t_grid"):

    # read the current unsorted exchange grid
    eg_file = global_settings.root_dir + "/input/" + model + "/mappings/" + grid + "_" + "exchangegrid.nc"

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
    nc.close()

    #create a dictionary for finding the exchange grid cells that correspond to a task,
    # i.e. eg_tasks_dict = {"task1" : [cell1, cell2,...], "task2" : [cell3, cell4,...]}
    eg_tasks_dict = {}
    for cell in grid_size:    
        try:
            eg_tasks_dict[eg_tasks[cell-1]].append(cell)    # minus one since nc format starts from 1 and python starts from 0
        except:
            eg_tasks_dict[eg_tasks[cell-1]] = [cell]        # minus one since nc format starts from 1 and python starts from 0

    # sort the dictionary according to the task index
    eg_tasks_dict = dict(sorted(eg_tasks_dict.items()))

    # find the permutation from unsorted to sorted exchange grid
    permutation = []
    # get the task vector for the sorted exchange grid (will be stored in the exchange grid nc-file)
    sorted_tasks = []
    for task in eg_tasks_dict.keys():
        permutation += eg_tasks_dict[task]
        sorted_tasks += [task]*len(eg_tasks_dict[task])

    # sort other quantities according to new order
    sorted_grid_center_lat = grid_center_lat[:]
    for i, old_index in enumerate(permutation):
        sorted_grid_center_lat[i] = grid_center_lat[old_index-1]    # minus one since nc format starts from 1 and python starts from 0

    sorted_grid_center_lon = grid_center_lon[:]
    for i, old_index in enumerate(permutation):
        sorted_grid_center_lon[i] = grid_center_lon[old_index-1]     

    sorted_grid_imask = grid_imask[:]
    for i, old_index in enumerate(permutation):
        sorted_grid_imask[i] = grid_imask[old_index-1]           

    sorted_grid_corner_lat = grid_corner_lat[:]
    for i, old_index in enumerate(permutation):
        sorted_grid_corner_lat[i] = grid_corner_lat[old_index-1]

    sorted_grid_corner_lon = grid_corner_lon[:]
    for i, old_index in enumerate(permutation):
        sorted_grid_corner_lon[i] = grid_corner_lon[old_index-1]      

    sorted_grid_area = grid_area[:]
    for i, old_index in enumerate(permutation):
        sorted_grid_area[i] = grid_area[old_index-1]                 

    print(permutation)   



    sorted_eg_file = global_settings.root_dir + "/input/" + model + "/mappings/" + grid + "_" + "exchangegrid_sorted.nc"

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
    task_var = nc.createVariable("task","f8",("grid_size",)); task_var[:]=sorted_tasks
    nc.sync()
    nc.close()

    return permutation


def sort_remapping(global_settings, model, permutation, grid="t_grid"):

    # 1. update remapping from exhange grid to model grid

    # read in current remapping
    remap_file = global_settings.root_dir + "/input/" + model + "/mappings/remap_" + grid + "_exchangegrid_to_" + model + ".nc"

    nc = Dataset(remap_file,"r")
    src_grid_size = nc.variables['src_grid_size'][:]
    dst_grid_size = nc.variables['dst_grid_size'][:]
    grid_rank = nc.variables['grid_rank'][:]
    grid_dims = nc.variables['grid_dims'][:]
    grid_center_lat = nc.variables['grid_center_lat'][:]
    grid_center_lon = nc.variables['grid_center_lon'][:]
    grid_imask = nc.variables['grid_imask'][:]
    grid_corner_lat = nc.variables['grid_corner_lat'][:][:]
    grid_corner_lon = nc.variables['grid_corner_lon'][:][:]
    grid_area = nc.variables['grid_area'][:]
    nc.close()    

    return

    # # write new file
    # sorted_remap_file = global_settings.root_dir + "/input/" + model + "/mappings/remap_" + grid + "_exchangegrid_to_" + model + "_sorted.nc"

    # model_grid_title       = model+'_'+grid
    # exchangegrid_title      = model+'_'+grid+'_exchangegrid' 

    # nc = Dataset(sorted_remap_file,'w')
    # nc.title = sorted_remap_file
    # nc.normalization = 'no norm' 
    # nc.map_method = 'Conservative remapping'
    # nc.conventions = "SCRIP" 
    # nc.source_grid = exchangegrid_title
    # nc.dest_grid = model_grid_title
    # nc.createDimension("src_grid_size"   ,len(src_grid_size) ); src_grid_size_var    = nc.createVariable("src_grid_size"   ,"i4",("src_grid_size"   ,)); src_grid_size_var[:]    = src_grid_size
    # nc.createDimension("dst_grid_size"   ,len(dst_grid_size)  ); dst_grid_size_var    = nc.createVariable("dst_grid_size"   ,"i4",("dst_grid_size"   ,)); dst_grid_size_var[:]    = dst_grid_size
    # nc.createDimension("src_grid_corners"   ,max(corners[0:global_k])  ); src_grid_corners_var    = nc.createVariable("src_grid_corners"   ,"i4",("src_grid_corners"   ,)); src_grid_corners_var[:]    = [n+1 for n in range(max(corners[0:global_k]))]
    # nc.createDimension("dst_grid_corners"   ,4  ); dst_grid_corners_var    = nc.createVariable("dst_grid_corners"   ,"i4",("dst_grid_corners"   ,)); dst_grid_corners_var[:]    = [n+1 for n in range(4)]
    # nc.createDimension("src_grid_rank"   ,1   ); src_grid_rank_var    = nc.createVariable("src_grid_rank"   ,"i4",("src_grid_rank"   ,)); src_grid_rank_var[:]    = [1]
    # nc.createDimension("dst_grid_rank"   ,len(grid_dims_1)   ); dst_grid_rank_var    = nc.createVariable("dst_grid_rank"   ,"i4",("dst_grid_rank"   ,)); dst_grid_rank_var[:]    = [n+1 for n in range(len(grid_dims_2))]
    # nc.createDimension("num_links"   ,global_k   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = np.arange(global_k)
    # nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = np.arange(1)
    # src_grid_dims_var       = nc.createVariable("src_grid_dims"      ,"i4",("src_grid_rank",               )); src_grid_dims_var.missval=np.int32(-1)  ; src_grid_dims_var[:]      =[global_k]
    # dst_grid_dims_var       = nc.createVariable("dst_grid_dims"      ,"i4",("dst_grid_rank",               )); dst_grid_dims_var.missval=np.int32(-1)  ; dst_grid_dims_var[:]      =grid_dims_2
    # src_grid_center_lat_var = nc.createVariable("src_grid_center_lat","f8",("src_grid_size",               )); src_grid_center_lat_var.units='radians' ; src_grid_center_lat_var[:]=np.deg2rad([np.mean([poly_y[k][0:(corners[k]-1)]]) for k in range(global_k)])
    # dst_grid_center_lat_var = nc.createVariable("dst_grid_center_lat","f8",("dst_grid_size",               )); dst_grid_center_lat_var.units='radians' ; dst_grid_center_lat_var[:]=np.deg2rad(grid_center_lat2)
    # src_grid_center_lon_var = nc.createVariable("src_grid_center_lon","f8",("src_grid_size",               )); src_grid_center_lon_var.units='radians' ; src_grid_center_lon_var[:]=np.deg2rad([np.mean([poly_x[k][0:(corners[k]-1)]]) for k in range(global_k)])
    # dst_grid_center_lon_var = nc.createVariable("dst_grid_center_lon","f8",("dst_grid_size",               )); dst_grid_center_lon_var.units='radians' ; dst_grid_center_lon_var[:]=np.deg2rad(grid_center_lon2)
    # src_grid_imask_var      = nc.createVariable("src_grid_imask"     ,"i4",("src_grid_size",               )); src_grid_imask_var.units='unitless'     ; src_grid_imask_var[:]     =[1]*global_k
    # dst_grid_imask_var      = nc.createVariable("dst_grid_imask"     ,"i4",("dst_grid_size",               )); dst_grid_imask_var.units='unitless'     ; dst_grid_imask_var[:]     =grid_imask_2
    # src_grid_area_var       = nc.createVariable("src_grid_area"      ,"f8",("src_grid_size",               )); src_grid_area_var.units='square radians'; src_grid_area_var[:]      =area3
    # dst_grid_area_var       = nc.createVariable("dst_grid_area"      ,"f8",("dst_grid_size",               )); dst_grid_area_var.units='square radians'; dst_grid_area_var[:]      =area2
    # src_grid_frac_var       = nc.createVariable("src_grid_frac"      ,"f8",("src_grid_size",               )); src_grid_frac_var.units='unitless'      ; src_grid_frac_var[:]      =[1.0]*global_k
    # dst_grid_frac_var       = nc.createVariable("dst_grid_frac"      ,"f8",("dst_grid_size",               )); dst_grid_frac_var.units='unitless'      ; dst_grid_frac_var[:]      =area2_fraction
    # src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   ));                                           src_address_var[:]        =[n+1 for n in range(global_k)]
    # dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   ));                                           dst_address_var[:]        =[n+1 for n in bottom_index[0:global_k]]
    # remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        ));                                           remap_matrix_var[:,:]     =np.ma.asarray([[val] for val in fraction_of_bottom_normalized])
    # nc.close()
    

def visualize_domain_decomposition(global_settings, model, model_tasks, eg_tasks, grid = "t_grid"):
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

        plt.plot(x_hull, y_hull, 'r-', linewidth=2)
        plt.fill(x_hull, y_hull, 'r', alpha=0.2)

    nc_file = global_settings.root_dir + "/input/" + model + "/mappings/" + grid + "_exchangegrid.nc"
    nc = Dataset(nc_file, 'r')
    grid_corner_lat = nc.variables['grid_corner_lat'][:][:]
    grid_corner_lon = nc.variables['grid_corner_lon'][:][:]
    imask = nc.variables['grid_imask'][:]
    nc.close()
    
    eg_tasks_dict = {}
    for i, task in enumerate(eg_tasks):
        try:
            eg_tasks_dict[task].append(i)
        except:
            eg_tasks_dict[task]=[i]

    #print(eg_tasks_dict)

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

        plt.plot(x_hull, y_hull, 'g--', linewidth=2)
        plt.fill(x_hull, y_hull, 'g', alpha=0.2)

    plt.savefig('domain_decomposition_' + model + "_" + grid + '.pdf')
    #plt.show()