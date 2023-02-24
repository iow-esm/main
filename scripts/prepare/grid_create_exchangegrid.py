# This script will create an exchangegrid file and suitable mappings in the "mappings" folder inside a MOM5 input folder 
# and inside a "mappings" folder in the atmospheric model's input folder.
# The function is called from create_mappings.py 


import numpy as np

from grids import Grid, GridManager


def grid_create_exchangegrid(global_settings,        # root directory of IOW ESM
                                  atmos_model,         # name of atmospheric model instance
                                  bottom_model,        # name of bottom model instance (MOM5 model)
                                  which_grid):         # 't_grid' or 'u_grid' or 'v_grid'

    ###########################################################
    # STEP 1: DEFINE FILENAMES AND GRID NAMES FOR SCRIP FILES #
    ###########################################################
    scrip_file_1 = global_settings.input_dir+'/'+atmos_model +'/mappings/t_grid.nc'         # since CCLM uses a rotated grid, we have to remap momentum to the t-grid.
    scrip_file_2 = global_settings.input_dir+'/'+bottom_model+'/mappings/'+which_grid+'.nc'

    bottom_to_atmos_file    = global_settings.input_dir+'/'+bottom_model+'/mappings/remap_'+which_grid+'_'+bottom_model+'_to_'+atmos_model +'.nc'
    atmos_to_bottom_file    = global_settings.input_dir+'/'+atmos_model +'/mappings/remap_'+which_grid+'_'+atmos_model +'_to_'+bottom_model+'.nc'

    exchange_grid_file      = global_settings.input_dir+'/'+bottom_model+'/mappings/'+which_grid+'_exchangegrid.nc'
    intersection_grid_file      = global_settings.input_dir+'/'+bottom_model+'/mappings/'+which_grid+'_intersectiongrid.nc'

    bottom_to_exchange_file = global_settings.input_dir+'/'+bottom_model+'/mappings/remap_'+which_grid+'_'+bottom_model+'_to_exchangegrid.nc'
    exchange_to_bottom_file = global_settings.input_dir+'/'+bottom_model+'/mappings/remap_'+which_grid+'_exchangegrid_to_'+bottom_model+'.nc'
    exchange_to_atmos_file  = global_settings.input_dir+'/'+bottom_model+'/mappings/remap_'+which_grid+'_exchangegrid_to_'+atmos_model+'.nc'
   
    atmos_to_exchange_file  = global_settings.input_dir+'/'+atmos_model +'/mappings/remap_to_exchangegrid_for_'+bottom_model+'_'+which_grid+'.nc'

    atmos_grid_title        = atmos_model+'_t_grid'
    bottom_grid_title       = bottom_model+'_'+which_grid
    exchangegrid_title      = bottom_model+'_'+which_grid+'_exchangegrid'   # We allow only one atmospheric model but several bottom models
                                                                            # so we must make clear which exchange grid this is.

    intersection_grid_title      = bottom_model+'_'+which_grid+'_intersectiongrid'        

    exchange_grid_type = global_settings.exchange_grid_type

    ####################################################
    # STEP 2: READ IN MODEL GRID FILES IN SCRIP FORMAT #
    ####################################################
    print('    reading in model grids...')

    atmos_grid = Grid(from_grid=scrip_file_1, title=atmos_grid_title, grid_corners=4)
    bottom_grid = Grid(from_grid=scrip_file_2, title=bottom_grid_title, grid_corners=4) # TODO: corners should be stored in scrip file

    #######################################################
    # STEP 3: CALCULATE POLYGONS AND THEIR BOUNDING BOXES #
    #######################################################

    if exchange_grid_type == "atmos":
        exchange_grid = atmos_grid
    elif exchange_grid_type == "bottom":
        exchange_grid = bottom_grid
    else:  # default
        exchange_grid = None

    ####################################
    # STEP 6: WRITE ALL REQUIRED FILES #
    ####################################
    print('    contrstructing relevant grids from '+atmos_grid.title+' and '+bottom_grid.title+'...')
    
    if exchange_grid is None:
        exchange_grid_name = "intersection_grid"
    else:
        exchange_grid_name = exchange_grid.title

    print('    with exchange grid: '+exchange_grid_name+'...')
    grids_atmos_bottom = GridManager(atmos_grid, bottom_grid, exchange_grid)
    print('    ...done.')

    print('    write intersection grid file')
    grids_atmos_bottom.intersection_grid.title = intersection_grid_title
    grids_atmos_bottom.intersection_grid.write(intersection_grid_file)

    print('    write exchange grid file')
    grids_atmos_bottom.exchange_grid.title = exchangegrid_title
    grids_atmos_bottom.exchange_grid.write(exchange_grid_file)

    print('    writing first-order conservative mapping files...')
    print('    atmos -> bottom...')
    grids_atmos_bottom.write_remapping(atmos_to_bottom_file, atmos_grid, bottom_grid)

    print('    bottom -> atmos...')
    grids_atmos_bottom.write_remapping(bottom_to_atmos_file, bottom_grid, atmos_grid)

    # mappings from or to exchange grid
    exchange_grid = grids_atmos_bottom.exchange_grid # to shorten the following lines

    print('    atmos -> exchange...')
    grids_atmos_bottom.write_remapping(atmos_to_exchange_file, atmos_grid, exchange_grid) 

    print('    exchange -> atmos...')
    grids_atmos_bottom.write_remapping(exchange_to_atmos_file, exchange_grid, atmos_grid)

    print('    bottom -> exchange...')
    grids_atmos_bottom.write_remapping(bottom_to_exchange_file, bottom_grid, exchange_grid)    

    print('    exchange -> bottom...')
    grids_atmos_bottom.write_remapping(exchange_to_bottom_file, exchange_grid, bottom_grid)

    return
