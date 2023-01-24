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
        model_handling.ModelHandlerBase.__init__(self, model_handling.ModelTypes.atmosphere, global_settings, my_directory)
        
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
        destfile = full_directory+'/lmparbin'
        if not os.path.isfile(destfile):
            # no executable, need to copy
            if debug_mode:
                sourcefile = IOW_ESM_ROOT+'/components/CCLM/cclm/bin_DEBUG/lmparbin'
            else:
                sourcefile = IOW_ESM_ROOT+'/components/CCLM/cclm/bin_PRODUCTION/lmparbin'
            # check if file exists
            if os.path.isfile(sourcefile):
                shutil.copyfile(sourcefile,destfile)   # copy the file
            else:
                print('ERROR creating work directory '+full_directory+': Wanted to copy the executable from '+sourcefile+
                      ' but that does not exist. You may have to build it.')
        st = os.stat(destfile)                 # get current permissions
        os.chmod(destfile, st.st_mode | 0o777) # add a+rwx permission

        # STEP 2: Adjust times in INPUT_IO
        my_startdate = datetime.strptime(start_date,'%Y%m%d')
        my_enddate = datetime.strptime(end_date,'%Y%m%d')
        my_initdate = datetime.strptime(init_date,'%Y%m%d')
        starthours = (my_startdate - my_initdate).days*24
        finalhours = (my_enddate - my_initdate).days*24

        change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_IO',
                         after='&IOCTL', before='/END', start_of_line='nhour_restart',
                         new_value = '='+str(starthours)+','+str(finalhours)+','+str(finalhours-starthours)+',')
        change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_IO',
                         after='&GRIBOUT', before='/END', start_of_line='hcomb',
                         new_value = '='+str(starthours)+','+str(finalhours)+',_*_,', repeated=True) # mask out ('_*_') the print interval, should be used as is
        change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_ORG',
                         after='&RUNCTL', before='/END', start_of_line='ydate_ini',
                         new_value = '=\''+str(init_date)+'00\' ydate_end=\''+str(end_date)+'00\',')
        change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_ORG',
                         after='&RUNCTL', before='/END', start_of_line='hstart',
                         new_value = '='+str(starthours)+', hstop='+str(finalhours)+',')
        change_in_namelist.change_in_namelist(filename=full_directory+'/INPUT_OASIS',
                         after='&OASISCTL', before='/END', start_of_line='dt_cp',
                         new_value = ' = '+str(coupling_time_step))             

        # STEP 3: Copy hotstart files if a corresponding folder exists
        if (start_date != init_date):
            hotstart_folder = IOW_ESM_ROOT + '/hotstart/' + run_name + '/' + my_directory + '/' + start_date
            os.system('cp '+hotstart_folder+'/* '+full_directory+'/')        # copy all hotstart files 
        # otherwise use boundary data to perfrom a cold start
        else:
            if not os.path.isfile(full_directory + '/OBC/laf' + init_date + '00.nc'):
                print("ERROR: For a cold start a file laf<init_date>00.nc must be provided but could not be found. The model will probably crash.")
            else:
                os.system('ln -s ' + full_directory + '/OBC/laf' + init_date + '00.nc ' + full_directory + '/')
            
        # STEP 4: Store some information on the run
        info_file_name = full_directory + "/RUN_INFO"
        with open(info_file_name, 'w') as file:
            file.write(get_run_information.get_run_information(IOW_ESM_ROOT, debug_mode))
        file.close()
        return
        
    def check_for_success(self, work_directory_root, start_date, end_date):
        # if CCLM has succeeded there is a restart file
        hotstartfile = work_directory_root+'/'+self.my_directory+'/lrfd'+str(end_date)+'00o'
        
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
        if (not os.path.isdir(hotstartdir)):
            os.makedirs(hotstartdir)

        # STEP 2: MOVE OUTPUT
        os.system('mv '+workdir+'/out* '+outputdir+'/.')
        
        # if we run with verbos flux calculator the exchanged fields are stored in files AS*.nc and AR*.nc
        # if files are present we keep them        
        if glob.glob(workdir+'/AS*.nc') != []:
            os.system('mv '+workdir+'/AS*.nc '+outputdir+'/.')
        if glob.glob(workdir+'/AR*.nc') != []:
            os.system('mv '+workdir+'/AR*.nc '+outputdir+'/.')
        
        # store run information (commit ID's of built components, global_settings,...)
        if os.path.isfile(workdir + '/RUN_INFO'):
            os.system('mv '+workdir+'/RUN_INFO '+outputdir+'/.')

        # keep the important input files
        files_to_keep = ["INPUT_ASS", "INPUT_DIA", "INPUT_DYN", "INPUT_INI", "INPUT_IO", "INPUT_OASIS", "INPUT_ORG", "INPUT_PHY"]
        for file in files_to_keep:         
            os.system('mv '+workdir+'/'+file+' '+outputdir+'/.')   

        # STEP 3: MOVE HOTSTART
        hotstartfile = workdir+'/lrfd'+str(end_date)+'00o'           # CCLM hotstart file
        os.system('mv '+hotstartfile+' '+hotstartdir+'/.')
    
    def grid_convert_to_SCRIP(self):
    
        from numpy import sin, cos, arcsin, arctan2, pi, sqrt
        
        ########## auxiliary functions ########
        def get_float_after_key(key,line):
            match = re.search('.*'+key+'\s*=\s*((\+|-)?([0-9]+)(\.[0-9]+)?)|((\+|-)?\.?[0-9]+)', line) # search for real number after 'expression=' but allow spaces
            if match:
                if len(match.groups())>=2:
                    if match.group(1) is not None:
                        return(float(match.group(1)))
            return(-1000.0)

        def cross(a,b):
            return([a[1]*b[2]-a[2]*b[1],
                   a[2]*b[0]-a[0]*b[2],
                   a[0]*b[1]-a[1]*b[0]])

        def scalprod(a,b):
            return(a[0]*b[0]+a[1]*b[1]+a[2]*b[2])

        def rotate(vector,axis,angle):
            vec1 = [x*scalprod(axis,vector) for x in axis]
            vec2 = [cos(angle)*x for x in cross(cross(axis,vector),axis)]
            vec3 = [sin(angle)*x for x in cross(axis,vector)]
            return([sum(x) for x in zip(vec1, vec2, vec3)])

        def rotate_gridpoint(rlon, rlat, pollon, pollat):
            # get rotated cartesian coordinates
            rvec = [cos(rlon*pi/180)*cos(rlat*pi/180),
                    sin(rlon*pi/180)*cos(rlat*pi/180),
                    sin(rlat*pi/180)]

            # get north pole vector
            pole = [0,0,1]

            # rotate around north pole such that (0,0) is opposite of pollat
            vec1 = rotate(rvec,pole,(180+pollon)*pi/180)

            # get rotated north pole vector
            rpole = [cos(pollon*pi/180)*cos(pollat*pi/180),
                     sin(pollon*pi/180)*cos(pollat*pi/180),
                     sin(pollat*pi/180)]

            # get perpendicular axis around which to rotate
            rotaxis = cross(pole,rpole)
            rotaxis = [x / sqrt(scalprod(rotaxis,rotaxis)) for x in rotaxis]

            # perform rotation
            vec = rotate(vec1,rotaxis,(90-pollat)*pi/180)

            # back-convert
            lat = arcsin(vec[2])*180/pi
            lon = arctan2(vec[1],vec[0])*180/pi

            return([lon,lat])

        def rotate_grid(rlonvec,rlatvec,pollon,pollat):
            lon=[-1000.0]*len(rlonvec)
            lat=[-1000.0]*len(rlatvec)
            for i in range(len(rlonvec)):
                point = rotate_gridpoint(rlonvec[i],rlatvec[i],pollon,pollat)
                lon[i]=point[0]
                lat[i]=point[1]
            return(lon,lat)
            
            
        ################## main function #####################
        
        my_directory = self.my_directory       # name of this model instance
    
         # STEP 1: CREATE EMPTY "mappings" SUBDIRECTORY
        full_directory = self.global_settings.input_dir+'/'+my_directory
        if (os.path.isdir(full_directory+'/mappings')):
            os.system('rm -r '+full_directory+'/mappings')
        os.system('mkdir '+full_directory+'/mappings')

        # STEP 2: CHECK IF "INPUT_ORG" EXISTS
        if not (os.path.isfile(full_directory+'/INPUT_ORG')):
            print('ERROR in grid_convert_CCLM_to_SCRIP: File '+full_directory+'/INPUT_ORG not found.')
            return

        # STEP 3: READ IN VALUES FROM INPUT_ORG
        f = open(full_directory+'/INPUT_ORG')
        startlat_tot  = -1000.0
        startlon_tot  = -1000.0
        pollat        = -1000.0
        pollon        = -1000.0 
        polgam        =     0.0
        dlon          = -1000.0 
        dlat          = -1000.0
        ie_tot        = -1000.0 
        je_tot        = -1000.0
        for line in f:
            if get_float_after_key('startlat_tot',line) > -1000.0:
                startlat_tot = get_float_after_key('startlat_tot',line)
            if get_float_after_key('startlon_tot',line) > -1000.0:
                startlon_tot = get_float_after_key('startlon_tot',line)
            if get_float_after_key('pollat',line) > -1000.0:
                pollat = get_float_after_key('pollat',line)
            if get_float_after_key('pollon',line) > -1000.0:
                pollon = get_float_after_key('pollon',line)
            if get_float_after_key('polgam',line) > -1000.0:
                polgam = get_float_after_key('polgam',line)
            if get_float_after_key('dlon',line) > -1000.0:
                dlon = get_float_after_key('dlon',line)
            if get_float_after_key('dlat',line) > -1000.0:
                dlat = get_float_after_key('dlat',line)
            if get_float_after_key('ie_tot',line) > -1000.0:
                ie_tot = int(get_float_after_key('ie_tot',line))
            if get_float_after_key('je_tot',line) > -1000.0:
                je_tot = int(get_float_after_key('je_tot',line))
        f.close()
        if (polgam != 0.0):
            print('ERROR in grid_convert_CCLM_to_SCRIP: can only handle polgam=0.0 values, but value in file '+full_directory+'/INPUT_ORG differs.')
            return

        # define output files
        t_grid_file = full_directory+'/mappings/t_grid.nc'
    #    u_grid_file = full_directory+'/mappings/u_grid.nc'
    #    v_grid_file = full_directory+'/mappings/v_grid.nc'  
        t_grid_title = my_directory+'_t_grid'
    #    u_grid_title = my_directory+'_u_grid'
    #    v_grid_title = my_directory+'_v_grid'

        # define axis indexes
        grid_dims = [ie_tot, je_tot]
        n_grid_cells = ie_tot*je_tot
        n_grid_corners = 4
        n_grid_rank = 2
        grid_cell_index = np.arange(n_grid_cells)
        grid_corners = np.arange(n_grid_corners)
        grid_rank    = np.arange(n_grid_rank)

        # create rotated grids
        # create t grid
        rxt = list(np.linspace(start=startlon_tot, stop=startlon_tot+dlon*(ie_tot-1), num=ie_tot)) # x values on rotated grid
        ryt = list(np.linspace(start=startlat_tot, stop=startlat_tot+dlat*(je_tot-1), num=je_tot)) # y values on rotated grid
        # create t grid corners
        rxt_corners = list(np.linspace(start=startlon_tot-dlon/2, stop=startlon_tot+dlon*(ie_tot-1)+dlon/2, num=ie_tot+1)) # x values on rotated grid
        ryt_corners = list(np.linspace(start=startlat_tot-dlat/2, stop=startlat_tot+dlat*(je_tot-1)+dlat/2, num=je_tot+1)) # y values on rotated grid
    #    # create u grid
    #    rxu = list(np.linspace(start=startlon_tot+dlon/2, stop=startlon_tot+dlon*(ie_tot-1)+dlon/2, num=ie_tot)) # x values on rotated grid
    #    ryu = list(np.linspace(start=startlat_tot       , stop=startlat_tot+dlat*(je_tot-1)       , num=je_tot)) # y values on rotated grid
    #    # create u grid corners
    #    rxu_corners = list(np.linspace(start=startlon_tot       , stop=startlon_tot+dlon*ie_tot           , num=ie_tot+1)) # x values on rotated grid
    #    ryu_corners = list(np.linspace(start=startlat_tot-dlat/2, stop=startlat_tot+dlat*(je_tot-1)+dlat/2, num=je_tot+1)) # y values on rotated grid
    #    # create v grid
    #    rxv = list(np.linspace(start=startlon_tot       , stop=startlon_tot+dlon*(ie_tot-1)       , num=ie_tot)) # x values on rotated grid
    #    ryv = list(np.linspace(start=startlat_tot+dlat/2, stop=startlat_tot+dlat*(je_tot-1)+dlat/2, num=je_tot)) # y values on rotated grid
    #    # create v grid corners
    #    rxv_corners = list(np.linspace(start=startlon_tot-dlon/2, stop=startlon_tot+dlon*(ie_tot-1)+dlon/2, num=ie_tot+1)) # x values on rotated grid
    #    ryv_corners = list(np.linspace(start=startlat_tot       , stop=startlat_tot+dlat*je_tot           , num=je_tot+1)) # y values on rotated grid

        # write these data (midpoints and corners) to long lists with one entry for each gridpoint
        # i index changes fastest, then j, then corner
        rx_t      = rxt*je_tot
        rx_vert_t = rxt_corners[0:ie_tot]*je_tot + rxt_corners[1:(ie_tot+1)]*je_tot + rxt_corners[1:(ie_tot+1)]*je_tot + rxt_corners[0:ie_tot]*je_tot
        ry_t      = list(np.repeat(ryt,ie_tot))
        ry_vert_t = list(np.repeat(ryt_corners[0:je_tot],ie_tot))*2 + list(np.repeat(ryt_corners[1:(je_tot+1)],ie_tot))*2

    #    rx_u      = rxu*je_tot
    #    rx_vert_u = rxu_corners[0:ie_tot]*je_tot + rxu_corners[1:(ie_tot+1)]*je_tot + rxu_corners[1:(ie_tot+1)]*je_tot + rxu_corners[0:ie_tot]*je_tot
    #    ry_u      = list(np.repeat(ryu,ie_tot))
    #    ry_vert_u = list(np.repeat(ryu_corners[0:je_tot],ie_tot))*2 + list(np.repeat(ryu_corners[1:(je_tot+1)],ie_tot))*2
    #
    #    rx_v      = rxv*je_tot
    #    rx_vert_v = rxv_corners[0:ie_tot]*je_tot + rxv_corners[1:(ie_tot+1)]*je_tot + rxv_corners[1:(ie_tot+1)]*je_tot + rxv_corners[0:ie_tot]*je_tot
    #    ry_v      = list(np.repeat(ryv,ie_tot))
    #    ry_vert_v = list(np.repeat(ryv_corners[0:je_tot],ie_tot))*2 + list(np.repeat(ryv_corners[1:(je_tot+1)],ie_tot))*2

        print('    rotating t grid...')
        x_t, y_t = rotate_grid(rx_t,ry_t,pollon,pollat)
        print('    rotating t grid corners...')
        x_vert_t, y_vert_t = rotate_grid(rx_vert_t,ry_vert_t,pollon,pollat)

        print('    writing t_grid.nc...')
        # get values for t grid
        grid_center_lon = x_t
        grid_center_lat = y_t
        grid_imask      = [1]*n_grid_cells
        grid_corner_lon = np.ma.asarray([[np.nan for col in grid_corners] for row in grid_cell_index])
        grid_corner_lat = np.ma.asarray([[np.nan for col in grid_corners] for row in grid_cell_index])
        for i in range(grid_dims[0]):
            for j in range (grid_dims[1]):
                for k in grid_corners:
                    grid_corner_lon[j*grid_dims[0]+i,k] = x_vert_t[k*ie_tot*je_tot+j*ie_tot+i]
                    grid_corner_lat[j*grid_dims[0]+i,k] = y_vert_t[k*ie_tot*je_tot+j*ie_tot+i]

        # delete t-grid file if it exists
        if os.path.isfile(t_grid_file):
            os.remove(t_grid_file)
        # write t grid file
        nc = Dataset(t_grid_file,"w")
        nc.title = t_grid_title
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
        print('    done.')
        
    def get_model_executable(self):
        return "lmparbin"
        
    def get_num_threads(self):
        # CCLM model - parallelization is described in INPUT_ORG, e.g. nprocx= 8, nprocy= 24
        model               = self.my_directory             # name of model's input folder
        
        inputfile = self.global_settings.input_dir+'/'+model+'/INPUT_ORG'
        mythreads_x = 0
        mythreads_y = 0
        mythreads = 0
        if not os.path.isfile(inputfile):
            print('Could not determine parallelization layout because the following file was missing: '+inputfile)
        else :
            f = open(inputfile)
            for line in f:
                match = re.search('nprocx\s*=\s*(\d+)', line) # search for number after 'nprocx=', but allow spaces
                if match:
                    mythreads_x = int(match.group(1))
                match = re.search('nprocy\s*=\s*(\d+)', line) # search for number after 'nprocy=', but allow spaces
                if match:
                    mythreads_y = int(match.group(1))
            f.close()
            mythreads = mythreads_x * mythreads_y
        if mythreads==0:
            print('Could not determine number of threads for model ',model)
            
        return mythreads