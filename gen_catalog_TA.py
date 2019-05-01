#!/usr/bin/python

from __future__ import print_function
import time
import os, sys, glob
from os import walk, path

import numpy as np
import shutil
import pickle
import obspy
import csv
from obspy.core import read, UTCDateTime, Stream, Trace
from obspy.core.event import read_events 
from obspy.core.event import Catalog, Event, Magnitude, Origin, Pick, Arrival, WaveformStreamID, Comment, CreationInfo, ResourceIdentifier

##CREATE CATALOG FROM ANTELOPE EVENTS 
data_dir = '/auto/home/talongi/Cascadia/Data_tables/Events/'
picklefile = data_dir + 'all_event_arrivals_3.25.2019.pkl'
out=pickle.load(open(picklefile,'rb'))

out_3=[]
for i, events in enumerate(out):
	out_et=out[i][1::12]
	if len(out_et) > 1:
		out_3.append(out[i])
print(out_3)


db_catalog = Catalog()

#Append picks and events from db to Catalog 
for i, events in enumerate(out_3):
	event=Event()	
	picks=Pick()
	origin=Origin()
	arrival=Arrival()
	e_time=out_3[i][1::12]
	sta = out_3[i][2::12]
	cha = out_3[i][3::12]
	phase = out_3[i][4::12]
	pick_time = out_3[i][5::12]
	lat = out_3[i][6::12]
	lon = out_3[i][7::12]
	orid=out_3[i][8::12]
	dep = out_3[i][9::12]
	ml=out_3[i][10::12]
	fm = out_3[i][11::12]
	for x, times in enumerate(pick_time):
		#if str(phase[x]) == 'S':
		event.resource_id=str(out_3[i][0])
		if fm[x] == 'c.':
			pol = "positive"
		elif fm[x] == 'd.':
			pol = "negative"
		else:
			pol = "undecidable"
		rd = str(out_3[i][0])
		picks = Pick(resource_id=rd, time=UTCDateTime(pick_time[x]), waveform_id = WaveformStreamID(network_code="hobitss", station_code=str(sta[x]), channel_code=str(cha[x])), polarity = pol, phase_hint=str(phase[x]))
		origin = Origin(resource_id=(str(orid[x])), time = UTCDateTime(e_time[x]), longitude= str(lon[x]), latitude=str(lat[x]), depth=str(dep[x]))
		magnitude = Magnitude(mag = ml[x], magnitude_type = "M", origin_id = (str(orid[x]))) 
		arrival = Arrival(pick_id = rd, phase = str(phase[x])) 
		event.picks.append(picks) 
		event.origins.append(origin)
		origin.arrivals.append(arrival) 
		event.magnitudes.append(magnitude)
	db_catalog.append(event)

db_catalog.write("ant_MERGED3" + '.xml', "QUAKEML")

print(db_catalog)

for event in db_catalog:
	location = open('ant_MERGE3.txt', 'a')
	event.origins = [origin for origin in event.origins]
	evid_char = str(event.resource_id)
	if evid_char[0:10] == "smi:local/":
		evid_char_old = evid_char
                nevidchars = len(evid_char)
                evid_char = evid_char[10:nevidchars]
        location.write(evid_char)
        location.write(" ")
        location.write(str(origin.time))
        location.write(" ")
        location.write(str(origin.latitude))
        location.write(" ")
        location.write(str(origin.longitude))
        location.write(" ")
        location.write(str(origin.depth))
        location.write(" ")
        location.write(str(event.magnitudes[1].mag)+ '\n')
	location.close()


