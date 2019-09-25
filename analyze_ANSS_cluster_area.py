#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 16:42:32 2019
Look at anss catalog seismicity for CM04A cluster region
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

data_file = '/auto/home/talongi/Cascadia/Data_tables/Events/ANSS_1980-2019_CM04A_region.csv'

df = pd.read_csv(data_file, sep = ',')

# threshold the data
mask = df.mag > 1.8 # completeness approx 1.8
df = df[mask]

times = [UTCDateTime(time) for time in df.time] #remove word template
times_mpl = [time.matplotlib_date for time in times] #date in matplotlib format

#figure
date_format = DateFormatter("%Y-%m-%d")
cmap = plt.get_cmap('jet', 30)
fig, ax1 = plt.subplots( figsize = (18,8))
im = ax1.scatter(times_mpl, df.mag, color = 'black', 
                 alpha = 0.35,
                label = 'ANSS Catalog Events')

# format x-axis for date
ax1.xaxis.set_major_formatter(date_format) 
ax1.set_ylabel('Magnitude')

ax2 = ax1.twinx()

ax2.plot(times_mpl, np.arange(len(times_mpl)), 
         ':k', linewidth = 3, color = 'darkred')

plt.setp(stemlines, linewidth = 0.5, color = 'gray')
plt.setp(baseline, color = 'gray')

ax2.set_ylabel('Cumulative Number of Events', color = 'darkred')

plt.xticks(np.linspace(min(times_mpl), max(times_mpl), 18 ))
ax1.legend()
plt.grid(axis = 'y')
fig.autofmt_xdate()

