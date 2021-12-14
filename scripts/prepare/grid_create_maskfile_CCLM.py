# This script will create a file "mappings/maskfile.nc" inside a CCLM input folder, which states the fraction of each CCLM grid cell which has a bidirectional coupling.
# 1.0 = coupled, 0.0 = uncoupled
# The function is called from create_mappings.py 

import os
import netCDF4
import numpy as np

def grid_create_maskfile_CCLM(IOW_ESM_ROOT,        # root directory of IOW ESM
                              my_directory,        # name of this model instance
                              which_grid = "t_grid"): # mask file for which grid?      

    # STEP 1: CHECK IF MAPPING FILE (FROM EXCHANGEGRID TO CCLM) EXISTS
    inputfile  = IOW_ESM_ROOT+'/input/'+my_directory+'/mappings/remap_' + which_grid + '_exchangegrid_to_'+my_directory+'.nc'
    if which_grid == "t_grid":
        outputfile = IOW_ESM_ROOT+'/input/'+my_directory+'/mappings/maskfile.nc'
    else:
        outputfile = IOW_ESM_ROOT+'/input/'+my_directory+'/mappings/maskfile_' + which_grid + '.nc'
        
    if not (os.path.isfile(inputfile)):
        print('ERROR in grid_convert_CCLM_to_SCRIP: File '+inputfile+' not found.')
        return

    # STEP 2: READ DIMENSIONS AND DESTINATION GRID FRACTION FROM MAPPING FILE
    # open dataset
    nc = netCDF4.Dataset(inputfile,"r")

    # get dimensions of CCLM grid and fraction that is covered by the exchange grid
    dst_grid_dims = nc.variables['dst_grid_dims'][:]
    dst_grid_frac = nc.variables['dst_grid_frac'][:]
    nc.close()
    print(sum(dst_grid_frac))

    # STEP 3: CONVERT VECTOR TO MATRIX
    imax = dst_grid_dims[0]
    jmax = dst_grid_dims[1]
    mymatrix = np.ma.asarray([[0.0 for i in range(imax)] for j in range(jmax)])
    print(imax)
    print(jmax)
    for j in range(jmax):
        mymatrix[j,:] = dst_grid_frac[(j*imax):((j+1)*imax)]
    print(sum(mymatrix))

    # STEP 4: WRITE NETCDF FILE
    nc = netCDF4.Dataset(outputfile,'w')
    nc.createDimension("xaxis"   ,imax  ); xaxis_var    = nc.createVariable("xaxis"   ,"i4",("xaxis"   ,)); xaxis_var[:]    = [n+1 for n in range(imax)]
    nc.createDimension("yaxis"   ,jmax  ); yaxis_var    = nc.createVariable("yaxis"   ,"i4",("yaxis"   ,)); yaxis_var[:]    = [n+1 for n in range(jmax)]
    mask_var      = nc.createVariable("frac_coupled"       ,"f8",("yaxis","xaxis",        ))
    mask_var[:,:] = mymatrix 
    nc.close()

    return
