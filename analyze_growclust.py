#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 12:51:02 2019
Modification of matlab code - moved to python
@author: talongi
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from obspy import read
from pyrocko import obspy_compat
from astropy.table import Table 

# ~~import Catalog
file = '/auto/home/talongi/Cascadia/Data_tables/Events/growclust_cat_run4.txt'
hdr_names = pd.array(['yr','mon','day','hr','min','sec', 
                      'evid', 
                      'lat','lon','depth','mag',
                      'qID', 'cID', 'nbranch',
                      'qnpair', 'qndiffP', 'qndiffS',
                      'rmsP', 'rmsS',
                      'eh', 'ez', 'et',
                      'latC', 'lonC', 'depC'])
cat = pd.read_csv(file, delim_whitespace=True, names = hdr_names)

#~~count arrivals append to last column of catalog dataframe
n_arrivals = []
for i in cat.evid:
    path = '/auto/proj/Cascadia/GrowClust/Run4/xcorr/Filtered3/' + str(i)   
    n_waveforms =  len(os.listdir(path))
    n_arrivals.append(n_waveforms)

N_arr = pd.DataFrame(n_arrivals, columns=['Narr'])
cat = pd.DataFrame.join(cat,N_arr)


# ~~import bounding box (bb)
file = '/auto/home/talongi/Cascadia/GMT/Growclust_map/cluster_box_lonlat.txt'
hdr_names_bb = pd.array(['lon','lat'])
bb = pd.read_csv(file, sep = ' ', names = hdr_names_bb)


def mask_catalog(catalog, max_lat, min_lat, max_lon, min_lon ,max_depth = [], min_depth = []):
    """ catalog should be a pandas data frame with catalog.lat, catalog.lon, & catalog.depth assigned
    """
    
    if type(max_depth) == list:    
        mask = np.all((catalog.lat > min_lat,
                        catalog.lat < max_lat,
                         
                        catalog.lon > min_lon,
                        catalog.lon < max_lon),
                        
                        axis = 0)
    
    else:
        mask = np.all((catalog.lat > min_lat,
                        catalog.lat < max_lat,
                         
                        catalog.lon > min_lon,
                        catalog.lon < max_lon,
    
                        catalog.depth > min_depth,
                        catalog.depth <= max_depth),
            
                        axis = 0)
                             
    return catalog[mask]

# bounding box mask
depth_range = (15, 19.5, 24.5)
bb_m_lower = mask_catalog(cat, bb.lat.max(), bb.lat.min(), 
                          bb.lon.max(), bb.lon.min(),
                          depth_range[2], depth_range[1])

bb_m_upper = mask_catalog(cat, bb.lat.max(), bb.lat.min(), 
                          bb.lon.max(), bb.lon.min(),
                          depth_range[1], depth_range[0])

#%%
# ~~ write to text file ||||| txt_hdr = ' '.join(hdr_names)
# lower cluster
format_L = bb_m_lower.sort_values(by = ['Narr'], ascending=False)
tL = Table.from_pandas(format_L)
tL.write(r'/auto/home/talongi/Cascadia/Data_tables/Events/Focal_mechanisms/below_plate_inter.txt',
        format='ascii.csv',
        overwrite=True)

# upper cluster
format_U = bb_m_upper.sort_values(by = ['Narr'], ascending=False)
tU = Table.from_pandas(format_U)
tU.write(r'/auto/home/talongi/Cascadia/Data_tables/Events/Focal_mechanisms/above_plate_inter.txt',
        format='ascii.csv',
        overwrite=True)  

#%% id first motions for spreadsheet.
obspy_compat.plant()

for index, row in format_U.iterrows():
    print(int(row['evid']), int(row['Narr']))
    event_id = int(row['evid'])
       
    stream = read('/auto/proj/Cascadia/GrowClust/Run4/xcorr/Filtered3/' + str(event_id) + '/*')
    stream.snuffle()
    
    input('Press Enter to Continue ....')


