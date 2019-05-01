#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 15:17:33 2018
Want  to change origin time of event from antelope 
origin time to simulPS origin time for sac files 
Filters waveforms 3-10hz and trim.
@author: talongi
"""
import time
tic = time.time()

import glob
import os
from astropy.io import ascii
import numpy as np
import obspy

# =============================================================================
# read data assign variables
# =============================================================================
eventfile = '/auto/home/talongi/Cascadia/Data_tables/Events/evlist_from_simPS_merge3.txt'
d = ascii.read(eventfile)

evid = d['col1']
yr = (d['YEAR'])
mo = (d['MO'])
dy = (d['DY'])
hr = d['HR']
mn = d['MN'] 
sec = d['Sec']
# =============================================================================
   
# sac dir with events in dir by evid - change for each run
os.chdir("/auto/proj/Cascadia/GrowClust/Run4/xcorr/Filtered3")
pwd = os.getcwd()

# use inside of loop to find evid and folder matches 
# dir must have only numeric folders to work
lstdir = os.listdir(pwd) #dir names (evids) as list
ls_arr = np.asarray(lstdir, dtype=int) #make list into array as integers for speed

#for loop stats
picks_adjusted = 0
N_events_adjusted = 0
count = 0
N_events_removed = 0
N_deleted_wf = 0
for id in evid:
    
    # set up date
    yr_in = int(yr[count])
    mo_in = int(mo[count])
    dy_in = int(dy[count])    
    hr_in = int(hr[count])
    mn_in = int(mn[count])
    # special formating for obspy UTCDateTime
    sec_in = float(sec[count])
  
    b = math.modf(sec_in) # splits into # and decimal
    b_sec = int(b[1])
    b_micro_sec = int(b[0] * 1e6) # must convert to microsec

       
    if sum(id == ls_arr) > 0:       
        # change directory to match 
        os.chdir(pwd + '/' +str(id))
        workdir = os.getcwd()
        
        # get list of sacfiles in dir
        list_sacfiles = glob.glob('*.SAC')
        
        # get date/time into obspy format
        dtUTC = obspy.UTCDateTime(yr_in,mo_in,dy_in,hr_in,mn_in,b_sec,b_micro_sec)
            
               
        # loop through each sac file to change reference time
        for file in list_sacfiles:
            # import header to change otime
            sacfile = obspy.io.sac.SACTrace.read(file, headonly=True) 
            sacfile.lovrok = True # allows changes to be made (probably not necessary)
            
            # remove sacfiles without orig time o p picks
            if sacfile.o == None or sacfile.a == None:
                os.remove(file)
                N_deleted_wf += 1
                continue
            
            # remove sacfile with time errors - stops program
            strt_tm = dtUTC - 1; #1 sec before origin time
            end_tm = dtUTC + sacfile.a + 10; #10 sec after p pick
            if strt_tm > end_tm:
                os.remove(file)
                N_events_removed += 1
                break               
            if sacfile.nzmsec == 1000: #msec = 1000 cause error in reftime
                os.remove(file)
                N_events_removed
                break

            
            else:
                # change header of sacfile                
                sacfile.o = dtUTC #change origin time to simPS origin time
                sacfile.iztype = 'io' #reference time =  event origin time
                sacfile.reftime = dtUTC #change reference time to simPs time
                #remove any duplicate deleted picks. 
                sacfile.t1 = None 
                sacfile.t2 = None
                sacfile.t3 = None
                
                # flag any problematic files - stops program
                if sacfile.iztype != 'io':
                    print(' ---- iztype problem ---- iztype not io ')
                    break           
                if sacfile.a <= 0:
                    print('P timing error')
                    break
                
                sacfile.write(file, headonly = True)                
                
                # == filter & trim waveform ===
                # import waveform for filtering
                sac_wf = obspy.read(file)
                
                # trim waveform
                sac_wf = sac_wf.slice(starttime = strt_tm, endtime = end_tm)
                
                # filter the trace
                wf_filtered = sac_wf.filter('bandpass', freqmin = 3, freqmax = 10)    
                wf_filtered.write(file, format = 'SAC')
            
                picks_adjusted += 1                          
        N_events_adjusted += 1            
    count += 1

print('Finished running script')
print('')
print('Number of Events Adjusted =', N_events_adjusted)
print('Number of Events Removed =', N_deleted_wf)
print('Number of Picks adjusted = ', picks_adjusted)

toc = time.time()
print('Run time =', toc - tic)

   
#%%

