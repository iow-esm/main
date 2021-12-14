# This script will create an exchangegrid file and suitable mappings in the "mappings" folder inside a MOM5 input folder 
# and inside a "mappings" folder in the atmospheric model's input folder.
# The function is called from create_mappings.py 

import os
import netCDF4
import numpy as np

from mapping_helper_functions import get_polys_and_boxes, sub_polybox, get_intersections, polygon_area 


def grid_create_exchangegrid_MOM5(IOW_ESM_ROOT,        # root directory of IOW ESM
                                  atmos_model,         # name of atmospheric model instance
                                  bottom_model,        # name of bottom model instance (MOM5 model)
                                  which_grid):         # 't_grid' or 'u_grid' or 'v_grid'

    ###########################################################
    # STEP 1: DEFINE FILENAMES AND GRID NAMES FOR SCRIP FILES #
    ###########################################################
    scrip_file_1 = IOW_ESM_ROOT+'/input/'+atmos_model +'/mappings/t_grid.nc'         # since CCLM uses a rotated grid, we have to remap momentum to the t-grid.
    scrip_file_2 = IOW_ESM_ROOT+'/input/'+bottom_model+'/mappings/'+which_grid+'.nc'

    bottom_to_atmos_file    = IOW_ESM_ROOT+'/input/'+bottom_model+'/mappings/remap_'+which_grid+'_'+bottom_model+'_to_'+atmos_model +'.nc'
    atmos_to_bottom_file    = IOW_ESM_ROOT+'/input/'+atmos_model +'/mappings/remap_'+which_grid+'_'+atmos_model +'_to_'+bottom_model+'.nc'

    exchange_grid_file      = IOW_ESM_ROOT+'/input/'+bottom_model+'/mappings/'+which_grid+'_exchangegrid.nc'

    bottom_to_exchange_file = IOW_ESM_ROOT+'/input/'+bottom_model+'/mappings/remap_'+which_grid+'_'+bottom_model+'_to_exchangegrid.nc'
    exchange_to_bottom_file = IOW_ESM_ROOT+'/input/'+bottom_model+'/mappings/remap_'+which_grid+'_exchangegrid_to_'+bottom_model+'.nc'
    exchange_to_atmos_file  = IOW_ESM_ROOT+'/input/'+bottom_model+'/mappings/remap_'+which_grid+'_exchangegrid_to_'+atmos_model+'.nc'
   
    atmos_to_exchange_file  = IOW_ESM_ROOT+'/input/'+atmos_model +'/mappings/remap_to_exchangegrid_for_'+bottom_model+'_'+which_grid+'.nc'

    atmos_grid_title        = atmos_model+'_tgrid'
    bottom_grid_title       = bottom_model+'_'+which_grid
    exchangegrid_title      = bottom_model+'_'+which_grid+'_exchangegrid'   # We allow only one atmospheric model but several bottom models
                                                                            # so we must make clear which exchange grid this is.

    ####################################################
    # STEP 2: READ IN MODEL GRID FILES IN SCRIP FORMAT #
    ####################################################
    print('    reading in model grids...')
    nc = netCDF4.Dataset(scrip_file_1, 'r')
    grid_corner_lon1 = nc.variables['grid_corner_lon'][:,:]
    grid_corner_lat1 = nc.variables['grid_corner_lat'][:,:]
    grid_center_lon1 = nc.variables['grid_center_lon'][:]
    grid_center_lat1 = nc.variables['grid_center_lat'][:]
    grid_imask_1     = nc.variables['grid_imask'][:]
    grid_dims_1      = nc.variables['grid_dims'][:]
    nc.close()

    nc = netCDF4.Dataset(scrip_file_2, 'r')
    grid_corner_lon2 = nc.variables['grid_corner_lon'][:,:]
    grid_corner_lat2 = nc.variables['grid_corner_lat'][:,:]
    grid_center_lon2 = nc.variables['grid_center_lon'][:]
    grid_center_lat2 = nc.variables['grid_center_lat'][:]
    grid_imask_2     = nc.variables['grid_imask'][:]
    grid_dims_2      = nc.variables['grid_dims'][:]
    nc.close()

    #######################################################
    # STEP 3: CALCULATE POLYGONS AND THEIR BOUNDING BOXES #
    #######################################################

    print('    calculating bounding boxes for atmos model cells...')
    polybox1 = get_polys_and_boxes(grid_corner_lon1[:,:], grid_corner_lat1[:,:], grid_imask_1[:])
    print('    calculating bounding boxes for bottom model cells...')
    polybox2 = get_polys_and_boxes(grid_corner_lon2[:,:], grid_corner_lat2[:,:], grid_imask_2[:])

    # remove those rows where imask=0
    print('    removing masked points...')
    polybox1 = sub_polybox(polybox1,[x==1 for x in grid_imask_1])
    polybox2 = sub_polybox(polybox2,[x==1 for x in grid_imask_2])

    ####################################################
    # STEP 4: CALCULATE INTERSECTIONS BETWEEN POLYGONS #
    ####################################################
    # To speed this up, we first sort the polygons into boxes of an n x n lat-lon grid.
    # Only cells from identical or adjacent boxes can overlap.
    print('    calculating intersections...')

    # how many points does the bottom model have?
    bottom_points = len(grid_imask_2)

    # We assume that the bottom model's lat-lon extent is the smaller one. 
    # The procedure will work anyway but take longer if the atmos model is the smaller one
    gridsize = int(np.sqrt(bottom_points)/20) # we want roughly 20x20 grid cells per box
    min_lon = min(polybox2[0])
    max_lon = max(polybox2[2])
    min_lat = min(polybox2[1])
    max_lat = max(polybox2[3])

    global_kmax = 4*bottom_points # on average we should not have more than 4 exchange grid cells per bottom grid cell
    cornermax = 100               # be safe on the number of corners we permit for the intersecting polygons

    # initialize lists that will store the information
    atmos_index = [-1 for k in range(global_kmax)]
    bottom_index = [-1 for k in range(global_kmax)]
    corners = [-1 for k in range(global_kmax)]
    poly_x = [[-1000.0 for col in range(cornermax)] for row in range(global_kmax)]
    poly_y = [[-1000.0 for col in range(cornermax)] for row in range(global_kmax)]

    global_k = 0
    for i in range(gridsize):
        # for polybox2 we select those elements whose minlon is exactly in the correct box
        subbox_lon_2 = sub_polybox(polybox2, [(x>=min_lon+i*(max_lon-min_lon)/gridsize)&
                                              (x<min_lon+(i+1)*(max_lon-min_lon)/gridsize) for x in polybox2[0]])
        # for polybox1 we check for maxlon at the left side and allow a larger range at the right side
        subbox_lon_1 = sub_polybox(polybox1, [(x>=min_lon+i*(max_lon-min_lon)/gridsize) for x in polybox1[2]])
        subbox_lon_1 = sub_polybox(subbox_lon_1, [(x<min_lon+(i+2)*(max_lon-min_lon)/gridsize) for x in subbox_lon_1[0]])
        for j in range(gridsize):
            # for polybox2 we select those elements whose minlat is exactly in the correct box
            subbox_lonlat_2 = sub_polybox(subbox_lon_2, [(x>=min_lat+j*(max_lat-min_lat)/gridsize)&
                                                         (x<min_lat+(j+1)*(max_lat-min_lat)/gridsize) for x in subbox_lon_2[1]])
            # for polybox1 we check for maxlat at the left side and allow a larger range at the right side
            subbox_lonlat_1 = sub_polybox(subbox_lon_1, [(x>=min_lat+j*(max_lat-min_lat)/gridsize) for x in subbox_lon_1[3]])
            subbox_lonlat_1 = sub_polybox(subbox_lonlat_1, [(x<min_lat+(j+2)*(max_lat-min_lat)/gridsize) for x in subbox_lonlat_1[1]])
            # print progress
            print('        '+str((i*gridsize+j)*100/(gridsize*gridsize))+'%')
            # call intersection routine
            intersect = get_intersections(subbox_lonlat_1,subbox_lonlat_2, int(2*4*bottom_points/(gridsize*gridsize)), cornermax)
            # first argument returned is the number of intersections found
            k = intersect[0]
            # see if we exceed our limit of intersections:
            if (global_k + k >= global_kmax):
                print('ERROR in grid_create_exchangegrid_MOM5: Too many intersections found between grid cells!')
                print('Please raise global_kmax which is presently global_kmax='+str(global_kmax)+'.')
                return
            # save intersections found in this gridbox to the global list
            atmos_index[global_k:(global_k+k)]=intersect[1][0:k]
            bottom_index[global_k:(global_k+k)]=intersect[2][0:k]
            corners[global_k:(global_k+k)]=intersect[3][0:k]
            poly_x[global_k:(global_k+k)]=intersect[4][0:k]
            poly_y[global_k:(global_k+k)]=intersect[5][0:k]
            global_k = global_k + k
    # search has finished, print global progress
    print('        100.0%')

    ####################################################
    # STEP 5: CALCULATE AREA OF POLYGONS ON THE SPHERE #
    ####################################################
    print('    calculating atmos area...')
    area1_at_activepoints = [polygon_area(polybox1[4][i].exterior.coords.xy[0],polybox1[4][i].exterior.coords.xy[1],1.0) 
                             for i in range(len(polybox1[0]))]
    area1 = [0.0 for i in range(len(grid_imask_1))]
    for i in range(len(polybox1[0])):
        area1[polybox1[5][i]] = area1_at_activepoints[i] # column 5 of polybox1 contains cell index

    print('    calculating bottom area...')
    area2_at_activepoints = [polygon_area(polybox2[4][i].exterior.coords.xy[0],polybox2[4][i].exterior.coords.xy[1],1.0) 
                             for i in range(len(polybox2[0]))]
    area2 = [0.0 for i in range(len(grid_imask_2))]
    for i in range(len(polybox2[0])):
        area2[polybox2[5][i]] = area2_at_activepoints[i] # column 5 of polybox2 contains cell index

    print('    calculating exchangegrid area...')
    area3 = [polygon_area(poly_x[i][0:corners[i]],poly_y[i][0:corners[i]],1.0) for i in range(global_k)]

    print('    calculating exchangegrid fraction of atmos grid...')
    fraction_of_atmos = [area3[i]/area1[atmos_index[i]] for i in range(global_k)] # exchange grid cell area fraction of atmos cell
    area1_fraction = [0.0 for i in range(len(grid_imask_1))]
    for i in range(global_k):  # calculate total fraction of atmos cell covered by all exchange grid cells
        area1_fraction[atmos_index[i]] = area1_fraction[atmos_index[i]] + fraction_of_atmos[i]
    fraction_of_atmos_normalized = fraction_of_atmos[:] # normalize this fraction with the total fraction of the atmospheric cell which is covered
    for i in range(global_k):
        fraction_of_atmos_normalized[i] = fraction_of_atmos_normalized[i] / area1_fraction[atmos_index[i]]

    print('    calculating exchangegrid fraction of bottom grid...')
    fraction_of_bottom = [area3[i]/area2[bottom_index[i]] for i in range(global_k)] # exchange grid cell area fraction of bottom cell
    area2_fraction = [0.0 for i in range(len(grid_imask_2))]
    for i in range(global_k):  # calculate total fraction of bottom cell covered by all exchange grid cells
        area2_fraction[bottom_index[i]] = area2_fraction[bottom_index[i]] + fraction_of_bottom[i]
    fraction_of_bottom_normalized = fraction_of_bottom # normalize this fraction with the total fraction of the bottom cell which is covered
    for i in range(global_k):
        fraction_of_bottom_normalized[i] = fraction_of_bottom_normalized[i] / area2_fraction[bottom_index[i]]

    ####################################
    # STEP 6: WRITE ALL REQUIRED FILES #
    ####################################
    print('    writing first-order conservative mapping files...')

    print('        bottom -> atmos...')
    nc = netCDF4.Dataset(bottom_to_atmos_file,'w')
    nc.title = bottom_to_atmos_file
    nc.normalization = 'no norm' 
    nc.map_method = 'Conservative remapping'
    nc.conventions = "SCRIP" 
    nc.source_grid = bottom_grid_title
    nc.dest_grid = atmos_grid_title
    nc.createDimension("src_grid_size"   ,len(grid_imask_2)  ); src_grid_size_var    = nc.createVariable("src_grid_size"   ,"i4",("src_grid_size"   ,)); src_grid_size_var[:]    = [n+1 for n in range(len(grid_imask_2))]
    nc.createDimension("dst_grid_size"   ,len(grid_imask_1)  ); dst_grid_size_var    = nc.createVariable("dst_grid_size"   ,"i4",("dst_grid_size"   ,)); dst_grid_size_var[:]    = [n+1 for n in range(len(grid_imask_1))]
    nc.createDimension("src_grid_corners"   ,4  ); src_grid_corners_var    = nc.createVariable("src_grid_corners"   ,"i4",("src_grid_corners"   ,)); src_grid_corners_var[:]    = [n+1 for n in range(4)]
    nc.createDimension("dst_grid_corners"   ,4  ); dst_grid_corners_var    = nc.createVariable("dst_grid_corners"   ,"i4",("dst_grid_corners"   ,)); dst_grid_corners_var[:]    = [n+1 for n in range(4)]
    nc.createDimension("src_grid_rank"   ,len(grid_dims_2)   ); src_grid_rank_var    = nc.createVariable("src_grid_rank"   ,"i4",("src_grid_rank"   ,)); src_grid_rank_var[:]    = [n+1 for n in range(len(grid_dims_2))]
    nc.createDimension("dst_grid_rank"   ,len(grid_dims_1)   ); dst_grid_rank_var    = nc.createVariable("dst_grid_rank"   ,"i4",("dst_grid_rank"   ,)); dst_grid_rank_var[:]    = [n+1 for n in range(len(grid_dims_1))]
    nc.createDimension("num_links"   ,global_k   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = [1]
    src_grid_dims_var       = nc.createVariable("src_grid_dims"      ,"i4",("src_grid_rank",               )); src_grid_dims_var.missval=np.int32(-1)  ; src_grid_dims_var[:]      =grid_dims_2
    dst_grid_dims_var       = nc.createVariable("dst_grid_dims"      ,"i4",("dst_grid_rank",               )); dst_grid_dims_var.missval=np.int32(-1)  ; dst_grid_dims_var[:]      =grid_dims_1
    src_grid_center_lat_var = nc.createVariable("src_grid_center_lat","f8",("src_grid_size",               )); src_grid_center_lat_var.units='radians' ; src_grid_center_lat_var[:]=np.deg2rad(grid_center_lat2)
    dst_grid_center_lat_var = nc.createVariable("dst_grid_center_lat","f8",("dst_grid_size",               )); dst_grid_center_lat_var.units='radians' ; dst_grid_center_lat_var[:]=np.deg2rad(grid_center_lat1)
    src_grid_center_lon_var = nc.createVariable("src_grid_center_lon","f8",("src_grid_size",               )); src_grid_center_lon_var.units='radians' ; src_grid_center_lon_var[:]=np.deg2rad(grid_center_lon2)
    dst_grid_center_lon_var = nc.createVariable("dst_grid_center_lon","f8",("dst_grid_size",               )); dst_grid_center_lon_var.units='radians' ; dst_grid_center_lon_var[:]=np.deg2rad(grid_center_lon1)
    src_grid_imask_var      = nc.createVariable("src_grid_imask"     ,"i4",("src_grid_size",               )); src_grid_imask_var.units='unitless'     ; src_grid_imask_var[:]     =grid_imask_2
    dst_grid_imask_var      = nc.createVariable("dst_grid_imask"     ,"i4",("dst_grid_size",               )); dst_grid_imask_var.units='unitless'     ; dst_grid_imask_var[:]     =grid_imask_1
    src_grid_area_var       = nc.createVariable("src_grid_area"      ,"f8",("src_grid_size",               )); src_grid_area_var.units='square radians'; src_grid_area_var[:]      =area2
    dst_grid_area_var       = nc.createVariable("dst_grid_area"      ,"f8",("dst_grid_size",               )); dst_grid_area_var.units='square radians'; dst_grid_area_var[:]      =area1
    src_grid_frac_var       = nc.createVariable("src_grid_frac"      ,"f8",("src_grid_size",               )); src_grid_frac_var.units='unitless'      ; src_grid_frac_var[:]      =area2_fraction
    dst_grid_frac_var       = nc.createVariable("dst_grid_frac"      ,"f8",("dst_grid_size",               )); dst_grid_frac_var.units='unitless'      ; dst_grid_frac_var[:]      =area1_fraction
    src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   ));                                           src_address_var[:]        =[n+1 for n in bottom_index[0:global_k]]
    dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   ));                                           dst_address_var[:]        =[n+1 for n in atmos_index[0:global_k]]
    remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        ));                                           remap_matrix_var[:,:]     =np.ma.asarray([[val] for val in fraction_of_atmos_normalized])
    nc.close()

    print('        atmos -> bottom...')
    nc = netCDF4.Dataset(atmos_to_bottom_file,'w')
    nc.title = atmos_to_bottom_file
    nc.normalization = 'no norm' 
    nc.map_method = 'Conservative remapping'
    nc.conventions = "SCRIP" 
    nc.source_grid = atmos_grid_title
    nc.dest_grid = bottom_grid_title
    nc.createDimension("src_grid_size"   ,len(grid_imask_1)  ); src_grid_size_var    = nc.createVariable("src_grid_size"   ,"i4",("src_grid_size"   ,)); src_grid_size_var[:]    = [n+1 for n in range(len(grid_imask_1))]
    nc.createDimension("dst_grid_size"   ,len(grid_imask_2)  ); dst_grid_size_var    = nc.createVariable("dst_grid_size"   ,"i4",("dst_grid_size"   ,)); dst_grid_size_var[:]    = [n+1 for n in range(len(grid_imask_2))]
    nc.createDimension("src_grid_corners"   ,4  ); src_grid_corners_var    = nc.createVariable("src_grid_corners"   ,"i4",("src_grid_corners"   ,)); src_grid_corners_var[:]    = [n+1 for n in range(4)]
    nc.createDimension("dst_grid_corners"   ,4  ); dst_grid_corners_var    = nc.createVariable("dst_grid_corners"   ,"i4",("dst_grid_corners"   ,)); dst_grid_corners_var[:]    = [n+1 for n in range(4)]
    nc.createDimension("src_grid_rank"   ,len(grid_dims_1)   ); src_grid_rank_var    = nc.createVariable("src_grid_rank"   ,"i4",("src_grid_rank"   ,)); src_grid_rank_var[:]    = [n+1 for n in range(len(grid_dims_1))]
    nc.createDimension("dst_grid_rank"   ,len(grid_dims_1)   ); dst_grid_rank_var    = nc.createVariable("dst_grid_rank"   ,"i4",("dst_grid_rank"   ,)); dst_grid_rank_var[:]    = [n+1 for n in range(len(grid_dims_2))]
    nc.createDimension("num_links"   ,global_k   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = [1]
    src_grid_dims_var       = nc.createVariable("src_grid_dims"      ,"i4",("src_grid_rank",               )); src_grid_dims_var.missval=np.int32(-1)  ; src_grid_dims_var[:]      =grid_dims_1
    dst_grid_dims_var       = nc.createVariable("dst_grid_dims"      ,"i4",("dst_grid_rank",               )); dst_grid_dims_var.missval=np.int32(-1)  ; dst_grid_dims_var[:]      =grid_dims_2
    src_grid_center_lat_var = nc.createVariable("src_grid_center_lat","f8",("src_grid_size",               )); src_grid_center_lat_var.units='radians' ; src_grid_center_lat_var[:]=np.deg2rad(grid_center_lat1)
    dst_grid_center_lat_var = nc.createVariable("dst_grid_center_lat","f8",("dst_grid_size",               )); dst_grid_center_lat_var.units='radians' ; dst_grid_center_lat_var[:]=np.deg2rad(grid_center_lat2)
    src_grid_center_lon_var = nc.createVariable("src_grid_center_lon","f8",("src_grid_size",               )); src_grid_center_lon_var.units='radians' ; src_grid_center_lon_var[:]=np.deg2rad(grid_center_lon1)
    dst_grid_center_lon_var = nc.createVariable("dst_grid_center_lon","f8",("dst_grid_size",               )); dst_grid_center_lon_var.units='radians' ; dst_grid_center_lon_var[:]=np.deg2rad(grid_center_lon2)
    src_grid_imask_var      = nc.createVariable("src_grid_imask"     ,"i4",("src_grid_size",               )); src_grid_imask_var.units='unitless'     ; src_grid_imask_var[:]     =grid_imask_1
    dst_grid_imask_var      = nc.createVariable("dst_grid_imask"     ,"i4",("dst_grid_size",               )); dst_grid_imask_var.units='unitless'     ; dst_grid_imask_var[:]     =grid_imask_2
    src_grid_area_var       = nc.createVariable("src_grid_area"      ,"f8",("src_grid_size",               )); src_grid_area_var.units='square radians'; src_grid_area_var[:]      =area1
    dst_grid_area_var       = nc.createVariable("dst_grid_area"      ,"f8",("dst_grid_size",               )); dst_grid_area_var.units='square radians'; dst_grid_area_var[:]      =area2
    src_grid_frac_var       = nc.createVariable("src_grid_frac"      ,"f8",("src_grid_size",               )); src_grid_frac_var.units='unitless'      ; src_grid_frac_var[:]      =area1_fraction
    dst_grid_frac_var       = nc.createVariable("dst_grid_frac"      ,"f8",("dst_grid_size",               )); dst_grid_frac_var.units='unitless'      ; dst_grid_frac_var[:]      =area2_fraction
    src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   ));                                           src_address_var[:]        =[n+1 for n in atmos_index[0:global_k]]
    dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   ));                                           dst_address_var[:]        =[n+1 for n in bottom_index[0:global_k]]
    remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        ));                                           remap_matrix_var[:,:]     =np.ma.asarray([[val] for val in fraction_of_bottom_normalized])
    nc.close()

    print('    writing exchange grid SCRIP file...')
    nc = netCDF4.Dataset(exchange_grid_file,"w")
    nc.title = exchangegrid_title
    nc.createDimension("grid_size"   ,global_k  ); grid_size_var    = nc.createVariable("grid_size"   ,"i4",("grid_size"   ,)); grid_size_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("grid_corners",max(corners[0:global_k])); grid_corners_var = nc.createVariable("grid_corners","i4",("grid_corners",)); grid_corners_var[:] = [n+1 for n in range(max(corners[0:global_k]))]
    nc.createDimension("grid_rank"   ,1   ); grid_rank_var    = nc.createVariable("grid_rank"   ,"i4",("grid_rank"   ,)); grid_rank_var[:]    = [1]
    grid_dims_var       = nc.createVariable("grid_dims"      ,"i4",("grid_rank",               )); grid_dims_var.missval=np.int32(-1) ; grid_dims_var[:]      =[global_k]
    grid_center_lat_var = nc.createVariable("grid_center_lat","f8",("grid_size",               )); grid_center_lat_var.units="degrees"; grid_center_lat_var[:]=[np.mean([poly_y[k][0:(corners[k]-1)]]) for k in range(global_k)]
    grid_center_lon_var = nc.createVariable("grid_center_lon","f8",("grid_size",               )); grid_center_lon_var.units="degrees"; grid_center_lon_var[:]=[np.mean([poly_x[k][0:(corners[k]-1)]]) for k in range(global_k)]
    grid_imask_var      = nc.createVariable("grid_imask"     ,"i4",("grid_size",               )); grid_imask_var.missval=np.int32(-1); grid_imask_var[:]     =[1]*global_k
    grid_corner_lat_var = nc.createVariable("grid_corner_lat","f8",("grid_size","grid_corners",)); grid_corner_lat_var.units="degrees"; grid_corner_lat_var[:]=np.ma.asarray([[poly_y[k][0:max(corners[0:global_k])]] for k in range(global_k)])
    grid_corner_lon_var = nc.createVariable("grid_corner_lon","f8",("grid_size","grid_corners",)); grid_corner_lon_var.units="degrees"; grid_corner_lon_var[:]=np.ma.asarray([[poly_x[k][0:max(corners[0:global_k])]] for k in range(global_k)])
    grid_area_var       = nc.createVariable("grid_area"      ,"f8",("grid_size",               )); grid_area_var.units      ="square radians"; grid_area_var[:]=area3
    nc.sync()
    nc.close()

    print('    writing exchange grid mapping files...')
    print('    atmos -> exchange...')
    nc = netCDF4.Dataset(atmos_to_exchange_file,'w')
    nc.title = atmos_to_exchange_file
    nc.normalization = 'no norm' 
    nc.map_method = 'Conservative remapping'
    nc.conventions = "SCRIP" 
    nc.source_grid = atmos_grid_title
    nc.dest_grid = exchangegrid_title
    nc.createDimension("src_grid_size"   ,len(grid_imask_1)  ); src_grid_size_var    = nc.createVariable("src_grid_size"   ,"i4",("src_grid_size"   ,)); src_grid_size_var[:]    = [n+1 for n in range(len(grid_imask_1))]
    nc.createDimension("dst_grid_size"   ,global_k  ); dst_grid_size_var    = nc.createVariable("dst_grid_size"   ,"i4",("dst_grid_size"   ,)); dst_grid_size_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("src_grid_corners"   ,4  ); src_grid_corners_var    = nc.createVariable("src_grid_corners"   ,"i4",("src_grid_corners"   ,)); src_grid_corners_var[:]    = [n+1 for n in range(4)]
    nc.createDimension("dst_grid_corners"   ,max(corners[0:global_k])  ); dst_grid_corners_var    = nc.createVariable("dst_grid_corners"   ,"i4",("dst_grid_corners"   ,)); dst_grid_corners_var[:]    = [n+1 for n in range(max(corners[0:global_k]))]
    nc.createDimension("src_grid_rank"   ,len(grid_dims_1)   ); src_grid_rank_var    = nc.createVariable("src_grid_rank"   ,"i4",("src_grid_rank"   ,)); src_grid_rank_var[:]    = [n+1 for n in range(len(grid_dims_1))]
    nc.createDimension("dst_grid_rank"   ,1   ); dst_grid_rank_var    = nc.createVariable("dst_grid_rank"   ,"i4",("dst_grid_rank"   ,)); dst_grid_rank_var[:]    = [1]
    nc.createDimension("num_links"   ,global_k   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = [1]
    src_grid_dims_var       = nc.createVariable("src_grid_dims"      ,"i4",("src_grid_rank",               )); src_grid_dims_var.missval=np.int32(-1)  ; src_grid_dims_var[:]      =grid_dims_1
    dst_grid_dims_var       = nc.createVariable("dst_grid_dims"      ,"i4",("dst_grid_rank",               )); dst_grid_dims_var.missval=np.int32(-1)  ; dst_grid_dims_var[:]      =[global_k]
    src_grid_center_lat_var = nc.createVariable("src_grid_center_lat","f8",("src_grid_size",               )); src_grid_center_lat_var.units='radians' ; src_grid_center_lat_var[:]=np.deg2rad(grid_center_lat1)
    dst_grid_center_lat_var = nc.createVariable("dst_grid_center_lat","f8",("dst_grid_size",               )); dst_grid_center_lat_var.units='radians' ; dst_grid_center_lat_var[:]=np.deg2rad([np.mean([poly_y[k][0:(corners[k]-1)]]) for k in range(global_k)])
    src_grid_center_lon_var = nc.createVariable("src_grid_center_lon","f8",("src_grid_size",               )); src_grid_center_lon_var.units='radians' ; src_grid_center_lon_var[:]=np.deg2rad(grid_center_lon1)
    dst_grid_center_lon_var = nc.createVariable("dst_grid_center_lon","f8",("dst_grid_size",               )); dst_grid_center_lon_var.units='radians' ; dst_grid_center_lon_var[:]=np.deg2rad([np.mean([poly_x[k][0:(corners[k]-1)]]) for k in range(global_k)])
    src_grid_imask_var      = nc.createVariable("src_grid_imask"     ,"i4",("src_grid_size",               )); src_grid_imask_var.units='unitless'     ; src_grid_imask_var[:]     =grid_imask_1
    dst_grid_imask_var      = nc.createVariable("dst_grid_imask"     ,"i4",("dst_grid_size",               )); dst_grid_imask_var.units='unitless'     ; dst_grid_imask_var[:]     =[1]*global_k
    src_grid_area_var       = nc.createVariable("src_grid_area"      ,"f8",("src_grid_size",               )); src_grid_area_var.units='square radians'; src_grid_area_var[:]      =area1
    dst_grid_area_var       = nc.createVariable("dst_grid_area"      ,"f8",("dst_grid_size",               )); dst_grid_area_var.units='square radians'; dst_grid_area_var[:]      =area3
    src_grid_frac_var       = nc.createVariable("src_grid_frac"      ,"f8",("src_grid_size",               )); src_grid_frac_var.units='unitless'      ; src_grid_frac_var[:]      =area1_fraction
    dst_grid_frac_var       = nc.createVariable("dst_grid_frac"      ,"f8",("dst_grid_size",               )); dst_grid_frac_var.units='unitless'      ; dst_grid_frac_var[:]      =[1.0]*global_k
    src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   ));                                           src_address_var[:]        =[n+1 for n in atmos_index[0:global_k]]
    dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   ));                                           dst_address_var[:]        =[n+1 for n in range(global_k)]
    remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        ));                                           remap_matrix_var[:,:]     =np.ma.asarray([[1.0] for k in range(global_k)])
    nc.close()

    print('        exchange -> atmos...')
    nc = netCDF4.Dataset(exchange_to_atmos_file,'w')
    nc.title = exchange_to_atmos_file
    nc.normalization = 'no norm' 
    nc.map_method = 'Conservative remapping'
    nc.conventions = "SCRIP" 
    nc.source_grid = exchangegrid_title
    nc.dest_grid = atmos_grid_title
    nc.createDimension("src_grid_size"   ,global_k  ); src_grid_size_var    = nc.createVariable("src_grid_size"   ,"i4",("src_grid_size"   ,)); src_grid_size_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("dst_grid_size"   ,len(grid_imask_1)  ); dst_grid_size_var    = nc.createVariable("dst_grid_size"   ,"i4",("dst_grid_size"   ,)); dst_grid_size_var[:]    = [n+1 for n in range(len(grid_imask_1))]
    nc.createDimension("src_grid_corners"   ,max(corners[0:global_k])  ); src_grid_corners_var    = nc.createVariable("src_grid_corners"   ,"i4",("src_grid_corners"   ,)); src_grid_corners_var[:]    = [n+1 for n in range(max(corners[0:global_k]))]
    nc.createDimension("dst_grid_corners"   ,4  ); dst_grid_corners_var    = nc.createVariable("dst_grid_corners"   ,"i4",("dst_grid_corners"   ,)); dst_grid_corners_var[:]    = [n+1 for n in range(4)]
    nc.createDimension("src_grid_rank"   ,1   ); src_grid_rank_var    = nc.createVariable("src_grid_rank"   ,"i4",("src_grid_rank"   ,)); src_grid_rank_var[:]    = [1]
    nc.createDimension("dst_grid_rank"   ,len(grid_dims_1)   ); dst_grid_rank_var    = nc.createVariable("dst_grid_rank"   ,"i4",("dst_grid_rank"   ,)); dst_grid_rank_var[:]    = [n+1 for n in range(len(grid_dims_1))]
    nc.createDimension("num_links"   ,global_k   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = [1]
    src_grid_dims_var       = nc.createVariable("src_grid_dims"      ,"i4",("src_grid_rank",               )); src_grid_dims_var.missval=np.int32(-1)  ; src_grid_dims_var[:]      =[global_k]
    dst_grid_dims_var       = nc.createVariable("dst_grid_dims"      ,"i4",("dst_grid_rank",               )); dst_grid_dims_var.missval=np.int32(-1)  ; dst_grid_dims_var[:]      =grid_dims_1
    src_grid_center_lat_var = nc.createVariable("src_grid_center_lat","f8",("src_grid_size",               )); src_grid_center_lat_var.units='radians' ; src_grid_center_lat_var[:]=np.deg2rad([np.mean([poly_y[k][0:(corners[k]-1)]]) for k in range(global_k)])
    dst_grid_center_lat_var = nc.createVariable("dst_grid_center_lat","f8",("dst_grid_size",               )); dst_grid_center_lat_var.units='radians' ; dst_grid_center_lat_var[:]=np.deg2rad(grid_center_lat1)
    src_grid_center_lon_var = nc.createVariable("src_grid_center_lon","f8",("src_grid_size",               )); src_grid_center_lon_var.units='radians' ; src_grid_center_lon_var[:]=np.deg2rad([np.mean([poly_x[k][0:(corners[k]-1)]]) for k in range(global_k)])
    dst_grid_center_lon_var = nc.createVariable("dst_grid_center_lon","f8",("dst_grid_size",               )); dst_grid_center_lon_var.units='radians' ; dst_grid_center_lon_var[:]=np.deg2rad(grid_center_lon1)
    src_grid_imask_var      = nc.createVariable("src_grid_imask"     ,"i4",("src_grid_size",               )); src_grid_imask_var.units='unitless'     ; src_grid_imask_var[:]     =[1]*global_k
    dst_grid_imask_var      = nc.createVariable("dst_grid_imask"     ,"i4",("dst_grid_size",               )); dst_grid_imask_var.units='unitless'     ; dst_grid_imask_var[:]     =grid_imask_1
    src_grid_area_var       = nc.createVariable("src_grid_area"      ,"f8",("src_grid_size",               )); src_grid_area_var.units='square radians'; src_grid_area_var[:]      =area3
    dst_grid_area_var       = nc.createVariable("dst_grid_area"      ,"f8",("dst_grid_size",               )); dst_grid_area_var.units='square radians'; dst_grid_area_var[:]      =area1
    src_grid_frac_var       = nc.createVariable("src_grid_frac"      ,"f8",("src_grid_size",               )); src_grid_frac_var.units='unitless'      ; src_grid_frac_var[:]      =[1.0]*global_k
    dst_grid_frac_var       = nc.createVariable("dst_grid_frac"      ,"f8",("dst_grid_size",               )); dst_grid_frac_var.units='unitless'      ; dst_grid_frac_var[:]      =area1_fraction
    src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   ));                                           src_address_var[:]        =[n+1 for n in range(global_k)]
    dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   ));                                           dst_address_var[:]        =[n+1 for n in atmos_index[0:global_k]]
    remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        ));                                           remap_matrix_var[:,:]     =np.ma.asarray([[val] for val in fraction_of_atmos_normalized])
    nc.close()

    print('        bottom -> exchange...')
    nc = netCDF4.Dataset(bottom_to_exchange_file,'w')
    nc.title = bottom_to_exchange_file
    nc.normalization = 'no norm' 
    nc.map_method = 'Conservative remapping'
    nc.conventions = "SCRIP" 
    nc.source_grid = bottom_grid_title
    nc.dest_grid = exchangegrid_title
    nc.createDimension("src_grid_size"   ,len(grid_imask_2)  ); src_grid_size_var    = nc.createVariable("src_grid_size"   ,"i4",("src_grid_size"   ,)); src_grid_size_var[:]    = [n+1 for n in range(len(grid_imask_2))]
    nc.createDimension("dst_grid_size"   ,global_k  ); dst_grid_size_var    = nc.createVariable("dst_grid_size"   ,"i4",("dst_grid_size"   ,)); dst_grid_size_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("src_grid_corners"   ,4  ); src_grid_corners_var    = nc.createVariable("src_grid_corners"   ,"i4",("src_grid_corners"   ,)); src_grid_corners_var[:]    = [n+1 for n in range(4)]
    nc.createDimension("dst_grid_corners"   ,max(corners[0:global_k])  ); dst_grid_corners_var    = nc.createVariable("dst_grid_corners"   ,"i4",("dst_grid_corners"   ,)); dst_grid_corners_var[:]    = [n+1 for n in range(max(corners[0:global_k]))]
    nc.createDimension("src_grid_rank"   ,len(grid_dims_2)   ); src_grid_rank_var    = nc.createVariable("src_grid_rank"   ,"i4",("src_grid_rank"   ,)); src_grid_rank_var[:]    = [n+1 for n in range(len(grid_dims_2))]
    nc.createDimension("dst_grid_rank"   ,1   ); dst_grid_rank_var    = nc.createVariable("dst_grid_rank"   ,"i4",("dst_grid_rank"   ,)); dst_grid_rank_var[:]    = [n+1 for n in range(1)]
    nc.createDimension("num_links"   ,global_k   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = [1]
    src_grid_dims_var       = nc.createVariable("src_grid_dims"      ,"i4",("src_grid_rank",               )); src_grid_dims_var.missval=np.int32(-1)  ; src_grid_dims_var[:]      =grid_dims_2
    dst_grid_dims_var       = nc.createVariable("dst_grid_dims"      ,"i4",("dst_grid_rank",               )); dst_grid_dims_var.missval=np.int32(-1)  ; dst_grid_dims_var[:]      =[global_k]
    src_grid_center_lat_var = nc.createVariable("src_grid_center_lat","f8",("src_grid_size",               )); src_grid_center_lat_var.units='radians' ; src_grid_center_lat_var[:]=np.deg2rad(grid_center_lat2)
    dst_grid_center_lat_var = nc.createVariable("dst_grid_center_lat","f8",("dst_grid_size",               )); dst_grid_center_lat_var.units='radians' ; dst_grid_center_lat_var[:]=np.deg2rad([np.mean([poly_y[k][0:(corners[k]-1)]]) for k in range(global_k)])
    src_grid_center_lon_var = nc.createVariable("src_grid_center_lon","f8",("src_grid_size",               )); src_grid_center_lon_var.units='radians' ; src_grid_center_lon_var[:]=np.deg2rad(grid_center_lon2)
    dst_grid_center_lon_var = nc.createVariable("dst_grid_center_lon","f8",("dst_grid_size",               )); dst_grid_center_lon_var.units='radians' ; dst_grid_center_lon_var[:]=np.deg2rad([np.mean([poly_x[k][0:(corners[k]-1)]]) for k in range(global_k)])
    src_grid_imask_var      = nc.createVariable("src_grid_imask"     ,"i4",("src_grid_size",               )); src_grid_imask_var.units='unitless'     ; src_grid_imask_var[:]     =grid_imask_2
    dst_grid_imask_var      = nc.createVariable("dst_grid_imask"     ,"i4",("dst_grid_size",               )); dst_grid_imask_var.units='unitless'     ; dst_grid_imask_var[:]     =[1]*global_k
    src_grid_area_var       = nc.createVariable("src_grid_area"      ,"f8",("src_grid_size",               )); src_grid_area_var.units='square radians'; src_grid_area_var[:]      =area2
    dst_grid_area_var       = nc.createVariable("dst_grid_area"      ,"f8",("dst_grid_size",               )); dst_grid_area_var.units='square radians'; dst_grid_area_var[:]      =area3
    src_grid_frac_var       = nc.createVariable("src_grid_frac"      ,"f8",("src_grid_size",               )); src_grid_frac_var.units='unitless'      ; src_grid_frac_var[:]      =area2_fraction
    dst_grid_frac_var       = nc.createVariable("dst_grid_frac"      ,"f8",("dst_grid_size",               )); dst_grid_frac_var.units='unitless'      ; dst_grid_frac_var[:]      =[1.0]*global_k
    src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   ));                                           src_address_var[:]        =[n+1 for n in bottom_index[0:global_k]]
    dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   ));                                           dst_address_var[:]        =[n+1 for n in range(global_k)]
    remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        ));                                           remap_matrix_var[:,:]     =np.ma.asarray([[1.0] for k in range(global_k)])
    nc.close()

    print('        exchange -> bottom...')
    nc = netCDF4.Dataset(exchange_to_bottom_file,'w')
    nc.title = exchange_to_bottom_file
    nc.normalization = 'no norm' 
    nc.map_method = 'Conservative remapping'
    nc.conventions = "SCRIP" 
    nc.source_grid = exchangegrid_title
    nc.dest_grid = bottom_grid_title
    nc.createDimension("src_grid_size"   ,global_k ); src_grid_size_var    = nc.createVariable("src_grid_size"   ,"i4",("src_grid_size"   ,)); src_grid_size_var[:]    = [n+1 for n in range(global_k)]
    nc.createDimension("dst_grid_size"   ,len(grid_imask_2)  ); dst_grid_size_var    = nc.createVariable("dst_grid_size"   ,"i4",("dst_grid_size"   ,)); dst_grid_size_var[:]    = [n+1 for n in range(len(grid_imask_2))]
    nc.createDimension("src_grid_corners"   ,max(corners[0:global_k])  ); src_grid_corners_var    = nc.createVariable("src_grid_corners"   ,"i4",("src_grid_corners"   ,)); src_grid_corners_var[:]    = [n+1 for n in range(max(corners[0:global_k]))]
    nc.createDimension("dst_grid_corners"   ,4  ); dst_grid_corners_var    = nc.createVariable("dst_grid_corners"   ,"i4",("dst_grid_corners"   ,)); dst_grid_corners_var[:]    = [n+1 for n in range(4)]
    nc.createDimension("src_grid_rank"   ,1   ); src_grid_rank_var    = nc.createVariable("src_grid_rank"   ,"i4",("src_grid_rank"   ,)); src_grid_rank_var[:]    = [1]
    nc.createDimension("dst_grid_rank"   ,len(grid_dims_1)   ); dst_grid_rank_var    = nc.createVariable("dst_grid_rank"   ,"i4",("dst_grid_rank"   ,)); dst_grid_rank_var[:]    = [n+1 for n in range(len(grid_dims_2))]
    nc.createDimension("num_links"   ,global_k   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = np.arange(global_k)
    nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = np.arange(1)
    src_grid_dims_var       = nc.createVariable("src_grid_dims"      ,"i4",("src_grid_rank",               )); src_grid_dims_var.missval=np.int32(-1)  ; src_grid_dims_var[:]      =[global_k]
    dst_grid_dims_var       = nc.createVariable("dst_grid_dims"      ,"i4",("dst_grid_rank",               )); dst_grid_dims_var.missval=np.int32(-1)  ; dst_grid_dims_var[:]      =grid_dims_2
    src_grid_center_lat_var = nc.createVariable("src_grid_center_lat","f8",("src_grid_size",               )); src_grid_center_lat_var.units='radians' ; src_grid_center_lat_var[:]=np.deg2rad([np.mean([poly_y[k][0:(corners[k]-1)]]) for k in range(global_k)])
    dst_grid_center_lat_var = nc.createVariable("dst_grid_center_lat","f8",("dst_grid_size",               )); dst_grid_center_lat_var.units='radians' ; dst_grid_center_lat_var[:]=np.deg2rad(grid_center_lat2)
    src_grid_center_lon_var = nc.createVariable("src_grid_center_lon","f8",("src_grid_size",               )); src_grid_center_lon_var.units='radians' ; src_grid_center_lon_var[:]=np.deg2rad([np.mean([poly_x[k][0:(corners[k]-1)]]) for k in range(global_k)])
    dst_grid_center_lon_var = nc.createVariable("dst_grid_center_lon","f8",("dst_grid_size",               )); dst_grid_center_lon_var.units='radians' ; dst_grid_center_lon_var[:]=np.deg2rad(grid_center_lon2)
    src_grid_imask_var      = nc.createVariable("src_grid_imask"     ,"i4",("src_grid_size",               )); src_grid_imask_var.units='unitless'     ; src_grid_imask_var[:]     =[1]*global_k
    dst_grid_imask_var      = nc.createVariable("dst_grid_imask"     ,"i4",("dst_grid_size",               )); dst_grid_imask_var.units='unitless'     ; dst_grid_imask_var[:]     =grid_imask_2
    src_grid_area_var       = nc.createVariable("src_grid_area"      ,"f8",("src_grid_size",               )); src_grid_area_var.units='square radians'; src_grid_area_var[:]      =area3
    dst_grid_area_var       = nc.createVariable("dst_grid_area"      ,"f8",("dst_grid_size",               )); dst_grid_area_var.units='square radians'; dst_grid_area_var[:]      =area2
    src_grid_frac_var       = nc.createVariable("src_grid_frac"      ,"f8",("src_grid_size",               )); src_grid_frac_var.units='unitless'      ; src_grid_frac_var[:]      =[1.0]*global_k
    dst_grid_frac_var       = nc.createVariable("dst_grid_frac"      ,"f8",("dst_grid_size",               )); dst_grid_frac_var.units='unitless'      ; dst_grid_frac_var[:]      =area2_fraction
    src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   ));                                           src_address_var[:]        =[n+1 for n in range(global_k)]
    dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   ));                                           dst_address_var[:]        =[n+1 for n in bottom_index[0:global_k]]
    remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        ));                                           remap_matrix_var[:,:]     =np.ma.asarray([[val] for val in fraction_of_bottom_normalized])
    nc.close()

    return
