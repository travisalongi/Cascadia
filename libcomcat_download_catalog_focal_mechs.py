#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 12:00:47 2020
code to download earthquake catalog
remember to load correct environment in order to use the libcomcat library
@author: talongi
"""

from libcomcat.dataframes import get_summary_data_frame, get_detail_data_frame
from libcomcat.search import search, DetailEvent
from datetime import datetime


events = search(starttime = datetime(2006,10,30),
                endtime = datetime(2006,11,15),
                minlatitude = 40.4,
                maxlatitude = 40.6,
                minlongitude = -125,
                maxlongitude = -123)

detail_events = get_detail_data_frame(events)

#detail_events.to_csv('/auto/home/talongi/Cascadia/Data_tables/Events/ANSS_1980-2019_detailed.csv')

#%%
#find nans
import numpy as np
import pandas as pd

index_match = []
for i, x in enumerate(detail_events.nc_np1_strike):
    if type(x) == str:
        index_match.append(i)
        
foc_mech_cat = detail_events.iloc[index_match] 

mo = np.ones(foc_mech_cat.shape[0]) * 4
exp = np.ones(foc_mech_cat.shape[0]) * 23
zeros = np.zeros(foc_mech_cat.shape[0])

foc_mech_fmt = {'lon' : foc_mech_cat.longitude.values,
                'lat' : foc_mech_cat.latitude.values,
                'dep' : foc_mech_cat.depth.values,
                'st1' : foc_mech_cat.nc_np1_strike.values,
                'dip1' : foc_mech_cat.nc_np1_dip.values,
                'rake1' : foc_mech_cat.nc_np1_rake.values,
                'st2' : foc_mech_cat.nc_np2_strike.values,
                'dip2' : foc_mech_cat.nc_np2_dip.values,
                'rake2' : foc_mech_cat.nc_np2_rake.values,
                'mo_base' : mo,
                'mo_exp' : exp,
                'z1' : zeros,
                'z2' : zeros}
df = pd.DataFrame(foc_mech_fmt)

path = '/auto/home/talongi/Cascadia/GMT/06_Plate_interface_map/fm_list.csv'
df.to_csv(path,sep = ',', header = False, index = False)