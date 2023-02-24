# This script will create a mapping between an individual bottom model's t grid and u/v grid.
# To do so, the mapping (back and forth) is first calculated on the original model grid.
# The method is identical to the exchange grid calculation.
# Then, the final mapping is created by matrix multiplications which mean consecutive remappings:
# exchange grid t_grid -> original t_grid -> original u_grid -> exchange grid u_grid
# exchange grid u_grid -> original u_grid -> original t_grid -> exchange grid t_grid
# This is necessary because the exchange grid cells have, in the worst case, no overlap.


import numpy as np
from scipy.sparse import coo_matrix, csr_matrix

from grids import Grid, GridManager
import netCDF4


def grid_create_uv_t_regridding(global_settings,        # root directory of IOW ESM
                                bottom_model,        # name of bottom model instance (MOM5 model)
                                which_grid):         # 'u_grid' or 'v_grid'

    ########################################################################
    # STEP 1: DEFINE FILENAMES AND GRID NAMES FOR BOTTOM MODEL SCRIP FILES #
    ########################################################################
    scrip_file_1       = global_settings.input_dir+'/'+bottom_model+'/mappings/t_grid.nc'         
    scrip_file_2       = global_settings.input_dir+'/'+bottom_model+'/mappings/'+which_grid+'.nc'

    t_to_u_file_orig   = global_settings.input_dir+'/'+bottom_model+'/mappings/regrid_original_t_grid_'+bottom_model+'_to_'+which_grid+'.nc'
    u_to_t_file_orig   = global_settings.input_dir+'/'+bottom_model+'/mappings/regrid_original_'+which_grid+'_'+bottom_model+'_to_t_grid.nc'

    t_to_exchange_file = global_settings.input_dir+'/'+bottom_model+'/mappings/remap_t_grid_'+bottom_model+'_to_exchangegrid.nc'
    exchange_to_t_file = global_settings.input_dir+'/'+bottom_model+'/mappings/remap_t_grid_exchangegrid_to_'+bottom_model+'.nc'
    
    u_to_exchange_file = global_settings.input_dir+'/'+bottom_model+'/mappings/remap_'+which_grid+'_'+bottom_model+'_to_exchangegrid.nc'
    exchange_to_u_file = global_settings.input_dir+'/'+bottom_model+'/mappings/remap_'+which_grid+'_exchangegrid_to_'+bottom_model+'.nc'
    
    t_to_u_file        = global_settings.input_dir+'/'+bottom_model+'/mappings/regrid_t_grid_'+bottom_model+'_to_'+which_grid+'.nc'
    u_to_t_file        = global_settings.input_dir+'/'+bottom_model+'/mappings/regrid_'+which_grid+'_'+bottom_model+'_to_t_grid.nc'

    bottom_grid_title       = bottom_model+'_'+which_grid
    bottom_t_grid_title     = bottom_model+'_t_grid'
    exchangegrid_title      = bottom_model+'_'+which_grid+'_exchangegrid'   # We allow only one atmospheric model but several bottom models
                                                                            # so we must make clear which exchange grid this is.

    ####################################################
    # STEP 2: READ IN MODEL GRID FILES IN SCRIP FORMAT #
    ####################################################
    print('    reading in model grids...')

    t_grid = Grid(from_grid=scrip_file_1, title=bottom_t_grid_title, grid_corners=4)
    other_grid = Grid(from_grid=scrip_file_2, title=bottom_grid_title, grid_corners=4) # TODO: corners should be stored in scrip file

    print('    contrstructing relevant grids from '+t_grid.title+' and '+other_grid.title+'...')

    grids = GridManager(t_grid, other_grid)
    print('    ...done.')
    ################################################
    # STEP 6: WRITE ORIGINAL-GRID REGRIDDING FILES #
    ################################################
    print('    writing original-grid regridding files...')

    print('        '+which_grid+' -> t_grid...')
    grids.write_remapping(u_to_t_file_orig, other_grid, t_grid)

    print('        t_grid -> '+which_grid+'...')
    grids.write_remapping(t_to_u_file_orig, t_grid, other_grid)

    ####################################################
    # STEP 7: READ IN REMAPPING AND REGRIDDING WEIGHTS #
    ####################################################
    print('    calculating exchange-grid regridding: t_grid -> '+which_grid+'...')
    # read in individual regridding steps
    nc = netCDF4.Dataset(exchange_to_t_file, 'r')
    src_address1   = nc.variables['src_address'][:]
    dst_address1   = nc.variables['dst_address'][:]
    remap_matrix1  = nc.variables['remap_matrix'][:,0]
    src_grid_dims1 = nc.variables['src_grid_dims'][:]
    dst_grid_dims1 = nc.variables['dst_grid_dims'][:]
    nc.close()
    nc = netCDF4.Dataset(t_to_u_file_orig, 'r')
    src_address2  = nc.variables['src_address'][:]
    dst_address2  = nc.variables['dst_address'][:]
    remap_matrix2 = nc.variables['remap_matrix'][:,0]
    src_grid_dims2 = nc.variables['src_grid_dims'][:]
    dst_grid_dims2 = nc.variables['dst_grid_dims'][:]
    nc.close()
    nc = netCDF4.Dataset(u_to_exchange_file, 'r')
    src_address3  = nc.variables['src_address'][:]
    dst_address3  = nc.variables['dst_address'][:]
    remap_matrix3 = nc.variables['remap_matrix'][:,0]
    src_grid_dims3 = nc.variables['src_grid_dims'][:]
    dst_grid_dims3 = nc.variables['dst_grid_dims'][:]
    nc.close()
    # format data as sparse matrix
    matrix1 = coo_matrix((remap_matrix1, (dst_address1-1, src_address1-1)), shape=(np.prod(dst_grid_dims1), np.prod(src_grid_dims1)))
    matrix2 = coo_matrix((remap_matrix2, (dst_address2-1, src_address2-1)), shape=(np.prod(dst_grid_dims2), np.prod(src_grid_dims2)))
    matrix3 = coo_matrix((remap_matrix3, (dst_address3-1, src_address3-1)), shape=(np.prod(dst_grid_dims3), np.prod(src_grid_dims3)))
    # multiply all three remapping steps
    mymatrix = matrix3 * matrix2 * matrix1
    mymatrix = mymatrix.tocoo()
    # write values to netcdf file
    nc = netCDF4.Dataset(t_to_u_file,'w')
    nc.createDimension("num_links"   ,len(mymatrix.row)   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = [n+1 for n in range(len(mymatrix.row))]
    nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = [1]
    src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   )); src_address_var[:]        =[n+1 for n in mymatrix.col]
    dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   )); dst_address_var[:]        =[n+1 for n in mymatrix.row]
    remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        )); remap_matrix_var[:,:]     =np.ma.asarray([[val] for val in mymatrix.data])
    nc.close()    

    print('    calculating exchange-grid regridding: '+which_grid+' -> t_grid...')
    # read in individual regridding steps
    nc = netCDF4.Dataset(exchange_to_u_file, 'r')
    src_address1   = nc.variables['src_address'][:]
    dst_address1   = nc.variables['dst_address'][:]
    remap_matrix1  = nc.variables['remap_matrix'][:,0]
    src_grid_dims1 = nc.variables['src_grid_dims'][:]
    dst_grid_dims1 = nc.variables['dst_grid_dims'][:]
    nc.close()
    nc = netCDF4.Dataset(u_to_t_file_orig, 'r')
    src_address2  = nc.variables['src_address'][:]
    dst_address2  = nc.variables['dst_address'][:]
    remap_matrix2 = nc.variables['remap_matrix'][:,0]
    src_grid_dims2 = nc.variables['src_grid_dims'][:]
    dst_grid_dims2 = nc.variables['dst_grid_dims'][:]
    nc.close()
    nc = netCDF4.Dataset(t_to_exchange_file, 'r')
    src_address3  = nc.variables['src_address'][:]
    dst_address3  = nc.variables['dst_address'][:]
    remap_matrix3 = nc.variables['remap_matrix'][:,0]
    src_grid_dims3 = nc.variables['src_grid_dims'][:]
    dst_grid_dims3 = nc.variables['dst_grid_dims'][:]
    nc.close()
    # format data as sparse matrix
    matrix1 = coo_matrix((remap_matrix1, (dst_address1-1, src_address1-1)), shape=(np.prod(dst_grid_dims1), np.prod(src_grid_dims1)))
    matrix2 = coo_matrix((remap_matrix2, (dst_address2-1, src_address2-1)), shape=(np.prod(dst_grid_dims2), np.prod(src_grid_dims2)))
    matrix3 = coo_matrix((remap_matrix3, (dst_address3-1, src_address3-1)), shape=(np.prod(dst_grid_dims3), np.prod(src_grid_dims3)))
    # multiply all three remapping steps
    mymatrix = matrix3 * matrix2 * matrix1
    mymatrix = mymatrix.tocoo()
    # write values to netcdf file
    nc = netCDF4.Dataset(u_to_t_file,'w')
    nc.createDimension("num_links"   ,len(mymatrix.row)   ); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = [n+1 for n in range(len(mymatrix.row))]
    nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = [1]
    src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   )); src_address_var[:]        =[n+1 for n in mymatrix.col]
    dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   )); dst_address_var[:]        =[n+1 for n in mymatrix.row]
    remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        )); remap_matrix_var[:,:]     =np.ma.asarray([[val] for val in mymatrix.data])
    nc.close()    

    return
