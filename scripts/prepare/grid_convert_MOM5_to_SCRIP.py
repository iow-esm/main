# This script will create a "mappings" folder inside a MOM5 input folder and create files t_grid.nc, u_grid.nc and v_grid.nc in SCRIP format.
# The function is called from create_mappings.py 

import os
from netCDF4 import Dataset
import numpy as np

def grid_convert_MOM5_to_SCRIP(IOW_ESM_ROOT,        # root directory of IOW ESM
                               my_directory):       # name of this model instance

    # STEP 1: CREATE EMPTY "mappings" SUBDIRECTORY
    full_directory = IOW_ESM_ROOT+'/input/'+my_directory
    if (os.path.isdir(full_directory+'/mappings')):
        os.system('rm -r '+full_directory+'/mappings')
    os.system('mkdir '+full_directory+'/mappings')

    # STEP 2: CHECK IF grid_spec.nc EXISTS
    if not (os.path.isfile(full_directory+'/INPUT/grid_spec.nc')):
        print('ERROR in grid_convert_MOM5_to_SCRIP: File '+full_directory+'/INPUT/grid_spec.nc not found.')
        return

    # STEP 3: CONVERT THE GRIDS TO SCRIP FORMAT
    inputfile = full_directory+'/INPUT/grid_spec.nc'
    t_grid_file = full_directory+'/mappings/t_grid.nc'
    u_grid_file = full_directory+'/mappings/u_grid.nc'
    v_grid_file = full_directory+'/mappings/v_grid.nc'   # in case of MOM5, both u and v grid are actually the c-grid
    t_grid_title = my_directory+'_t_grid'
    u_grid_title = my_directory+'_u_grid'
    v_grid_title = my_directory+'_v_grid'

    # open dataset
    nc = Dataset(inputfile,"r")

    # get centers and corners of cells
    x_t      = nc.variables['x_T'     ][:,:]
    x_vert_t = nc.variables['x_vert_T'][:,:,:]
    y_t      = nc.variables['y_T'     ][:,:]
    y_vert_t = nc.variables['y_vert_T'][:,:,:]
    x_c      = nc.variables['x_C'     ][:,:]
    x_vert_c = nc.variables['x_vert_C'][:,:,:]
    y_c      = nc.variables['y_C'     ][:,:]
    y_vert_c = nc.variables['y_vert_C'][:,:,:]
    grid_dims = x_t.shape

    # get info whether cells are active
    wet_t    = nc.variables['wet'     ][:,:]
    wet_c    = nc.variables['wet'     ][:,:]
    wet_c[:,:]=0.0
    for i in range(grid_dims[0]-1):
        for j in range(grid_dims[1]-1):
            wet_c[i,j] = wet_t[i,j]*wet_t[i+1,j]*wet_t[i,j+1]*wet_t[i+1,j+1]

    nc.close()

    # define axis indexes
    n_grid_cells = np.prod(grid_dims)
    n_grid_corners = 4
    n_grid_rank = 2
    grid_cell_index = np.arange(n_grid_cells)
    grid_corners = np.arange(n_grid_corners)
    grid_rank    = np.arange(n_grid_rank)

    # get values for t grid
    grid_center_lon = x_t.flatten()
    grid_center_lat = y_t.flatten()
    grid_imask      = wet_t.flatten()
    grid_imask      = [int(x) for x in grid_imask]
    grid_corner_lon = np.ma.asarray([[np.nan for col in grid_corners] for row in grid_cell_index])
    grid_corner_lat = np.ma.asarray([[np.nan for col in grid_corners] for row in grid_cell_index])
    for i in range(grid_dims[0]):    # note that i and j are changed compared to typical notation
        for j in range (grid_dims[1]):
            grid_center_lon[i*grid_dims[1]+j] = x_t[i,j]
            grid_center_lat[i*grid_dims[1]+j] = y_t[i,j]
            grid_imask     [i*grid_dims[1]+j] = int(wet_t[i,j])
            for k in grid_corners:
                grid_corner_lon[i*grid_dims[1]+j,k] = x_vert_t[k,i,j]
                grid_corner_lat[i*grid_dims[1]+j,k] = y_vert_t[k,i,j]

    # delete t-grid file if it exists
    if os.path.isfile(t_grid_file):
        os.remove(t_grid_file)
    # write t grid file
    nc = Dataset(t_grid_file,"w")
    nc.title = t_grid_title
    nc.createDimension("grid_size"   ,n_grid_cells  ); grid_size_var    = nc.createVariable("grid_size"   ,"i4",("grid_size"   ,)); grid_size_var[:]    = grid_cell_index
    nc.createDimension("grid_corners",n_grid_corners); grid_corners_var = nc.createVariable("grid_corners","i4",("grid_corners",)); grid_corners_var[:] = grid_corners
    nc.createDimension("grid_rank"   ,n_grid_rank   ); grid_rank_var    = nc.createVariable("grid_rank"   ,"i4",("grid_rank"   ,)); grid_rank_var[:]    = grid_rank
    grid_dims_var       = nc.createVariable("grid_dims"      ,"i4",("grid_rank",               )); grid_dims_var.missval=np.int32(-1) ; grid_dims_var[:]      =[grid_dims[1],grid_dims[0]]
    grid_center_lat_var = nc.createVariable("grid_center_lat","f8",("grid_size",               )); grid_center_lat_var.units="degrees"; grid_center_lat_var[:]=grid_center_lat
    grid_center_lon_var = nc.createVariable("grid_center_lon","f8",("grid_size",               )); grid_center_lon_var.units="degrees"; grid_center_lon_var[:]=grid_center_lon
    grid_imask_var      = nc.createVariable("grid_imask"     ,"i4",("grid_size",               )); grid_imask_var.missval=np.int32(-1); grid_imask_var[:]     =grid_imask
    grid_corner_lat_var = nc.createVariable("grid_corner_lat","f8",("grid_size","grid_corners",)); grid_corner_lat_var.units="degrees"; grid_corner_lat_var[:]=grid_corner_lat
    grid_corner_lon_var = nc.createVariable("grid_corner_lon","f8",("grid_size","grid_corners",)); grid_corner_lon_var.units="degrees"; grid_corner_lon_var[:]=grid_corner_lon
    nc.sync()
    nc.close()

    # get values for c grid
    grid_center_lon = x_c.flatten()
    grid_center_lat = y_c.flatten()
    grid_imask      = wet_c.flatten()
    grid_imask      = [int(x) for x in grid_imask]
    grid_corner_lon = np.ma.asarray([[np.nan for col in grid_corners] for row in grid_cell_index])
    grid_corner_lat = np.ma.asarray([[np.nan for col in grid_corners] for row in grid_cell_index])
    for i in range(grid_dims[0]):    #note that i and j are changed compared to typical notation
        for j in range (grid_dims[1]):
            grid_center_lon[i*grid_dims[1]+j] = x_c[i,j]
            grid_center_lat[i*grid_dims[1]+j] = y_c[i,j]
            grid_imask     [i*grid_dims[1]+j] = int(wet_c[i,j])
            for k in grid_corners:
                grid_corner_lon[i*grid_dims[1]+j,k] = x_vert_c[k,i,j]
                grid_corner_lat[i*grid_dims[1]+j,k] = y_vert_c[k,i,j]

    # delete u-grid file if it exists
    if os.path.isfile(u_grid_file):
        os.remove(u_grid_file)
    # write u grid file
    nc = Dataset(u_grid_file,"w")
    nc.title = u_grid_title
    nc.createDimension("grid_size"   ,n_grid_cells  ); grid_size_var    = nc.createVariable("grid_size"   ,"i4",("grid_size"   ,)); grid_size_var[:]    = grid_cell_index
    nc.createDimension("grid_corners",n_grid_corners); grid_corners_var = nc.createVariable("grid_corners","i4",("grid_corners",)); grid_corners_var[:] = grid_corners
    nc.createDimension("grid_rank"   ,n_grid_rank   ); grid_rank_var    = nc.createVariable("grid_rank"   ,"i4",("grid_rank"   ,)); grid_rank_var[:]    = grid_rank
    grid_dims_var       = nc.createVariable("grid_dims"      ,"i4",("grid_rank",               )); grid_dims_var.missval=np.int32(-1) ; grid_dims_var[:]      =[grid_dims[1],grid_dims[0]]
    grid_center_lat_var = nc.createVariable("grid_center_lat","f8",("grid_size",               )); grid_center_lat_var.units="degrees"; grid_center_lat_var[:]=grid_center_lat
    grid_center_lon_var = nc.createVariable("grid_center_lon","f8",("grid_size",               )); grid_center_lon_var.units="degrees"; grid_center_lon_var[:]=grid_center_lon
    grid_imask_var      = nc.createVariable("grid_imask"     ,"i4",("grid_size",               )); grid_imask_var.missval=np.int32(-1); grid_imask_var[:]     =grid_imask
    grid_corner_lat_var = nc.createVariable("grid_corner_lat","f8",("grid_size","grid_corners",)); grid_corner_lat_var.units="degrees"; grid_corner_lat_var[:]=grid_corner_lat
    grid_corner_lon_var = nc.createVariable("grid_corner_lon","f8",("grid_size","grid_corners",)); grid_corner_lon_var.units="degrees"; grid_corner_lon_var[:]=grid_corner_lon
    nc.sync()
    nc.close()

    # delete v-grid file if it exists
    if os.path.isfile(v_grid_file):
        os.remove(v_grid_file)
    # write v grid file
    nc = Dataset(v_grid_file,"w")
    nc.title = v_grid_title
    nc.createDimension("grid_size"   ,n_grid_cells  ); grid_size_var    = nc.createVariable("grid_size"   ,"i4",("grid_size"   ,)); grid_size_var[:]    = grid_cell_index
    nc.createDimension("grid_corners",n_grid_corners); grid_corners_var = nc.createVariable("grid_corners","i4",("grid_corners",)); grid_corners_var[:] = grid_corners
    nc.createDimension("grid_rank"   ,n_grid_rank   ); grid_rank_var    = nc.createVariable("grid_rank"   ,"i4",("grid_rank"   ,)); grid_rank_var[:]    = grid_rank
    grid_dims_var       = nc.createVariable("grid_dims"      ,"i4",("grid_rank",               )); grid_dims_var.missval=np.int32(-1) ; grid_dims_var[:]      =grid_dims
    grid_center_lat_var = nc.createVariable("grid_center_lat","f8",("grid_size",               )); grid_center_lat_var.units="degrees"; grid_center_lat_var[:]=grid_center_lat
    grid_center_lon_var = nc.createVariable("grid_center_lon","f8",("grid_size",               )); grid_center_lon_var.units="degrees"; grid_center_lon_var[:]=grid_center_lon
    grid_imask_var      = nc.createVariable("grid_imask"     ,"i4",("grid_size",               )); grid_imask_var.missval=np.int32(-1); grid_imask_var[:]     =grid_imask
    grid_corner_lat_var = nc.createVariable("grid_corner_lat","f8",("grid_size","grid_corners",)); grid_corner_lat_var.units="degrees"; grid_corner_lat_var[:]=grid_corner_lat
    grid_corner_lon_var = nc.createVariable("grid_corner_lon","f8",("grid_size","grid_corners",)); grid_corner_lon_var.units="degrees"; grid_corner_lon_var[:]=grid_corner_lon
    nc.sync()
    nc.close()
    
    return
