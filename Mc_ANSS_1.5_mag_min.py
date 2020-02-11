# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 14:25:18 2020

@author: USGS Kluesner
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from obspy.core import UTCDateTime
from eqcorrscan.utils.mag_calc import calc_max_curv, calc_b_value


def rolling_window(array, window_size, step_size):
    """"makes array of rolling windows, where each row is a new rolling window"""
    half_win = window_size / 2
    min_index = int(half_win)
    max_index = int(len(array) - half_win)
    
    arr_of_arrays = np.array([])
    
    for index in np.arange(min_index, max_index + 1, step_size):                
        w_index = np.arange(index - half_win, index + half_win, dtype = int)
        b = array[w_index]
        
        if len(arr_of_arrays) == 0:
            arr_of_arrays = b
            
        else: 
            arr_of_arrays = np.vstack((arr_of_arrays, b))
        
    return arr_of_arrays
      


catalog = pd.read_csv('1980-2020ANSS_events.csv')
years = np.array([row.time.split('-')[0] for i,row in catalog.iterrows()]).astype(int)
mags = catalog.mag.values

mag_completenesses = []
for year in np.unique(years):
    boolean = [years == year]
    Mc = calc_max_curv(mags[boolean])
    print(year, np.sum(boolean), Mc)
    mag_completenesses.append(Mc)
    
plt.plot(np.unique(years), mag_completenesses, 'o')


