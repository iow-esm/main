# This script will fill the required files into the work directory for a MOM5 model.
# The function is called from create_work_directories.py 

from datetime import datetime
import os
import shutil

import change_in_namelist
import get_run_information

import glob

from netCDF4 import Dataset
import numpy as np

import re

import model_handling

class ModelHandler(model_handling.ModelHandlerBase):
    def __init__(self, global_settings, my_directory):
        # initialize base class 
        model_handling.ModelHandlerBase.__init__(self, 
                                                 model_handling.ModelTypes.bottom,  # specify this model as a bottom model
                                                 global_settings,                   # pass global settings 
                                                 my_directory,                      # memorize specific directory name = "model_domain"
                                                 grids = [model_handling.GridTypes.t_grid, model_handling.GridTypes.u_grid, model_handling.GridTypes.v_grid]) # model grids
        
    def create_work_directory(self, work_directory_root, start_date, end_date):
    
        # STEP 0: get local parameters from global settings
        IOW_ESM_ROOT        = self.global_settings.root_dir              # root directory of IOW ESM
        init_date           = self.global_settings.init_date             # 'YYYYMMDD'
        coupling_time_step  = self.global_settings.coupling_time_step    # in seconds
        run_name            = self.global_settings.run_name              # string
        debug_mode          = self.global_settings.debug_mode            # FALSE if executables compiled for production mode shall be used, 
                                                            # TRUE if executables compiled for debug mode shall be used
                                                            
        my_directory        = self.my_directory             # name of model's input folder
        
        # STEP 1: CHECK IF EXECUTABLE ALREADY EXISTS, IF NOT COPY IT
        full_directory = work_directory_root+'/'+my_directory
        destfile = full_directory+'/fms_MOM_SIS.x'
        if not os.path.isfile(destfile):
            # no executable, need to copy
            if debug_mode:
                sourcefile = IOW_ESM_ROOT+'/components/MOM5/exec/IOW_ESM_DEBUG/MOM_SIS/fms_MOM_SIS.x'
            else:
                sourcefile = IOW_ESM_ROOT+'/components/MOM5/exec/IOW_ESM_PRODUCTION/MOM_SIS/fms_MOM_SIS.x'
            # check if file exists
            if os.path.isfile(sourcefile):
                shutil.copyfile(sourcefile,destfile)   # copy the file
            else:
                print('ERROR creating work directory '+full_directory+': Wanted to copy the executable from '+sourcefile+
                      ' but that does not exist. You may have to build it.')
        st = os.stat(destfile)                 # get current permissions
        os.chmod(destfile, st.st_mode | 0o777) # add a+rwx permission

        # STEP 2: Adjust times in input.nml
        my_startdate = datetime.strptime(start_date,'%Y%m%d')
        my_enddate = datetime.strptime(end_date,'%Y%m%d')
        my_initdate = datetime.strptime(init_date,'%Y%m%d')

        rundays = (my_enddate - my_startdate).days

        change_in_namelist.change_in_namelist(filename=full_directory+'/input.nml',
                         after='&coupler_nml', before='/', start_of_line='days',
                         new_value = '='+str(rundays))
        change_in_namelist.change_in_namelist(filename=full_directory+'/input.nml',
                         after='&coupler_nml', before='/', start_of_line='current_date',
                         new_value = '='+datetime.strftime(my_initdate,'%Y,%m,%d,0,0,0'))
        change_in_namelist.change_in_namelist(filename=full_directory+'/input.nml',
                         after='&coupler_nml', before='/', start_of_line='dt_cpld',
                         new_value = '='+str(coupling_time_step))
        change_in_namelist.change_in_namelist(filename=full_directory+'/input.nml',
                         after='&coupler_nml', before='/', start_of_line='dt_atmos',
                         new_value = '='+str(coupling_time_step))
        change_in_namelist.change_in_namelist(filename=full_directory+'/diag_table',
                         after='', before='EOF', start_of_line='*AUTO*',
                         new_value = datetime.strftime(my_initdate,"%Y %m %d 0 0 0"), 
                         completely_replace_line=True)

        # STEP 3: Create an empty folder named "RESTART"
        os.makedirs(full_directory+'/RESTART') 

        # STEP 4: Copy hotstart files if a corresponding folder exists
        if (start_date != init_date):
            hotstart_folder = IOW_ESM_ROOT + '/hotstart/' + run_name + '/' + my_directory + '/' + start_date
            os.system('cp '+hotstart_folder+'/*.res.nc '+full_directory+'/INPUT/')    # copy MOM5 hotstart files
            os.system('cp '+hotstart_folder+'/coupler.res '+full_directory+'/INPUT/') # copy MOM5 file stating present date
            os.system('cp '+hotstart_folder+'/res*.nc '+full_directory+'/')           # copy OASIS3 hotstart files
        # otherwise use initial data in INIT folder for a cold start
        else:
            if not os.path.isdir(full_directory + '/INIT'):
                print("ERROR: For a cold start an INIT folder must be provided but could not be found. The model will probably crash.")
            else:
                os.system('cp '+full_directory+'/INIT/* '+full_directory+'/INPUT/')
         
        # STEP 5: generate run information
        info_file_name = full_directory + "/RUN_INFO"
        with open(info_file_name, 'w') as file:
            file.write(get_run_information.get_run_information(IOW_ESM_ROOT, debug_mode))
        file.close()

        return
        
    def check_for_success(self, work_directory_root, start_date, end_date):
        # if MOM5 has succeeded there is a RESTART folder
        hotstartfile = work_directory_root+'/'+self.my_directory+'/RESTART/*'
        
        # if restart folder is empty we failed
        if glob.glob(hotstartfile) == []:
            print('run failed because no file exists:'+hotstartfile)
            return False
        
        # we succeeded
        return True
    
    def move_results(self, work_directory_root, start_date, end_date):
    
        # work directory of this model instance
        workdir = work_directory_root + '/' + self.my_directory
        # directory for output        
        outputdir = self.global_settings.root_dir + '/output/' + self.global_settings.run_name+'/'+self.my_directory+'/'+str(start_date)
        # directory for hotstarts
        hotstartdir = self.global_settings.root_dir + '/hotstart/' + self.global_settings.run_name+'/'+self.my_directory+'/'+str(end_date)   

        # STEP 1: CREATE DIRECTORIES IF REQUIRED
        if (not os.path.isdir(outputdir)): 
            os.makedirs(outputdir)
        if (not os.path.isdir(outputdir+'/out_raw')):
            os.makedirs(outputdir+'/out_raw')
        if (not os.path.isdir(hotstartdir)):
            os.makedirs(hotstartdir)

        # STEP 2: MOVE OUTPUT
        os.system('mv '+workdir+'/*.nc.???? '+outputdir+'/out_raw/.')
        os.system('mv '+workdir+'/MS*.nc '+outputdir+'/.')
        os.system('mv '+workdir+'/MR*.nc '+outputdir+'/.')
        
        if os.path.isfile(workdir + '/RUN_INFO'):     
            files_to_keep = ["input.nml", "data_table", "diag_table", "field_table"]
            for file in files_to_keep:
                os.system('(echo \"*** ' + file + '\"; cat ' + workdir+'/'+file+'; echo) >> '+workdir+'/RUN_INFO')
            os.system('mv '+workdir+'/RUN_INFO '+outputdir+'/.')

        # STEP 3: MOVE HOTSTART
        os.system('mv '+workdir+'/RESTART/* '+hotstartdir+'/.')  # MOM hotstart files
        os.system('mv '+workdir+'/restart* '+hotstartdir+'/.')  # OASIS hotstart file
    
    def grid_convert_to_SCRIP(self):
        IOW_ESM_ROOT = self.global_settings.root_dir        # root directory of IOW ESM
        my_directory = self.my_directory       # name of this model instance
    
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
        
    def get_model_executable(self):
        return "fms_MOM_SIS.x"
        
    def get_num_threads(self):
        # MOM5 model - parallelization is given in input.nml in section &ocean_model_nml
        # "layout = 14,10"  e.g. means 14x10 rectangles exist, but a few of them may be masked out
        # "mask_table = 'INPUT/mask_table'" (optional) means we will find this file there
        # it contains the number of masked (=inactive) rectangles in the first line
        
        IOW_ESM_ROOT        = self.global_settings.root_dir              # root directory of IOW ESM
        model               = self.my_directory             # name of model's input folder
        
        inputfile = IOW_ESM_ROOT+'/input/'+model+'/input.nml'
        mythreads_x = 0
        mythreads_y = 0
        mythreads_masked = 0
        if not os.path.isfile(inputfile):
            print('Could not determine parallelization layout because the following file was missing: '+inputfile)
            return 0

        status = 'before' # make sure we seek in the correct area only
        f = open(inputfile)
        for line in f:
            if (line.strip()=='&ocean_model_nml') & (status == 'before'):
                status = 'active' # start searching
            if (line.strip()=='/') & (status == 'active'):
                status = 'after'  # stop searching
            if (status == 'active'):                        
                match = re.search("layout\s*=\s*(\d+)\s*,\s*(\d+)", line) # search for two comma-separated numbers after 'layout=', but allow spaces
                if match:
                    mythreads_x = int(match.group(1))
                    mythreads_y = int(match.group(2))
                    # memorize the layout for getting the domain decomposition
                    self.ndivx = mythreads_x
                    self.ndivy = mythreads_y
                match = re.search("mask_table\s*=\s*'([^']*)'", line) # search for anything between single quotes behind 'mask_table=', 
                                                                      # but allow spaces
                if match:
                    maskfile = IOW_ESM_ROOT+'/input/'+model+'/'+match.group(1)
                    # memorize the mask file for getting the domain decomposition
                    self.maskfile = maskfile
                    if not os.path.isfile(maskfile):
                        print('Could not determine parallelization layout because the following MOM5 mask file was missing: '+maskfile)
                        mythreads_masked = -1
                    else:
                        fm = open(maskfile)
                        mythreads_masked = int(fm.readline().strip())
                        fm.close()
        f.close()
        if mythreads_masked < 1: # did not find mask file
            mythreads = 0
        else:
            mythreads = mythreads_x * mythreads_y - mythreads_masked
            
        return mythreads

    def get_domain_decomposition(self):

        # get the correct paths
        IOW_ESM_ROOT = self.global_settings.root_dir              # root directory of IOW ESM
        full_directory = IOW_ESM_ROOT+'/input/' + self.my_directory

        # check if grid_spec.nc exists
        grid_spec_file = full_directory +'/INPUT/grid_spec.nc'
        if not (os.path.isfile(grid_spec_file)):
            print('ERROR in get_domain_decomposition: File '+full_directory+'/INPUT/grid_spec.nc not found.')
            return

        # open dataset
        nc = Dataset(grid_spec_file,"r")

        # get grid size as shape of the "Geographic longitude of T_cell centers"
        x_t = nc.variables['x_T'     ][:,:]
        grid_dims = x_t.shape
        nc.close()
        
        # get the mask file (use get_num_threads method that sets self.maskfile, self.ndivx, self.ndivy)
        if self.get_num_threads() <= 0:
            print("Gettin the number of threads failed. Abort.")
            return []

        # mimic domain decomposition from MOM5 code (mpp_domain.c)
        def mpp_compute_extent(npts, ndivs):

            #print(npts, ndivs)
            
            ibegin= [0]*ndivs
            iend = [0]*ndivs

            ndivs_is_odd = ndivs%2
            npts_is_odd = npts%2
            symmetrize = 0

            if( ndivs_is_odd and npts_is_odd ):
                symmetrize = 1
            if( ndivs_is_odd == 0 and npts_is_odd == 0 ):
                symmetrize = 1
            if( ndivs_is_odd and npts_is_odd == 0 and ndivs < npts/2 ):
                symmetrize = 1

            isg = 0
            ieg = npts-1
            ist = isg

            for ndiv in range(0,ndivs):

                #mirror domains are stored in the list and retrieved if required. 
                if( ndiv == 0 ): # initialize max points and max domains 
                    imax = ieg
                    ndmax = ndivs
                # do bottom half of decomposition, going over the midpoint for odd ndivs
                if( ndiv < (ndivs-1)/2+1 ):
                    # domain is sized by dividing remaining points by remaining domains
                    ie = ist + np.ceil((imax-ist+1.0)/(ndmax-ndiv) ) - 1
                    ndmirror = (ndivs-1) - ndiv # mirror domain

                    if( (ndmirror > ndiv) and symmetrize ): # only for domains over the midpoint
	                    # mirror extents, the max(,) is to eliminate overlaps
                        ibegin[ndmirror] = max(isg+ieg-ie, ie+1)
                        iend[ndmirror] = max(isg+ieg-ist, ie+1)
                        imax = ibegin[ndmirror] - 1
                        ndmax -= 1
                else:
                    if( symmetrize ):
	                    #do top half of decomposition by retrieving saved values */
                        ist = ibegin[ndiv]
                        ie = iend[ndiv]
    
                    else:
                        ie = ist + np.ceil((imax-ist+1.0)/(ndmax-ndiv)) - 1

                ibegin[ndiv] = ist
                iend[ndiv] = ie

                ist = ie + 1              

            return ibegin, iend                        

        # get the index limits for the domains 
        ibeginx, iendx = mpp_compute_extent(grid_dims[1], self.ndivx)   # x direction
        ibeginy, iendy = mpp_compute_extent(grid_dims[0], self.ndivy)   # y direction

        print("Use domain extents in x direction as: ", np.array(iendx, dtype=int) - np.array(ibeginx, dtype=int) + 1)
        print("Use domain extents in y direction as: ", np.array(iendy, dtype=int) - np.array(ibeginy, dtype=int) + 1)

        # get mask file content
        with open(self.maskfile) as mf:
            lines = mf.readlines()

        # throw away first two lines
        lines.pop(0)    # number of masked domains
        lines.pop(0)    # layout

        # matrix containing the process indeces
        processes = np.zeros(shape=(self.ndivx, self.ndivy), dtype=int)

        # go through the lines and mark masked unused domains with -1
        for line in lines:
            i,j = line.strip().split(",")
            i = int(i)
            j = int(j)
            processes[i-1][j-1] = -1

        # count remaining processes (that are not masked out)
        counter = 0

        for j in range(0, self.ndivy):
            for i in range(0, self.ndivx):

                if processes[i][j] == -1:
                    continue
                
                processes[i][j] = counter
                counter += 1

        #print(processes)

        # build array with task index for each grid point
        tasks = []
        for j in range(0, grid_dims[0]):
            # check in which domain this gridpoint is in y direction
            for k,endy in enumerate(iendy):
                if (j <= endy) and (j >= ibeginy[k]):
                    ky = k
                    break
            for i in range(0, grid_dims[1]):
                # check in which domain this gridpoint is in x direction
                for k,endx in enumerate(iendx):
                    if (i <= endx) and (i >= ibeginx[k]):
                        kx = k
                        break

                # store the task corresponding to this grid point           
                tasks.append(processes[kx][ky]) 

        return tasks


