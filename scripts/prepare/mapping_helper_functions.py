# This script contains helper functions used to create any kind of mappings and exchange grids between models.

import netCDF4
from shapely.geometry import Polygon
from numpy import sqrt
import numpy as np

def get_polys_and_boxes(gc_lon1, gc_lat1, imask):
    # This function converts the longitudes and latitudes given to polygons and lat-lon bounding boxes.
    # Only cells with imask==1 will be converted and cells with imask==0 will be ignored.
    polynum = range(gc_lon1.shape[0])
    poly1 = [0.0 for i in polynum]
    bounds1 = [[-1000.0,-1000.0,-1000.0,-1000.0] for row in range(gc_lon1.shape[0])]
    for i in range(gc_lon1.shape[0]):
        if imask[i]==1:
            poly1[i] = Polygon(zip(gc_lon1[i,:],gc_lat1[i,:]))
            bounds1[i] = poly1[i].bounds
    minlon = [bounds1[i][0] for i in range(gc_lon1.shape[0])]
    minlat = [bounds1[i][1] for i in range(gc_lon1.shape[0])]
    maxlon = [bounds1[i][2] for i in range(gc_lon1.shape[0])]
    maxlat = [bounds1[i][3] for i in range(gc_lon1.shape[0])]
    return([minlon, minlat, maxlon, maxlat, poly1, polynum])

def sub_polybox(polybox, condition):
    # This function will select those polygons and their bounding boxes from a polygon list where condition==True.
    # The polygon list should be created by calling get_polys_and_boxes()
    return([[i for (i, v) in zip(column, condition) if v] for column in polybox])

def get_intersections(polybox1, polybox2, kmax, cornermax):
    # This function will check if any polygons between the lists polybox1 and polybox2 intersect.
    atmos_index = [-1 for k in range(kmax)]
    bottom_index = [-1 for k in range(kmax)]
    corners = [-1 for k in range(kmax)]
    poly_x = [[-1000.0 for col in range(cornermax)] for row in range(kmax)]
    poly_y = [[-1000.0 for col in range(cornermax)] for row in range(kmax)]
    poly1 = polybox1[4]
    poly2 = polybox2[4]
    k=0
    for i in range(len(polybox1[0])):
        minlon1 = polybox1[0][i]
        minlat1 = polybox1[1][i]
        maxlon1 = polybox1[2][i]
        maxlat1 = polybox1[3][i]
        for j in range(len(polybox2[0])):
            minlon2 = polybox2[0][j]
            minlat2 = polybox2[1][j]
            maxlon2 = polybox2[2][j]
            maxlat2 = polybox2[3][j]
            if (minlon1 < maxlon2) & (maxlon1 > minlon2):
                if (minlat1 < maxlat2) & (maxlat1 > minlat2):
                    poly3 = poly1[i].intersection(poly2[j])
                    if not poly3.is_empty:
                        atmos_index[k]=polybox1[5][i]
                        bottom_index[k]=polybox2[5][j]
                        x, y = poly3.exterior.coords.xy
                        corners[k] = len(y)
                        poly_x[k][0:corners[k]] = x
                        poly_y[k][0:corners[k]] = y
                        k=k+1
            if k>=kmax:
                print('Error in get_intersections: kmax exceeded')
    return([k, atmos_index, bottom_index, corners, poly_x, poly_y])

def polygon_area(lats, lons, radius = 6378137):
    """
    Computes area of spherical polygon, assuming spherical Earth.
    Returns result in ratio of the sphere's area if the radius is specified.
    Otherwise, in the units of provided radius.
    Set radius to 1.0 to get square radians.
    lats and lons are in degrees.
    """
    from numpy import arctan2, cos, sin, sqrt, pi, power, append, diff, deg2rad
    lats = np.deg2rad(lats)
    lons = np.deg2rad(lons)

    # Line integral based on Green's Theorem, assumes spherical Earth

    #close polygon
    if (lats[0]!=lats[-1]) | (lons[0]!=lons[-1]):
        lats = append(lats, lats[0])
        lons = append(lons, lons[0])

    #colatitudes relative to (0,0)
    a = sin(lats/2)**2 + cos(lats)* sin(lons/2)**2
    colat = 2*arctan2( sqrt(a), sqrt(1-a) )

    #azimuths relative to (0,0)
    az = arctan2(cos(lats) * sin(lons), sin(lats)) % (2*pi)

    # Calculate diffs
    # daz = diff(az) % (2*pi)
    daz = diff(az)
    daz = (daz + pi) % (2 * pi) - pi

    deltas=diff(colat)/2
    colat=colat[0:-1]+deltas

    # Perform integral
    integrands = (1-cos(colat)) * daz

    # Integrate
    area = abs(sum(integrands))/(4*pi)

    area = min(area,1-area)
    if radius is not None: #return in units of radius, set radius to 1.0 to get square radians
        return area * 4*pi*radius**2
    else: #return in ratio of sphere total area
        return area


