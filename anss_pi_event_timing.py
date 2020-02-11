# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 10:01:21 2020

@author: Travis Alongi
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from obspy.core import UTCDateTime
plt.close()

with open('ANSS_1980-2019.csv') as f:
    header_names = f.readline().split(',')
        
catalog = pd.read_csv('anss_pi_events.txt', sep = '\s+', names = header_names )

utc_time = [UTCDateTime(time) for time in catalog.time]
time_mpl = np.array([UTCDateTime(time).matplotlib_date for time in catalog.time])

limits = np.linspace(time_mpl.min(), time_mpl.max(), 5)
limits = limits.round() #round to integer

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y-%m')

fig, ax = plt.subplots(1,1)
mask_0 = np.logical_and(time_mpl > limits[0], time_mpl < limits[1])
mask_1 = np.logical_and(time_mpl > limits[1], time_mpl < limits[2])
mask_2 = np.logical_and(time_mpl > limits[2], time_mpl < limits[3])
mask_3 = np.logical_and(time_mpl > limits[3], time_mpl < limits[4])

ax.scatter(time_mpl, catalog.depth/1e3, catalog.mag**3, 'k', alpha = 0.5)

ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(years_fmt)
ax.set_xlim([limits.min(), limits.max()])
ax.tick_params(axis = 'x', labelsize = 6)
fig.autofmt_xdate()
fig.tight_layout()
ax.set_ylabel('Depth [km]')


fig, ax = plt.subplots(1,1)
mask_0 = np.logical_and(time_mpl > limits[0], time_mpl < limits[1])
mask_1 = np.logical_and(time_mpl > limits[1], time_mpl < limits[2])
mask_2 = np.logical_and(time_mpl > limits[2], time_mpl < limits[3])
mask_3 = np.logical_and(time_mpl > limits[3], time_mpl < limits[4])

ax.scatter(time_mpl, catalog.latitude, catalog.mag**3, 'k', alpha = 0.5)
winsize = 200
plt.plot(time_mpl, catalog.latitude.rolling(winsize).median(), 'r-')
plt.plot(time_mpl, catalog.latitude.rolling(winsize).median() + catalog.latitude.rolling(winsize).std(), 'r:')
plt.plot(time_mpl, catalog.latitude.rolling(winsize).median() - catalog.latitude.rolling(winsize).std(), 'r:')


from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
kfit = KMeans(n_clusters = 4).fit(np.column_stack((time_mpl, catalog.latitude)))
kfit_centroids = kfit.cluster_centers_
t, la = kfit_centroids.T
plt.plot(t,la,'g*')

gfit = GaussianMixture().fit_predict(np.column_stack((time_mpl, catalog.latitude)))

ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(years_fmt)
ax.set_xlim([limits.min(), limits.max()])
ax.tick_params(axis = 'x', labelsize = 6)
fig.autofmt_xdate()
fig.tight_layout()
ax.set_ylabel('Depth [km]')