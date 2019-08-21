#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:47:18 2019
@author: talongi
"""
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import definitions as my

catalog = my.load_growclust_catalog('/auto/home/talongi/Cascadia/Data_tables/Events/growclust_cat_run4.txt')
xi,yi,zi, df_interace, utm = my.load_interface('/auto/proj/Cascadia/scripts/McCrory_2012/cascadia_grid_gmt_3D.xyz',
                                          lat_max = 41,
                                          lat_min = 40,
                                          lon_max = -123,
                                          lon_min = -125,
                                          n_grid_points = 2000,
                                          convert2UTM = True)

#convert depths to meters
catalog.depR = -catalog.depR * 1e3
zi = zi * 1e3

#format data to xyz
cat_utm = my.convert_latlon2utm(catalog.latR, catalog.lonR)
cat_xyz = np.column_stack((cat_utm[0], cat_utm[1], catalog.depR))

int_xyz = np.column_stack((xi.flat, yi.flat, zi.flat))
int_xyz = int_xyz[~np.isnan(zi.flat)] #remove nans

pi_distances = my.calc_min_dist(cat_xyz, int_xyz) #calc distances
catalog['pi_dist'] = pi_distances

plt.figure(1, figsize = (10,9))
plt.hist(pi_distances, bins = 20)

dist_cutoff = 5e3
mask = (pi_distances < dist_cutoff) & (catalog.mag > 1.5)
interface_catalog = catalog[mask]

e_ID = interface_catalog.eID
e_ID.to_csv('evid_pi_events.txt',
            sep = '\t',
            index = False,
            header = False)
