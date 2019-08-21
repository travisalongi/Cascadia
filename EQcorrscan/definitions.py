#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:47:18 2019
@author: talongi
"""
import time
import pandas as pd
import numpy as np
import utm
from scipy.interpolate import griddata
from sklearn.neighbors import NearestNeighbors

def convert_latlon2utm(lat, lon):
    """ converts lat lon coords to utm coords
    outputs:
        0 = easting
        1 = northing """
    lat = lat.to_list()
    lon = lon.to_list()
    easting = np.zeros(len(lon))
    northing = np.zeros(len(lat))
    for i, x in enumerate(zip(lat,lon)):
        in_utm = utm.from_latlon(x[0], x[1])
        easting[i], northing[i] = in_utm[0], in_utm[1]
    return easting, northing

def load_interface(textfile, lat_max, lat_min, lon_max, lon_min, 
                   n_grid_points = 1000, int_type = 'linear',
                   convert2UTM = False):
    """ takes surface file in xyz fand interpolates a 3D surface
    the resolution is limited by number of grid points.
    returns surface data in xyz"""
    hdr_names = np.array(['x', 'y', 'z'])
    data = pd.read_csv(textfile, sep = ',', names = hdr_names)
    lon_mask = np.logical_and(data.x > lon_min, data.x < lon_max)
    lat_mask = np.logical_and(data.y > lat_min, data.y < lat_max)
    mask = np.logical_and(lon_mask, lat_mask)
    data = data[mask]
    
    if convert2UTM == True:
        data.x, data.y = convert_latlon2utm(data.y, data.x)
        
    xi = np.linspace(min(data.x), max(data.x), n_grid_points)
    yi = np.linspace(min(data.y), max(data.y), n_grid_points)    
    X, Y = np.meshgrid(xi,yi) #make grid
    # interpolate the vlaues of z for all points in rectangular grid
    Z = griddata((data.x, data.y), data.z, (X, Y), method = int_type)
    return X, Y, Z, data, utm

def load_growclust_catalog(cat_file):
    # see growcluster userguide for explaination of each column
    hdr_names = ['yr','mon','day','hr','min','sec',
                 'eID', 
                 'latR','lonR','depR',
                 'mag', 
                 'qID','cID','nbranch',
                 'qnpair', 'qndiffP', 'qndiffS',
                 'rmsP', 'rmsS',
                 'eh', 'ez', 'et',
                 'latC', 'lonC', 'depC'] 
    df = pd.read_csv(cat_file, sep = '\s+', names = hdr_names )
    return df
        

def calc_min_dist(data_xyz, interface_xyz, algorithm = 'ball_tree'):
    """calculate min distance from event to point along interpolated surface
    min. dist. calc w/ knn
    data_xyz are points in lat,lon,depth (m)
    interface_xyz are points like data
    """
    t0 = time.time()
    dist_arr = np.zeros(data_xyz.shape[0])
    model = NearestNeighbors(n_neighbors = 1, algorithm = algorithm).fit(interface_xyz)   
    
    # calculate distances knn method
    for i,x in enumerate(data_xyz):
        x = x.reshape(1,3)
        d_min_dist = model.kneighbors(x)[0].min(axis = 1)
        dist_arr[i] = d_min_dist      
    print(time.time() - t0)    
    return dist_arr

