#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 13:48:25 2019
interplotes plate interface and grabs events from anss catalog within specified distance
creates new catalog for reading into gmt
tested some mapping packages but abandoned
@author: talongi
"""

import pandas as pd
import numpy as np
import cartopy as cart
import matplotlib.pyplot as plt
from obspy.core import UTCDateTime
from matplotlib.dates import DateFormatter
import definitions as my
plt.close('all')

lat_max = 41.5
lat_min = 39.5
lon_west = -125
lon_east = -123

catalog = pd.read_csv('/auto/home/talongi/Cascadia/Data_tables/Events/ANSS_1980-2019.csv')

#Use either model below 1) McCrory 2) Hayes
xi,yi,zi, df_interace, utm = my.load_interface('/auto/proj/Cascadia/scripts/McCrory_2012/cascadia_grid_gmt_3D.xyz',
                                          lat_max,
                                          lat_min,
                                          lon_west,
                                          lon_east,
                                          lon_n_grid_points=5e3,
                                          lat_n_grid_points=5e3,
                                          convert2UTM = True)





#convert depths to meters
catalog.depth = -catalog.depth * 1e3
zi = zi * 1e3

#format data to xyz
cat_utm = my.convert_latlon2utm(catalog.latitude, catalog.longitude)
cat_xyz = np.column_stack((cat_utm[0], cat_utm[1], catalog.depth))

int_xyz = np.column_stack((xi.flat, yi.flat, zi.flat))
int_xyz = int_xyz[~np.isnan(zi.flat)] #remove nans

pi_distances = my.calc_min_dist(cat_xyz, int_xyz) #calc distances
catalog['pi_dist'] = pi_distances

plt.figure(1, figsize = (10,9))
plt.hist(pi_distances/1e3, bins = 20)

dist_cutoff = 5e3
mask = (pi_distances < dist_cutoff) & (catalog.mag > 1.0) & (catalog.rms < 2) & (catalog.depthError < 3)
interface_catalog = catalog[mask]
decimal_time = time_decimal = [UTCDateTime(time).strftime('%Y.%j') for time in interface_catalog.time]
interface_catalog['decimal_time'] = decimal_time

interface_catalog.to_csv('anss_pi_events.txt',
            sep = '\t',
            index = False,
            header = False)

#%%
utc_time = [UTCDateTime(time) for time in interface_catalog.time]
time_mpl = [UTCDateTime(time).matplotlib_date for time in interface_catalog.time]
time_decimal = [UTCDateTime(time).strftime('%Y.%j') for time in interface_catalog.time]

years = [1981 + i*5 for i in range(8)]
dates_colorbar = [UTCDateTime(year,1,1) for year in years]
dates_colorbar_mpl = [date.matplotlib_date for date in dates_colorbar]

plt.close()
plt.figure(1)
plt.stem()

fig2 = plt.figure(2)
ax = plt.axes(projection = cart.crs.epsg(2926))
ax.add_feature(cart.feature.COASTLINE)
plt.scatter(interface_catalog.longitude, 
            interface_catalog.latitude, 
            (interface_catalog.mag) ** 3,
            time_mpl,
            alpha = 0.75)
cb = plt.colorbar()
cb.set_ticks(dates_colorbar_mpl)
cb.ax.set_yticklabels(years)

plt.figure(3)
dmask = np.abs(catalog.depth) < 40e3 #remove very deep events.
plt.scatter(catalog.longitude[dmask],
            catalog.latitude[dmask],
            catalog.mag[dmask],
            catalog.depth[dmask], 
            alpha = 0.5)
plt.colorbar()

from mpl_toolkits.mplot3d import Axes3D
fig4 = plt.figure(4)
ax = fig4.add_subplot(111, projection = '3d')
ax.scatter3D(interface_catalog.longitude, 
             interface_catalog.latitude,
             interface_catalog.depth,
             c = time_mpl)

