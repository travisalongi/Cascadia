#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 13:33:53 2020
Makes make of events + focal mechanisms
Last updated for AGU-2020

@author: travisalongi
"""
# =============================================================================
# imports
# =============================================================================
import pygmt as gmt
import pandas as pd
import numpy as np
import import_data as imp
import utm


save_file = 'gorda_plate_map.png'

# Comcat events
comcat_file = '/home/talongi/Zephyrus_share/Cascadia/Data_tables/Events/comcat_1980-2019_gorda_detailed.csv'
df = imp.comcat_detailed(comcat_file)
cat = df.sort_values('mag', ascending=False)


# subset with focal mechanisms
fm = cat[~np.isnan(cat.nc_np1_strike)]
e_lon = fm.lon
e_lat = fm.lat

#%%
# =============================================================================
# #init fig
# =============================================================================
fig = gmt.Figure()
gmt.config(FORMAT_GEO_MAP = 'D')
gmt.config(FONT = '14,Helvetica,Black')
gmt.config(MAP_FRAME_TYPE = 'plain')
gmt.config(MAP_FRAME_AXES = 'WesN')

#set up region
buffer = 0.1
map_region = [e_lon.min() - buffer,
              e_lon.max() + buffer,
              e_lat.min() - buffer,
              e_lat.max() + buffer]

fig.basemap(region=map_region, 
            projection="M8i", 
            # frame = True)
            B = '0.5f0.25')

fig.coast(shorelines=True, 
           land = 'cornsilk',
           water = 'lightcyan',
          T = str(((map_region[1] - map_region[0]) * 0.1) + map_region[0]) + '/' + str(((map_region[-1] - map_region[-2]) * 0.18) + map_region[-2]) + '/' + "0.45i",
          L = str(((map_region[1] - map_region[0]) * 0.1) + map_region[0]) + '/' + str(((map_region[-1] - map_region[-2]) * 0.1) + map_region[-2]) + '/' + str(((map_region[-1] - map_region[-2]) * 0.65) + map_region[-2]) + '/' + "3" )



#colormap for event depths
gmt.makecpt(cmap="buda", 
            series=[5, 30], output = 'buda_temp.cpt')
gmt.makecpt(cmap="buda", 
            series=[5, 30])

#events --- comcat
fig.plot(x = cat.lon, y = cat.lat, sizes = cat.mag/10, color = cat.depth,
          cmap = True, style = 'c', pen = 'black', t = 75)

# fm_file = '/home/talongi/Zephyrus_share/Cascadia/Data_tables/Focal_mechs/comcat_fm_gorda_1980_2019.csv'
# fig.meca(fm_file, '0.5c', convention = 'gcmt', t = 25)


# focal mechanisms
focal_mechanisms = dict(strike = fm.nc_np1_strike.to_list(), 
                        dip = fm.nc_np1_dip.to_list(), 
                        rake = fm.nc_np1_rake.to_list(), 
                        magnitude = fm.mag.to_list())
fig.meca(focal_mechanisms, scale = '0.75', 
         longitude = fm.lon.values, 
         latitude = fm.lat.values, 
         depth = fm.depth.values,
         # convention = 'aki',
         # G = 'green',
         W = 'red',
         Z = 'buda_temp.cpt')


fig.legend()
fig.colorbar(frame='15a10f+l"Depth (km)"',
             position = 'JBC+w8i/0.1ih')

# fig.show()
fig.show(method = 'external')
fig.savefig(save_file)
