import numpy as np
import netCDF4

from mapping_helper_functions import get_polys_and_boxes, sub_polybox, get_intersections, polygon_area

class Grid:
    
    def __init__(self, title = None, from_grid = None, **kwargs):

        if title is not None:
            self.title = title
        else:
            self.title = ""

        if type(from_grid) is str and from_grid.split(".")[-1] == "nc":
            self.read(from_grid) 
            
        elif type(from_grid) is Grid:
            import copy
            self = copy.deep_copy(from_grid)

        valid_kwargs = ['grid_dims', 'grid_imask', 'grid_corners', 'grid_corner_lon', 'grid_corner_lat', 'grid_center_lon', \
                        'grid_center_lat', 'grid_area', 'grid_area_fraction', 'grid_area_fraction_normalized', 'grid_index']
        

        for arg in kwargs.keys():
            if arg not in valid_kwargs:
                print("Keyword argument \""+arg+"\" is not valid.")
                continue

            setattr(self, arg, kwargs[arg])
        
        for valid_arg in valid_kwargs:
            try: 
                getattr(self, valid_arg)
            except:
                setattr(self, valid_arg, None) 

        self.grid_size = int(np.prod(self.grid_dims))
        self.grid_rank = len(self.grid_dims)

    def reconfigure(self, **kwargs):
        for arg in kwargs.keys():
            try:
                setattr(self, arg, kwargs[arg])
            except:
                pass

    def read(self, file_name):
        nc = netCDF4.Dataset(file_name, 'r')
        self.grid_corner_lon = nc.variables['grid_corner_lon'][:,:]
        self.grid_corner_lat = nc.variables['grid_corner_lat'][:,:]
        self.grid_center_lon = nc.variables['grid_center_lon'][:]
        self.grid_center_lat = nc.variables['grid_center_lat'][:]
        self.grid_imask     = nc.variables['grid_imask'][:]
        self.grid_dims      = nc.variables['grid_dims'][:]
        nc.close()


    def write(self, file_name):
        nc = netCDF4.Dataset(file_name,"w")
        nc.title = self.title
        nc.createDimension("grid_size"   ,self.grid_size  ); grid_size_var    = nc.createVariable("grid_size"   ,"i4",("grid_size"   ,)); grid_size_var[:]    = [n+1 for n in range(self.grid_size)]
        nc.createDimension("grid_corners",self.grid_corners); grid_corners_var = nc.createVariable("grid_corners","i4",("grid_corners",)); grid_corners_var[:] = [n+1 for n in range(self.grid_corners)]
        nc.createDimension("grid_rank"   ,self.grid_rank   ); grid_rank_var    = nc.createVariable("grid_rank"   ,"i4",("grid_rank"   ,)); grid_rank_var[:]    = [self.grid_rank]
        grid_dims_var       = nc.createVariable("grid_dims"      ,"i4",("grid_rank",               )); grid_dims_var.missval=np.int32(-1) ; grid_dims_var[:]      =self.grid_dims
        grid_center_lat_var = nc.createVariable("grid_center_lat","f8",("grid_size",               )); grid_center_lat_var.units="degrees"; grid_center_lat_var[:]=self.grid_center_lat
        grid_center_lon_var = nc.createVariable("grid_center_lon","f8",("grid_size",               )); grid_center_lon_var.units="degrees"; grid_center_lon_var[:] = self.grid_center_lon
        grid_imask_var      = nc.createVariable("grid_imask"     ,"i4",("grid_size",               )); grid_imask_var.missval=np.int32(-1); grid_imask_var[:]     =self.grid_imask 
        grid_corner_lat_var = nc.createVariable("grid_corner_lat","f8",("grid_size","grid_corners",)); grid_corner_lat_var.units="degrees"; grid_corner_lat_var[:]=self.grid_corner_lat
        grid_corner_lon_var = nc.createVariable("grid_corner_lon","f8",("grid_size","grid_corners",)); grid_corner_lon_var.units="degrees"; grid_corner_lon_var[:]=self.grid_corner_lon
        try:
            grid_area_var       = nc.createVariable("grid_area"      ,"f8",("grid_size",               )); grid_area_var.units      ="square radians"; grid_area_var[:]=self.grid_area
        except:
            pass
        nc.sync()
        nc.close()     

class IntersectionGrid(Grid):
    def __init__(self, grid1, grid2, **kwargs):

        self.grid1 = grid1
        self.grid2 = grid2

        grid_corner_lon1 = grid1.grid_corner_lon
        grid_corner_lat1 = grid1.grid_corner_lat
        grid_imask_1     = grid1.grid_imask

        grid_corner_lon2 = grid2.grid_corner_lon
        grid_corner_lat2 = grid2.grid_corner_lat
        grid_imask_2     = grid2.grid_imask

        #######################################################
        # STEP 3: CALCULATE POLYGONS AND THEIR BOUNDING BOXES #
        #######################################################

        print('    calculating bounding boxes for '+self.grid1.title+' cells...')
        polybox1 = get_polys_and_boxes(grid_corner_lon1[:,:], grid_corner_lat1[:,:], grid_imask_1[:])
        print('    calculating bounding boxes for '+self.grid1.title+' cells...')
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
        print('        ', end="")
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
                if (((i*gridsize+j)*100)//(gridsize*gridsize)) % 5 == 0:
                    print('.', end="", flush=True)
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
        print('done.')

        ####################################################
        # STEP 5: CALCULATE AREA OF POLYGONS ON THE SPHERE #
        ####################################################
        print('    calculating '+self.grid1.title+' areas...')
        area1_at_activepoints = [polygon_area(polybox1[4][i].exterior.coords.xy[0],polybox1[4][i].exterior.coords.xy[1],1.0) 
                                for i in range(len(polybox1[0]))]
        area1 = [0.0 for i in range(len(grid_imask_1))]
        for i in range(len(polybox1[0])):
            area1[polybox1[5][i]] = area1_at_activepoints[i] # column 5 of polybox1 contains cell index

        print('    calculating '+self.grid2.title+' areas...')
        area2_at_activepoints = [polygon_area(polybox2[4][i].exterior.coords.xy[0],polybox2[4][i].exterior.coords.xy[1],1.0) 
                                for i in range(len(polybox2[0]))]
        area2 = [0.0 for i in range(len(grid_imask_2))]
        for i in range(len(polybox2[0])):
            area2[polybox2[5][i]] = area2_at_activepoints[i] # column 5 of polybox2 contains cell index

        print('    calculating intersection grid areas...')
        area3 = [polygon_area(poly_x[i][0:corners[i]],poly_y[i][0:corners[i]],1.0) for i in range(global_k)]

        print('    calculating intersection area fractions of '+self.grid1.title+' ...')
        fraction_of_atmos = [area3[i]/area1[atmos_index[i]] for i in range(global_k)] # exchange grid cell area fraction of atmos cell
        area1_fraction = [0.0 for i in range(len(grid_imask_1))]
        for i in range(global_k):  # calculate total fraction of atmos cell covered by all exchange grid cells
            area1_fraction[atmos_index[i]] = area1_fraction[atmos_index[i]] + fraction_of_atmos[i]
        fraction_of_atmos_normalized = fraction_of_atmos[:] # normalize this fraction with the total fraction of the atmospheric cell which is covered
        for i in range(global_k):
            fraction_of_atmos_normalized[i] = fraction_of_atmos_normalized[i] / area1_fraction[atmos_index[i]]

        print('    calculating intersection area fractions of '+self.grid2.title+' ...')
        fraction_of_bottom = [area3[i]/area2[bottom_index[i]] for i in range(global_k)] # exchange grid cell area fraction of bottom cell
        area2_fraction = [0.0 for i in range(len(grid_imask_2))]
        for i in range(global_k):  # calculate total fraction of bottom cell covered by all exchange grid cells
            area2_fraction[bottom_index[i]] = area2_fraction[bottom_index[i]] + fraction_of_bottom[i]
        fraction_of_bottom_normalized = fraction_of_bottom # normalize this fraction with the total fraction of the bottom cell which is covered
        for i in range(global_k):
            fraction_of_bottom_normalized[i] = fraction_of_bottom_normalized[i] / area2_fraction[bottom_index[i]]        

        print('    create intersection grid object...')
        super().__init__(   grid_dims=np.array([global_k]),
                            grid_imask=np.array([1]*global_k), 
                            grid_corners=max(corners[0:global_k]),
                            grid_corner_lon =  np.ma.asarray([[poly_x[k][0:max(corners[0:global_k])]] for k in range(global_k)]),
                            grid_corner_lat = np.ma.asarray([[poly_y[k][0:max(corners[0:global_k])]] for k in range(global_k)]),
                            grid_center_lon = np.array([np.mean([poly_x[k][0:(corners[k]-1)]]) for k in range(global_k)]),
                            grid_center_lat = np.array([np.mean([poly_y[k][0:(corners[k]-1)]]) for k in range(global_k)]),
                            **kwargs)            

        print('    add intersection specific information to involved grids...')

        self.grid1.grid_area = np.array(area1)
        self.grid1.grid_area_fraction = np.array(area1_fraction)
        self.grid1.grid_index = np.array(atmos_index[0:global_k], dtype=int)
        self.grid1.grid_area_fraction_normalized = fraction_of_atmos_normalized

        self.grid2.grid_area = np.array(area2)
        self.grid2.grid_area_fraction = np.array(area2_fraction)
        self.grid2.grid_index = np.array(bottom_index[0:global_k], dtype=int)
        self.grid2.grid_area_fraction_normalized = fraction_of_bottom_normalized        

        self.grid_area = np.array(area3)
        self.grid_index = np.array(list(range(global_k)), dtype=int)
        self.grid_area_fraction = np.array([1.0]*global_k)
        self.grid_area_fraction_nomralized = np.array([1]*global_k)

class GridManager:
    def __init__(self, grid1, grid2, exchange_grid = None):

        print("    initialize GridManager for "+grid1.title+" and "+grid2.title+"...")

        self.grid1 = grid1
        self.grid2 = grid2

        if exchange_grid is None:
            exchange_grid = IntersectionGrid(self.grid1, self.grid2, title='intersection_grid')
            
        if (type(exchange_grid) is IntersectionGrid) and (exchange_grid.grid1 is self.grid1) and (exchange_grid.grid2 is self.grid2) :
            self.intersection_grid = exchange_grid 
            src_for_exchange_grid = self.intersection_grid
        elif (exchange_grid is self.grid1):
            self.intersection_grid = IntersectionGrid(self.grid1, self.grid2, title='intersection_grid')
            src_for_exchange_grid  = self.grid1
        elif (exchange_grid is self.grid2):
            self.intersection_grid = IntersectionGrid(self.grid1, self.grid2, title='intersection_grid')
            src_for_exchange_grid  = self.grid2
        else:
            print("Exchange grid must be one of the follwoing: None, grid1 or grid2")
            raise

        self.prepare_exchange_grid(src_for_exchange_grid)


    def prepare_exchange_grid(self, src_for_exchange_grid):

        print("    prepare exchange grid from "+src_for_exchange_grid.title+"...")

        num_links = self.intersection_grid.grid_size

        exchange_mask = [0]*len(src_for_exchange_grid.grid_imask)
        for i in range(self.intersection_grid.grid_size):
            if src_for_exchange_grid.grid_imask[src_for_exchange_grid.grid_index[i]] == 1:
                exchange_mask[src_for_exchange_grid.grid_index[i]] = 1

        exchange_mask = np.array(exchange_mask, dtype=int)

        exchange_grid_src_index = []
        for i, mask in enumerate(exchange_mask):
            if mask:
                exchange_grid_src_index.append(i)

        # find index of link that belongs to this exchange grid cell
        exchange_grid_src_index_inv = {}
        for i, src in enumerate(exchange_grid_src_index):
            exchange_grid_src_index_inv[src] = i

        exchange_index = [exchange_grid_src_index_inv[src_for_exchange_grid.grid_index[i]] for i in range(num_links)]
        exchange_index = np.array(exchange_index, dtype=int)

        exchange_grid_size = int(np.sum(exchange_mask))
        self.exchange_grid = Grid(title = "exchange_grid", 
                                  grid_dims = np.array([exchange_grid_size]),
                                  grid_imask = np.array([1]*exchange_grid_size),
                                  grid_corners = src_for_exchange_grid.grid_corners,
                                  grid_corner_lon = src_for_exchange_grid.grid_corner_lon[exchange_mask == 1][:],
                                  grid_corner_lat = src_for_exchange_grid.grid_corner_lat[exchange_mask == 1][:],
                                  grid_center_lon = src_for_exchange_grid.grid_center_lon[exchange_mask == 1],
                                  grid_center_lat = src_for_exchange_grid.grid_center_lat[exchange_mask == 1],
                                  grid_area = src_for_exchange_grid.grid_area[exchange_mask == 1]                 
                                  )

        print('    calculating intersection fractions of exchange grid...')
        self.exchange_grid.grid_index = exchange_index
        fraction_of_exchange = [self.intersection_grid.grid_area[i]/self.exchange_grid.grid_area[exchange_index[i]] for i in range(num_links)] # exchange grid cell area fraction of bottom cell
        self.exchange_grid.grid_area_fraction = [0.0 for i in range(self.exchange_grid.grid_size)]
        for i in range(num_links):  # calculate total fraction of exchange cell covered by all exchange grid cells
            self.exchange_grid.grid_area_fraction[exchange_index[i]] = self.exchange_grid.grid_area_fraction[exchange_index[i]] + fraction_of_exchange[i]
        self.exchange_grid.grid_area_fraction_normalized = fraction_of_exchange # normalize this fraction with the total fraction of the bottom cell which is covered
        for i in range(num_links):
            self.exchange_grid.grid_area_fraction_normalized[i] = self.exchange_grid.grid_area_fraction_normalized[i] / self.exchange_grid.grid_area_fraction[exchange_index[i]]   

    def write_remapping(self, file_name, src, dst):

        num_links = self.intersection_grid.grid_size

        nc = netCDF4.Dataset(file_name,'w')
        nc.title = file_name
        nc.normalization = 'no norm' 
        nc.map_method = 'Conservative remapping'
        nc.conventions = "SCRIP" 
        nc.source_grid = src.title
        nc.dest_grid = dst.title
        nc.createDimension("src_grid_size"   ,len(src.grid_imask)  ); src_grid_size_var    = nc.createVariable("src_grid_size"   ,"i4",("src_grid_size"   ,)); src_grid_size_var[:]    = [n+1 for n in range(len(src.grid_imask))]
        nc.createDimension("dst_grid_size"   ,len(dst.grid_imask)  ); dst_grid_size_var    = nc.createVariable("dst_grid_size"   ,"i4",("dst_grid_size"   ,)); dst_grid_size_var[:]    = [n+1 for n in range(len(dst.grid_imask))]
        nc.createDimension("src_grid_corners"   , src.grid_corners  ); src_grid_corners_var    = nc.createVariable("src_grid_corners"   ,"i4",("src_grid_corners"   ,)); src_grid_corners_var[:]    = [n+1 for n in range(src.grid_corners)]
        nc.createDimension("dst_grid_corners"   , dst.grid_corners  ); dst_grid_corners_var    = nc.createVariable("dst_grid_corners"   ,"i4",("dst_grid_corners"   ,)); dst_grid_corners_var[:]    = [n+1 for n in range(dst.grid_corners)]
        nc.createDimension("src_grid_rank"   ,len(src.grid_dims)   ); src_grid_rank_var    = nc.createVariable("src_grid_rank"   ,"i4",("src_grid_rank"   ,)); src_grid_rank_var[:]    = [n+1 for n in range(len(src.grid_dims))]
        nc.createDimension("dst_grid_rank"   ,len(dst.grid_dims)   ); dst_grid_rank_var    = nc.createVariable("dst_grid_rank"   ,"i4",("dst_grid_rank"   ,)); dst_grid_rank_var[:]    = [n+1 for n in range(len(dst.grid_dims))]
        nc.createDimension("num_links"   ,  num_links); num_links_var    = nc.createVariable("num_links"   ,"i4",("num_links"   ,)); num_links_var[:]    = [n+1 for n in range(num_links)]
        nc.createDimension("num_wgts"   ,1   ); num_wgts_var    = nc.createVariable("num_wgts"   ,"i4",("num_wgts"   ,)); num_wgts_var[:]    = [1]
        src_grid_dims_var       = nc.createVariable("src_grid_dims"      ,"i4",("src_grid_rank",               )); src_grid_dims_var.missval=np.int32(-1)  ; src_grid_dims_var[:]      =src.grid_dims
        dst_grid_dims_var       = nc.createVariable("dst_grid_dims"      ,"i4",("dst_grid_rank",               )); dst_grid_dims_var.missval=np.int32(-1)  ; dst_grid_dims_var[:]      =dst.grid_dims
        src_grid_center_lat_var = nc.createVariable("src_grid_center_lat","f8",("src_grid_size",               )); src_grid_center_lat_var.units='radians' ; src_grid_center_lat_var[:]=np.deg2rad(src.grid_center_lat)
        dst_grid_center_lat_var = nc.createVariable("dst_grid_center_lat","f8",("dst_grid_size",               )); dst_grid_center_lat_var.units='radians' ; dst_grid_center_lat_var[:]=np.deg2rad(dst.grid_center_lat)
        src_grid_center_lon_var = nc.createVariable("src_grid_center_lon","f8",("src_grid_size",               )); src_grid_center_lon_var.units='radians' ; src_grid_center_lon_var[:]=np.deg2rad(src.grid_center_lon)
        dst_grid_center_lon_var = nc.createVariable("dst_grid_center_lon","f8",("dst_grid_size",               )); dst_grid_center_lon_var.units='radians' ; dst_grid_center_lon_var[:]=np.deg2rad(dst.grid_center_lon) 
        src_grid_corner_lat_var = nc.createVariable("src_grid_corner_lat","f8",("src_grid_size", "src_grid_corners")); src_grid_corner_lat_var.units='radians' ; src_grid_corner_lat_var[:]=np.deg2rad(src.grid_corner_lat)
        dst_grid_corner_lat_var = nc.createVariable("dst_grid_corner_lat","f8",("dst_grid_size", "dst_grid_corners")); dst_grid_corner_lat_var.units='radians' ; dst_grid_corner_lat_var[:]=np.deg2rad(dst.grid_corner_lat)       
        src_grid_corner_lon_var = nc.createVariable("src_grid_corner_lon","f8",("src_grid_size", "src_grid_corners")); src_grid_corner_lon_var.units='radians' ; src_grid_corner_lon_var[:]=np.deg2rad(src.grid_corner_lon)
        dst_grid_corner_lon_var = nc.createVariable("dst_grid_corner_lon","f8",("dst_grid_size", "dst_grid_corners")); dst_grid_corner_lon_var.units='radians' ; dst_grid_corner_lon_var[:]=np.deg2rad(dst.grid_corner_lon)
        src_grid_imask_var      = nc.createVariable("src_grid_imask"     ,"i4",("src_grid_size",               )); src_grid_imask_var.units='unitless'     ; src_grid_imask_var[:]     = src.grid_imask
        dst_grid_imask_var      = nc.createVariable("dst_grid_imask"     ,"i4",("dst_grid_size",               )); dst_grid_imask_var.units='unitless'     ; dst_grid_imask_var[:]     = dst.grid_imask
        src_grid_area_var       = nc.createVariable("src_grid_area"      ,"f8",("src_grid_size",               )); src_grid_area_var.units='square radians'; src_grid_area_var[:]      = src.grid_area
        dst_grid_area_var       = nc.createVariable("dst_grid_area"      ,"f8",("dst_grid_size",               )); dst_grid_area_var.units='square radians'; dst_grid_area_var[:]      = dst.grid_area
        src_grid_frac_var       = nc.createVariable("src_grid_frac"      ,"f8",("src_grid_size",               )); src_grid_frac_var.units='unitless'      ; src_grid_frac_var[:]      = src.grid_area_fraction
        dst_grid_frac_var       = nc.createVariable("dst_grid_frac"      ,"f8",("dst_grid_size",               )); dst_grid_frac_var.units='unitless'      ; dst_grid_frac_var[:]      = dst.grid_area_fraction
        src_address_var         = nc.createVariable("src_address"        ,"i4",("num_links",                   ));                                           src_address_var[:]        = [n+1 for n in src.grid_index]
        dst_address_var         = nc.createVariable("dst_address"        ,"i4",("num_links",                   ));                                           dst_address_var[:]        = [n+1 for n in dst.grid_index]
        remap_matrix_var        = nc.createVariable("remap_matrix"       ,"f8",("num_links","num_wgts",        ));                                           remap_matrix_var[:,:]     = np.ma.asarray([[val] for val in dst.grid_area_fraction_normalized])
        nc.close()

