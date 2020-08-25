2#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 14:02:23 2020
Want to make plots of waveforms from plate interface events in 2006

@author: talongi
"""
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from obspy.core import read, UTCDateTime, stream
from obspy.core.stream import Stream
from obspy.signal.cross_correlation import correlate

from scipy.interpolate import interp1d
import geopy.distance

print('Closing all open plots.') #need to close all plots for pdf saving
plt.close('all')

os.chdir('/auto/proj/Cascadia/PermStatWF')
pwd = os.getcwd()

df = pd.read_csv('/auto/home/talongi/Cascadia/Data_tables/Events/NCSN_catalogs/nc_dd_pi_06_events.csv')
v_model = pd.read_csv('/auto/proj/Cascadia/GrowClust/Run1/IN/vzmodel.txt', sep = '\s+', names = ['depth', 'vp', 'vs'])
vp_interp = interp1d(v_model.depth, v_model.vp) #give the function a depth and it gives you the speed there.


limit_lon = (df.Longitude < -124.05) & (df.Longitude > -124.45)
print('number of events in cluster', np.sum(limit_lon))

cat = df[limit_lon]
cat = cat.sort_values(['Magnitude'], ascending = False)
cat = cat.reset_index(drop=True)
cat['DateTime'] = pd.to_datetime(cat.DateTime)


stations = {'KMPB' : (40.417190000000005,	-124.12076, .938),
            'KCR' : (40.42644,	-123.82064, .873),
            'KCT': (40.475570000000005,	-124.33748999999999, .378),
            'KCS' : (40.53791,	-123.51393999999999, 1.640)} #lat, lon, elevation (km)

    
def calc_hypo_distance(event,station):
    
    """enter event location in list or tuple, (lat,lon,depth) """
    g_circle_dist = geopy.distance.distance((event[0], event[1]), (station[0], station[1])).km
    total_depth = np.abs(event[2]) + np.abs(station[2])
    
    ray_dist = np.sqrt(g_circle_dist ** 2 + total_depth ** 2)
    return ray_dist
 
    
def travel_time(distance, velocity):
    time = distance / velocity
    return time


def plot_waveforms(obspy_stream):
    n = len(obspy_stream)
    
    if n > 1:
        stats = obspy_stream[0].stats
#        time_arr = np.linspace(0, stats.endtime - stats.starttime, stats.npts)
        
        fig = plt.figure(figsize = (8.5,11))
        fig.suptitle(stats.network + '.' + stats.station + '.' + stats.channel)
        
        for i,tr in enumerate(obspy_stream):
            time_arr = np.linspace(0, tr.stats.endtime - tr.stats.starttime, tr.stats.npts)
            
            plt.subplot(n,1,i+1)
            plt.plot(time_arr, tr, 'k', linewidth = 1)
            plt.text(time_arr.min() * 1, np.abs(tr.max() / 3), tr.stats.starttime, fontsize = 8) #plt time
            plt.text(time_arr.max(), np.abs(tr.max() * 0.5), str(i), fontsize = 8, color = 'darkorange') #plot index
            
        for ax in fig.get_axes():
            ax.label_outer()
            
        plt.xlabel('Seconds')
        
    else:
        print('not enough waveforms to generate meaningful plot')


def waveform_similarity(stream, vmin = None):
    """
    steam =  obspy stream of traces
    vmin = (float) minimum cross correlation coefficient for cc matrix
    """
    
    if len(st) > 1:
        stats = stream[0].stats
        n = len(stream)
        cc_arr = np.zeros((n,n))
        
        for i, tr in enumerate(stream):
            n_samples = len(tr)
            for j in np.arange(n):
                max_cc = correlate(tr, stream[j], shift = n_samples).max()
                
                cc_arr[i,j] = max_cc
                
        fig = plt.figure(figsize = (8.5,11))
        fig.suptitle(stats.network + '.' + stats.station + '.' + stats.channel)
        if vmin == None:
            plt.imshow(cc_arr, cmap = 'viridis', origin = 'lower')
        else:
            plt.imshow(cc_arr, cmap = 'viridis', origin = 'lower', vmin = vmin)
        for (j,i), label in np.ndenumerate(cc_arr.round(decimals = 2)):
            plt.text(i,j, label, ha = 'center', va = 'center', fontsize = 6)
        
        plt.xticks(np.arange(len(st)), color = 'darkorange')
        plt.yticks(np.arange(len(st)), color = 'darkorange')
        cbar = plt.colorbar(aspect = 50, orientation = 'horizontal')
        cbar.set_label('Cross Correlation Coefficient')
                
        return cc_arr

    else:
        print('there are not enough waveforms to warrant cross correlation')

def multipage(filename, figs=None, dpi=200):
    pp = PdfPages(filename)
    if figs is None:
        figs = [plt.figure(n) for n in plt.get_fignums()]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()


for stn in list(stations.keys())[:]:
    traces = []
    print(stn)
    for index, row in cat[:15].iterrows():
        origin_time = UTCDateTime(row.DateTime.to_pydatetime())
        
        ev_location = (row.Latitude, row.Longitude, row.Depth)
        stn_location = stations[stn]
        
        # calculate velocities from event location information
        Vp = vp_interp(row.Depth) * 0.95
        Vs = Vp / np.sqrt(3)
        
        # calculate the distances and theortical arrival times
        dist = calc_hypo_distance(ev_location, stn_location)
        P_arr = origin_time + travel_time(dist, Vp) #approx theoretical
        S_arr = origin_time + travel_time(dist, Vs)
        
        #set cuts
        begin = P_arr 
        end = S_arr + 3 
    
        day_wf = glob.glob(stn + '/' + '*' + str(origin_time.year) + '.' + str(origin_time.julday))
        
        if len(day_wf) == 1:
            fmt_file_name = pwd + '/' + day_wf[0] 
        
        else:
            print('Error finding correct file')
         
        t = read(fmt_file_name)[0]
        traces += read(fmt_file_name,
                       starttime = begin,
                       endtime = end)
        
    st = Stream(traces)
    
    # store prefilter data
    if len(st) > 1:
        st.write('/auto/home/talongi/Cascadia/Code/NC_PI_events/MSEED/' + stn + '.SAC')
    
    st.filter('bandpass', freqmin = 1, freqmax = 10, zerophase = True)
    st.sort(['starttime'])
    
    plot_waveforms(st)
    
    wf_similarity = waveform_similarity(st, vmin = 0.4)

#save all figures to a PDF
multipage('/auto/home/talongi/Cascadia/Figures/06_waveforms/waveforms_cc_matrix.pdf')
