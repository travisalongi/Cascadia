#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 14:21:10 2020

Examine growclust catalog in search of other clusters

@author: travisalongi
"""


from datetime import datetime
import import_data as imp
import numpy as np
import matplotlib.pyplot as plt

gc_file = '/Users/travisalongi/Cascadia/Data_tables/Events/growclust_cat_run4.txt'
d = imp.growclust_catalog(gc_file)

# plot lat vs time
fig, ax = plt.subplots(figsize = (11,7))
sc = ax.scatter(d.datetime, d.lat, (d.mag + 1)**3, d.depth, 
                alpha = 0.8,
                edgecolor = 'black',
                linewidth = 0.5,
                vmin = 0,
                vmax = 40)
ax.set_ylabel('Latitude')
ax.set_ylim([40,40.9])

cb = fig.colorbar(sc, aspect = 30, pad = 0.01)
cb.set_label('Depth')

# fig.tight_layout()
fig.autofmt_xdate()
ax.set_title('Growclust Relocations')