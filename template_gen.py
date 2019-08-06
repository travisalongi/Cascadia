#!/usr/bin/python
"""
Similar to Run2 removing cm stations adding stations KHMB
generating more templates
""" 
import time
import os, sys, glob, shutil

import numpy as np
import pickle

from obspy.core import read, UTCDateTime, Stream, Trace, trace
from obspy.signal.filter import bandpass
from obspy.core.event import read_events, Catalog, Event, Magnitude, Origin, Pick, Arrival, WaveformStreamID, Comment, CreationInfo, ResourceIdentifier


from multiprocessing import cpu_count
from eqcorrscan.utils import pre_processing, catalog_utils, plotting
from eqcorrscan.utils.plotting import pretty_template_plot
import matplotlib.pyplot as plt
from eqcorrscan.core import template_gen

init_time = time.time()
plt.close('all')
plt.ioff() #prevents plots pop ups

# =============================================================================
# ## 1. CREATE A CATALOG OF EVENTS ON DAY OF INTEREST FROM ANTELOPE DATABASE 
# =============================================================================
print("CREATING DATABASE EVENT CATALOG") 

with open("/auto/proj/Cascadia/EQcorrscan/CM04Cluster/evid_greatest_M.txt") as file: #with statement auto closes txtfile
    events_clust = [line.strip() for line in file] # assign events to list

##CREATE CATALOG OF TEMPLATES FROM ANTELOPE EVENTS 
out=pickle.load(open('all_event_arrivals_6.28.2019.pkl','rb')) #dictionary of picks
out_3=[] # list of lists of pick informations

for ev in events_clust: 
    for i, events in enumerate(out):
        out_et=out[i][1::11] #time is 1st entry skip 11 entries gets times
        out_lat=out[i][6::11] #all lats
        out_long=out[i][7::11] # all lons
        if len(out_et) > 1:
            et = UTCDateTime(out_et[0])
            lats = out_lat[0]
            lons = out_long[0]
            if str(out[i][0]) == str(ev):
                out_3.append(out[i])


db_catalog = Catalog() # start empty catalog
#Append picks and events from db to Catalog 
for i, events in enumerate(out_3):
    event=Event()    
    picks=Pick()
    origin=Origin()
    arrival=Arrival()
    e_time=out_3[i][1::33]
    sta = out_3[i][2::33]
    cha = out_3[i][3::33]
    phase = out_3[i][4::33]
    pick_time = out_3[i][5::33] #phase pick time
    lat = out_3[i][6::33]
    lon = out_3[i][7::33]
    orid=out_3[i][8::33]
    dep = out_3[i][9::33]
    ml=out_3[i][10::33]
    for x, times in enumerate(pick_time):
        event.resource_id=str(out_3[i][0]) #assign evid
        rd = str(out_3[i][0])
        picks = Pick(resource_id=rd, time=UTCDateTime(pick_time[x]), 
               waveform_id = WaveformStreamID(network_code="CI", station_code=str(sta[x]), channel_code=str(cha[x])), phase_hint=str(phase[x]))
        origin = Origin(resource_id=(str(orid[x])), 
                  time = UTCDateTime(e_time[x]), 
                  longitude= str(lon[x]), 
                  latitude=str(lat[x]), 
                  depth=str(dep[x]))
        magnitude = Magnitude(mag = ml[x], magnitude_type = "M", origin_id = (str(orid[x]))) 
        arrival = Arrival(pick_id = rd, phase = str(phase[x])) 
        event.picks.append(picks) 
        event.origins.append(origin)
        origin.arrivals.append(arrival) 
        event.magnitudes.append(magnitude)
    db_catalog.append(event)


#Only include picks for stations used 
all_picks=[]
for event in db_catalog:
    stations = ['KCT', 'KMPB', 'KCR', 'KHMB', 'KCS', 'KCO', 'KMR', 'KPP']                
    event.picks = [pick for pick in event.picks if pick.waveform_id.station_code in stations]
    all_picks+= [(pick.waveform_id.station_code, pick.waveform_id.channel_code) for pick in event.picks]

new_catalog=Catalog()
for event in db_catalog:
    event.picks = [pick for pick in event.picks if (pick.waveform_id.station_code, pick.waveform_id.channel_code) in all_picks]
    new_catalog.append(event)

# count number of picks for each event in catalog
n_picks = [len(event.picks) for event in new_catalog] 

#Save catalog
new_catalog.write("DB_Event_Catalog" + '.xml', "QUAKEML")

# =============================================================================
# ## 2. LOAD CATALOG IF AVAILABLE 
# cat=read_events("DB_Event_Catalog.xml")    
# =============================================================================

## 1. IMPORT WAVEFORMS FOR TEMPLATE 
print("IMPORTING AND PREPROCESSING WAVEFORM STREAMS.")
jday = [event.origins[0].time.julday for event in new_catalog]
yrs = [event.origins[0].time.year for event in new_catalog]
yrjdays = zip(yrs, jday)
    
# Handle directory level stuff
# if dirs already exist ask to overwrite
if os.path.isdir('Template_plots/'):
    inp = input('Templates already exist. Do you want to overwrite? (y/n)...')
    if inp == 'y':
        shutil.rmtree('Template_plots')
        shutil.rmtree('Templates_MSEED')
    if inp == 'n':
        sys.exit('Exiting code -- will not overwrite existing templates')
# make dirs for templates & plots if they don't esist   
if not os.path.isdir(os.getcwd() + '/Template_plots'):
    os.mkdir('Template_plots')
    os.mkdir('Templates_MSEED')
   
template_names = []
for i, (yr, days) in enumerate(zip(yrs, jday)):
    plt.close('all')
    st = Stream()
    print('\nworking on event ' + events_clust[i] + ' with %i picks' % n_picks[i])
    
    #perm NC stations    
    my_file = ('/auto/proj/Cascadia/data_nobackup/NC/KCT/KCT.NC.HHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/NC/KMPB/KMPB.NC.HHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/NC/KCR/KCR.NC.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/NC/KHMB/KHMB.NC.HHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/NC/KCS/KCS.NC.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/NC/KCO/KCO.NC.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/NC/KMR/KMR.NC.HHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/NC/KPP/KPP.NC.HHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
   
    if st.count() > 0: # need waveforms to continue
        std = Stream()
        for tr in st:
            num = tr.stats.npts
            samp = tr.stats.sampling_rate             
            if num >= (samp*86400)*.8:
                std.append(tr)
        
        print('number of good waveforms ', std.count())
        if std.count() < 3: # want 3 or more waveforms for templates
            print('skipping event not enough good waveforms')
            
        else:         
            std.sort(['starttime'])
            std.merge(fill_value="interpolate")
            st1=std.copy()
            
            start = UTCDateTime(year = yr, julday = days)
            end = start + 86400
            st_filter=st1.trim(starttime=start, endtime=end)
        
#            print('GENERATING TEMPLATE FOR ' + str(start) +   ' SAVING AS MINISEED FILES & PLOTS ARE SAVED TO FOLDER.')
            # template matching
            template = template_gen.from_meta_file(meta_file = new_catalog, st = st_filter,
                                                   lowcut = 3, highcut = 10, filt_order = 4, samp_rate = 25,
                                                   prepick = 0.15, length = 4.6, swin = 'P',
                                                   parallel = True)
            
            if len(template[0]) < 3:
                print('Skipping template -- %i picks & %i WF in template' % (n_picks[i], len(template[0])))
                
            else:
    #            stats = trace.Stats()
                template[0].sort(['starttime'])
                timestamp = template[0][0].stats.starttime
                end_template = template[0][0].stats.endtime
                
                # make plots
                stplot = std.copy()
                stplot = stplot.trim(starttime = timestamp - 5, 
                                     endtime= end_template + 5)
#                stplot = stplot.detrend()
#                stplot = stplot.resample(25)
                stplot = stplot.filter('bandpass', freqmin= 3, freqmax = 10, corners = 4, zerophase = True)
                pretty_template_plot(template[0], background = stplot, 
                                     picks = new_catalog[i].picks,
                                     save = True, savefile=os.path.join(os.getcwd() + "/Template_plots", "template_" + str(timestamp) + '-' +  str(events_clust[i]) + ".png"))
                
                template[0].write(os.getcwd() + '/Templates_MSEED/template_' + str(timestamp) + '-'+  str(events_clust[i]) +'.ms', format='MSEED')
                template_names.append('template_' + str(timestamp) + '.ms')
                st.clear()
                std.clear()
                st_filter.clear()
                stplot.clear()
        
print('Script took ', time.time() - init_time, ' s to complete.')