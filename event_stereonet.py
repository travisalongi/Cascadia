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
import pandas as pd
import mplstereonet
from matplotlib.pyplot import cm
from obspy.imaging.beachball import beachball, aux_plane
plt.close('all')

def find_matches(listlike, pattern):
    """ 
    looks through a list for matches like startswith* -- does not require wildcard
    returns boolean - like mask
    """
    S = pd.Series(listlike)
    mask = S.str.contains(pattern)
    return mask
    

class event:
    
    def __init__(self, az, toa, pol, stn = None, event_id = None, strike = None, dip = None, rake = None):
        """ 
        
        is a container for event
        az = list type of azimuths
        toa = list type of take of angles
        pol = first motion polarity (up = 1, down = 0)
        stn = list of stations that should be same length of az, toa, and pol
        event_id = unique event id
        
        
        """
        
        # if len(az) != len(toa): 
        #     print('toa & az inputs are not same length')
        
        # if len(toa) != len(pol):
        #     print('toa & polarity inputs are not same length')
       
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
        
        if type(pol[0]) == str:
                b = pol == 'u'
                pol = b.astype(int)
                
        #Instances of Class
        self.az = np.array(az)
        self.toa = np.array(toa)
        self.pol = np.array(pol)
        self.stn = np.array(stn)
        self.event_id = event_id
        self.strike = np.array(strike)
        self.dip = np.array(dip)
        self.rake = np.array(rake)
        
        
        # calculated instances
        self.aux_plane = aux_plane(self.strike, self.dip, self.rake)
        self.trend = np.asarray(trend_lst)
        self.plunge = np.asarray(plunge_lst)
    
    
    def reverse_pol(self, pattern):
       """reverses the polarity of stations matching pattern"""
       print(self.pol)
       mask = find_matches(self.stn, pattern) #find matches to pattern
       
       polarities = pd.Series(self.pol, dtype = bool) #polarities as a Series
       
       polarities.loc[mask] = ~polarities #swap polarites of stations
       polarities = polarities.astype(int)
       
       print(polarities)
       
       self.pol = polarities
       
       
       
       
       
       
    
    
    def beachball(self, color = 'gray'):
        """makes obspy beachball"""
        beachball([self.strike, self.dip, self.rake], facecolor = color)
    
        
        
    def fm_plot(self):
        """make a stereonet plot of event with first motions
        up = 1 --- close ciricles
        down = 0 --- open circles
        """

        fig = plt.figure(figsize = (6,6))
        ax = fig.add_subplot(111, projection = 'stereonet')
        ax.grid()
        
        #plot up arrivals
        up = self.pol == 1   
        ax.line(self.plunge[up], self.trend[up], 
                c = 'k', label = 'up')
    
        #plot down arrivals
        down = self.pol == 0
        ax.line(self.plunge[down], self.trend[down], 
                c = 'k', label = 'down', fillstyle = 'none')
        
        
        #instances of class as booleans
        self.up = up
        self.down = down
               
        if self.event_id != None:
            title_string = 'Event ID = ' + str(self.event_id)
            ax.set_title(title_string, fontsize = 18, loc = 'left')
            
        if self.strike != None:
            ax.plane(self.strike, self.dip, self.rake, color = 'black') #fault plane
            ax.plane(self.aux_plane[0], self.aux_plane[1], self.aux_plane[2], color = 'black')
            
                              
            
            
            

