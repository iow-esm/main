import netCDF4
import os

def modify_cclm_restart_file(  work_directory_root, # /path/to/work/directory for all models
                               my_directory,        # name of this model instance
                               start_date):

    
    nc_file = work_directory_root + "/" + my_directory + "/mappings/remap_t_grid_exchangegrid_to_" + my_directory + ".nc"

    print('reading in mapping from ' + nc_file)
    nc = netCDF4.Dataset(nc_file, 'r')
    # dst_address starts at 1, python use start with 0
    dst_address = nc.variables['dst_address'][:] - 1 
    src_grid_dims = nc.variables['src_grid_dims'][:]
    dst_grid_dims = nc.variables['dst_grid_dims'][:]
    nc.close()

    print('dst_address = ')
    print(dst_address)
    print("length = ", len(dst_address))
    print('src_grid_dims = ')
    print(src_grid_dims)
    print('dst_grid_dims = ')
    print(dst_grid_dims)

    # dst_adress = j * I_MAX + i
    I_MAX = dst_grid_dims[0]
    i = dst_address % I_MAX
    j = dst_address // I_MAX

    J_MAX = dst_grid_dims[1]
    #j = dst_address % J_MAX
    #i = dst_address // J_MAX

    print('i = ')
    print(i)
    print("length = ", len(i))
    print('j = ')
    print(j)
    print("length = ", len(j))
    
    nc_dir = work_directory_root + "/" + my_directory + "/OBC"
    nc_file = nc_dir + "/laf" + start_date + "00.nc"
    os.system("cp --remove-destination `readlink " + nc_file + "` " + nc_file)

    print('reading in restart file ' + nc_file)
    nc = netCDF4.Dataset(nc_file, 'r+')

    FR_LAND = nc.variables['FR_LAND'][:,:,:] 

    print('FR_LAND')
    print(FR_LAND)
    print('')
    print("length1 = ", len(FR_LAND))
    print("length2 = ", len(FR_LAND[0]))
    print("length3 = ", len(FR_LAND[0][0]))
    
    for idx,ii in enumerate(i):
        jj = j[idx]
        FR_LAND[:, jj, ii] = 0.0
    
    nc.variables['FR_LAND'][:,:,:] = FR_LAND
    nc.close()

    nc_file = nc_dir + "/laf_modified.nc"
    nc = netCDF4.Dataset(nc_file,'w')
    nc.createDimension("xaxis"   ,I_MAX  ); xaxis_var    = nc.createVariable("xaxis"   ,"i4",("xaxis"   ,)); xaxis_var[:]    = [n+1 for n in range(I_MAX)]
    nc.createDimension("yaxis"   ,J_MAX  ); yaxis_var    = nc.createVariable("yaxis"   ,"i4",("yaxis"   ,)); yaxis_var[:]    = [n+1 for n in range(J_MAX)]
    frland = nc.createVariable("FR_LAND"       ,"f8",("yaxis","xaxis",        ))
    frland[:,:] = FR_LAND[0, :, :]
    nc.close()

    #os.system("ln -s " + nc_file + " " + nc_dir + "/laf_modified.nc")




