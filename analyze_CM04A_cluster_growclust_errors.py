#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 11:48:57 2019
Makes cross sectional plot of cm04 cluster events
converts to utm for distance calculation (not used)
converts columns into UTCDateTime format
@author: talongi
"""

import pandas as pd
import numpy as np
import utm
import matplotlib.pyplot as plt
from obspy.core.utcdatetime import UTCDateTime

cat_file = '/auto/home/talongi/Cascadia/Data_tables/Events/growclust_cat_run4.txt'

# import growclust catalog
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

# =============================================================================
# # Bounding box
# =============================================================================
x1 = -124.15
x2 = -124.05
y1 = 40.63
y2 = 40.55
z1 = 14
z2 = 25

mlon = np.logical_and(df.lonR > x1, df.lonR < x2) 
mlat = np.logical_and(df.latR > y2, df.latR < y1)
mdep = np.logical_and(df.depR > z1 ,df.depR < z2)

# cast multiple logicals together
mbox = np.logical_and(np.logical_and(mlon,mlat), mdep)

# mask data
df_masked = df[mbox]



# =============================================================================
# convert to utm for distance calc. - format date - format - coords
# =============================================================================
d = np.zeros(len(df))
dt = []
coords = np.array([])
for i in (df_masked.depR.index):
    # convert lat/lon to utm
    utm_R = utm.from_latlon(df.latR[i], df.lonR[i])
    easting_R = utm_R[0]/1e3
    northing_R = utm_R[1]/1e3
    
    utm_C = utm.from_latlon(df.latC[i], df.lonC[i])
    easting_C = utm_C[0]/1e3
    northing_C = utm_C[1]/1e3
    
    form = np.array([easting_R, northing_R, df.depR[i],
                     easting_C, northing_C, df.depC[i]])
    
    # matrix of coordinates
    coords = np.append(coords, form)
    
    # calc distance between relocations
    d[i] = np.linalg.norm(form[:3] - form[3:])
    
    # format dates
    dt1 = UTCDateTime(df.yr[i], df.mon[i], df.day[i])
    dt.append(dt1)
    
# reformat coordinate data    
coords = np.split(coords, len(df_masked))
x,y,z,u,v,w = zip(*coords) #x,y,z relocations-- u,v,w orig locs

# =============================================================================
# make figure                  
# =============================================================================
fig1 = plt.figure(1, figsize = (12,12))
plt.errorbar(x, z, 
             xerr = df_masked.eh, 
             yerr = df_masked.ez,
             fmt = '.',
             alpha = 0.5,
             linewidth = 1.2,
             markeredgecolor = 'gray',
             markerfacecolor = 'black',
             clip_on = True
             ,label = 'GrowClust Locations')

plt.plot(u,w,'1', 
         ms = 10, color = 'gray', 
         label = 'SimPS Locations')
lgd = plt.legend(frameon = False)

plt.scatter(x,z, 
            s = 1e2 * df_masked.mag **2,
            c = dt,
            alpha = 0.5,
            cmap = 'RdYlBu',
            label = 'GrowClust Locations')


plt.xlim([403, 412])
plt.ylim([14,25])
plt.xlabel('Easting UTM 10 [km]')
plt.ylabel('Depth [km]')

cbar = plt.colorbar()
cbar.set_label('Time')
cbar.ax.set_yticklabels([''])

fig1.gca().invert_yaxis()
  