#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 11:50:37 2019
Similar to make_focal_mechs.py but Object Oriented
@author: talongi
"""
import os
import matplotlib.pyplot as plt
import numpy as np
import mplstereonet
from matplotlib.pyplot import cm
plt.close()

class event:
    
    def __init__(self, az, toa, pol, stn = 'none', event_id = 'none'):
        
        if len(az) != len(toa): 
            print('toa & az inputs are not same length')
        
        if len(toa) != len(pol):
            print('toa & polarity inputs are not same length')
       
        trend_lst = []
        plunge_lst = []
        for i, t in enumerate(toa):
            if t >= 90:
                if az[i] <= 180:
                    trend = az[i] + 180
                    plunge = toa[i] - 90
                else:
                    trend =  az[i] -180
                    plunge = toa[i] - 90
                        
            else:
                trend = az[i]
                plunge = 90 - toa[i]
                
            trend_lst.append(trend)
            plunge_lst.append(plunge)
        
        #Instances of Class
        self.az = az
        self.toa = toa
        self.pol = pol
        self.stn = stn 
        self.event_id = event_id
        
        self.trend = np.asarray(trend_lst)
        self.plunge = np.asarray(plunge_lst)
        
    def plot(self):

        fig = plt.figure(figsize = (12,6))
        ax = fig.add_subplot(111, projection = 'stereonet')
        ax.grid()
        
        #plot up arrivals
        up = self.pol == 1   
        ax.line(self.plunge[up], self.trend[up], c = 'k')
    
        #plot down arrivals
        down = self.pol == 0
        ax.line(self.plunge[down], self.trend[down], c = 'k',
                fillstyle = 'none')
               
        if self.event_id != 'none':
                title_string = 'Event ID = ' + str(self.event_id)
                ax.set_title(title_string, fontsize = 18, loc = 'left')

       

pol = np.zeros_like(toa)
pol[1] = 1            
          
e = event(az, toa, pol)     
#%%
"""        
 