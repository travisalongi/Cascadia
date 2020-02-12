#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 15:07:56 2020
Look at magnitude of completeness for a NCSN catalogs
Standard & Double Difference. 
Onshore vs. Offshore, superposition of two completeness levels.
Plot onshore as a function of time with a sliding window of 3 years.
@author: talongi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from eqcorrscan.utils.mag_calc import calc_max_curv
plt.close('all')

dd = pd.read_csv('/auto/home/talongi/Cascadia/Data_tables/Events/NC_DD_catalog.csv',
                 skiprows = 13)

nc = pd.read_csv('/auto/home/talongi/Cascadia/Data_tables/Events/NC_std_catalog.csv',
                 skiprows = 13)

print('NC standard catalog Mc = ', calc_max_curv(nc.Magnitude))
print('NC double diference calc = ' + str(calc_max_curv(dd.Magnitude)))



fig, (ax1, ax2) = plt.subplots(nrows = 2, ncols= 1)
bin_edges = np.arange(0,8,0.05)
ax1.hist(dd.Magnitude, bin_edges)
ax2.hist(nc.Magnitude, bin_edges)

ax1.set_yscale('log')
ax2.set_yscale('log')



# Magnitude of completeness onshore vs offshore 
shoreline = -124.4

offshore = dd[dd.Longitude < shoreline]
onshore = dd[dd.Longitude > shoreline]

mc_off = calc_max_curv(offshore.Magnitude)
mc_on = calc_max_curv(onshore.Magnitude)


# Calc completness for sliding window
years = np.array([row.DateTime.split('/')[0] for i,row in onshore.iterrows()]).astype(int)
mags = onshore.Magnitude.values

mag_completenesses = []
for year in np.unique(years[years > 1980]):
    boolean = (years >= year - 1) & (years <= year + 1)
    Mc = calc_max_curv(mags[boolean])
    print(year, np.sum(boolean), Mc)
    mag_completenesses.append(Mc)

plt.figure()        
plt.plot(np.unique(years[years > 1980]), mag_completenesses, ':o')
plt.xlim([min(years), max(years)])
plt.ylabel('Magnitude of Completeness')
plt.title('Onshore Southern Cascadia - NCSN Double Difference Catalog')
