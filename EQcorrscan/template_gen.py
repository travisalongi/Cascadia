#!/usr/bin/python

from __future__ import print_function
import time
import os, sys, glob

import string
import numpy as np
import shutil
import pickle
import obspy

from obspy.core import read, UTCDateTime, Stream, Trace, trace
from obspy.core.event import read_events 
from obspy.signal.filter import bandpass
from obspy.core.event import Catalog, Event, Magnitude, Origin, Pick, Arrival, WaveformStreamID, Comment, CreationInfo, ResourceIdentifier

#sys.path.append('/home/hshaddox/EQcorrscan/EQcorrscan-0.1.6/eqcorrscan/utils')

from multiprocessing import cpu_count
from eqcorrscan.utils import pre_processing, catalog_utils
from eqcorrscan.utils import plotting
from datetime import datetime, date
from eqcorrscan.utils.plotting import pretty_template_plot
import matplotlib.pyplot as plt
from collections import Counter
from eqcorrscan.core import template_gen, match_filter, lag_calc


## 1. CREATE A CATALOG OF EVENTS ON DAY OF INTEREST FROM ANTELOPE DATABASE 

print("CREATING DATABASE EVENT CATALOG") 

#Create list of event IDs to be used as templates. Will use to loop through all events later and select only cluster events. 
events_clust = [1191, 1287, 1812, 1328, 1428, 1429, 1390, 1190, 1307, 1289, 
                1365, 1366, 1367, 1186, 1185, 1163, 1153, 1152, 1151] #original NC_events used
# assign events to list
events_clust = []
with open("/auto/proj/Cascadia/EQcorrscan/CM04Cluster/evid_greatest_M.txt") as file: #with statement auto closes txtfile
    for line in file:
        line = line.strip() 
        events_clust.append(line)

##CREATE CATALOG FROM UCSC ANTELOPE EVENTS 
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



#Only include picks for stations used -- omitting CM09 because noisy
all_picks=[]
for event in db_catalog:
    stations = ["CM01A", "CM02A", "CM03A", "CM04A", "CMO5A", "CM06A", "CM07A", "CM08A"]
    event.picks = [pick for pick in event.picks if pick.waveform_id.station_code in stations]
    all_picks+= [(pick.waveform_id.station_code, pick.waveform_id.channel_code) for pick in event.picks]

new_catalog=Catalog()
for event in db_catalog:
    event.picks = [pick for pick in event.picks if (pick.waveform_id.station_code, pick.waveform_id.channel_code) in all_picks]
    new_catalog.append(event)

#Save catalog
new_catalog.write("DB_Event_Catalog" + '.xml', "QUAKEML")
    #db_catalog = catalog_utils.filter_picks(db_catalog, top_n_picks=7)

#new_catalog.plot(projection="local", water_fill_color="lightblue", label = None, color="date", title=("Templates"))

## 2. LOAD CATALOG IF AVAILABLE 
#cat=read_events("DB_Event_Catalog.xml")    


## 1. IMPORT WAVEFORMS FOR TEMPLATE 
print("IMPORTING AND PREPROCESSING WAVEFORM STREAMS.")

jday = []
for event in new_catalog:
    ot = event.origins[0].time
    j = str(ot.julday)
    jday.append(j)


template_names=[]
for i, days in enumerate(jday):
    ot = new_catalog[i].origins[0].time
    yr = (ot.year)
    print(yr, days)
    st = Stream()
    my_file = ('/auto/proj/Cascadia/data_nobackup/5E/CM01A/CM01A.5E.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/5E/CM02A/CM02A.5E.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/5E/CM03A/CM03A.5E.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/5E/CM04A/CM04A.5E.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/5E/CM05A/CM05A.5E.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/5E/CM06A/CM06A.5E.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/5E/CM07A/CM07A.5E.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    my_file = ('/auto/proj/Cascadia/data_nobackup/5E/CM08A/CM08A.5E.EHZ.%s.%s' % (yr, days))
    if os.path.isfile(my_file):
        st += read(my_file)
    
    if st.count() > 0:
        std = Stream()
        for tr in st:
            num = tr.stats.npts
            sta = tr.stats.station
            samp = tr.stats.sampling_rate 
            
            if num >= (samp*86400)*.8:
                std.append(tr)
                
        std.sort(['starttime'])
        std.merge(fill_value="interpolate")
        print(st)
        st1=std.copy()
        mon = ot.month
        day = ot.day
        start = UTCDateTime(yr, mon, day, 0, 0, 0)
        end = start + 86400
        st_filter=st1.trim(starttime=start, endtime=end)
        
        print("GENERATING TEMPLATES AND SAVING AS MINISEED FILES. PLOTS ARE SAVED TO FOLDER.")
        template = template_gen.from_meta_file(meta_file = new_catalog, st = st_filter,
                                               lowcut = 3, highcut = 10, filt_order = 4, samp_rate = 25,
                                               prepick = 0.15, length = 4.5, swin = 'P')
        
        stats = trace.Stats()
        timestamp = template[0][0].stats.starttime
        end_template = template[0][0].stats.endtime
        
        # make plots
        stplot = st_filter.copy()
        stplot = stplot.trim(starttime = timestamp - 5, 
                             endtime= end_template + 5)
        stplot = stplot.filter('bandpass', freqmin= 3, freqmax = 10)
        pretty_template_plot(template[0], background = stplot, 
                             save = True, savefile=os.path.join(os.getcwd() + "/Template_plots", "template_" + str(timestamp) + ".png"))
        
        template[0].write(os.getcwd() + '/Templates_MSEED/template_' + str(timestamp) + '.ms', format='MSEED')
        template_names.append('template_' + str(timestamp) + '.ms')
        st.clear()



