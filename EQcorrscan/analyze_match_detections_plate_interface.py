#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 16:34:05 2019

reformat detections file
#header
sed -n 1p Detections.csv >> detections.csv 
#every other line
sed -n 2~2p Detections.csv >>detections.csv

@author: talongi
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.colors import BoundaryNorm
from matplotlib import ticker
from obspy.core.utcdatetime import UTCDateTime
plt.close('all')
data_dir = '/auto/proj/Cascadia/EQcorrscan/Plate_interface/Run2/Detections/Detections_2009-2014.csv'

cluster = pd.read_csv('/auto/home/talongi/Cascadia/Data_tables/Events/cm04cluster.txt', sep = '\s+')

df = pd.read_csv(data_dir, sep = ',')
df = df.values[:-1,:]

t_temp = df[:,0] #template string
t_temp = [time.split('_')[1] for time in t_temp] #remove word template
evid = [int(ev[-7:-3]) for ev in t_temp] # get evid from near end of string
t_temp = [UTCDateTime(time.split('Z')[0]) for time in t_temp] #assigns t_temp as utc datetime object
t_det = [UTCDateTime(time) for time in df[:,1]] #change strings in utc datetime object
chan = df[:,2]
det_val = df[:,3]
avg_cc = df[:,4]

t_det_mpl = [date.matplotlib_date for date in t_det] #date in matplotlib format
t_temp_unique = np.unique(np.asarray(t_temp))

# back to dataframe
dic = {'temp_time':t_temp, 
       'evid': evid,
       'det_time': t_det,
       'chan': chan,
       'det_val': det_val,
       'avg_cc' : avg_cc}
df = pd.DataFrame(dic)

g = df.groupby('evid')
keys = g.groups.keys()
keys = [str(k) for k in keys]

#figure
date_format = DateFormatter("%Y-%m-%d")
cmap = plt.get_cmap('jet', 30)
fig, ax1 = plt.subplots( figsize = (18,8))
im = ax1.scatter(t_det_mpl, df.avg_cc, s = 10*df.chan.astype(float)*3, 
                 c = g.ngroup(), 
                cmap = cmap, alpha = 0.55,
                label = 'Detected Events')
ax1.plot(np.full((2),UTCDateTime(2014,3,10).matplotlib_date), [0.6,1], 'r') #plot M6.8 event

cbar = fig.colorbar(im, ax = ax1, cmap = cmap)

# set number of color bar ticks
tick_locator = ticker.MaxNLocator(len(t_temp_unique))
cbar.locator = tick_locator
cbar.update_ticks()

# set colorbar labels to string
cbar.ax.set_yticklabels(keys)
cbar.set_label('Event ID of Template')

# format x-axis for date
ax1.xaxis.set_major_formatter(date_format) 
ax1.set_ylabel('Average Cross Correlation')

#ax2 = ax1.twinx()
#
#ax2.plot(t_det_mpl, np.arange(len(t_det_mpl)), 
#         ':k', linewidth = 3, color = 'darkred')
#markerline, stemlines, baseline = ax2.stem(cluster.datetime_mpl, np.ones_like(cluster.datetime_mpl) * len(avg_cc), 
#                                           markerfmt = ' ', 
#                                           label = 'Picked Events')
#plt.setp(stemlines, linewidth = 0.5, color = 'gray')
#plt.setp(baseline, color = 'gray')

ax2.set_ylabel('Cumulative Number of Detected Events', color = 'darkred')

plt.xticks(np.linspace(min(t_det_mpl), max(t_det_mpl), 18 ))
plt.legend()
plt.grid(axis = 'y')
fig.autofmt_xdate()

