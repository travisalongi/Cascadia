#!/usr/bin/python
# python 3.7 -- EQcorrscan 0.3.3, T.Alongi adapted from H.Shaddox

import os
import sys
import glob
import csv

from obspy.core import read, UTCDateTime, Stream, Trace
from obspy.core.event import read_events #If this fails, check the version of obspy. It is read_events in newer versions and readEvents in the old versions.
from obspy.core.event import Catalog, Event, Magnitude, Origin, Pick, Arrival, WaveformStreamID, Comment, CreationInfo, ResourceIdentifier
import matplotlib.pyplot as plt

from eqcorrscan.utils import pre_processing, plotting
from eqcorrscan.core import match_filter

t_init = UTCDateTime.now()
plt.ioff() #prevents plots pop ups
# =============================================================================
# ## 1. LOAD PREMADE TEMPLATES
# =============================================================================
os.chdir('/auto/proj/Cascadia/EQcorrscan/CM04Cluster/Run3/Template_gen/Templates_MSEED')
pwd = os.getcwd()

# make list of template names
template_names = []
template_names = [filenames for (dirpath, dirnames, filenames) in os.walk(os.getcwd())][0]

# make list of streams 
templates = []
templates = [read(file) for file in template_names]

os.chdir('/auto/proj/Cascadia/EQcorrscan/CM04Cluster/Run3/Detections/')

if os.path.exists('Detections.csv'):
    inp = input('Over right this data? (y/n)')
    if inp == 'y':
        print('Code will continue to run Detections.csv will be overwritten')
        os.remove('Detections.csv')
    if inp == 'n':    
        sys.exit('Detection data already exists in this location code killed')

# =============================================================================
# ## 2. MAKE DETECTIONS
# =============================================================================
#start = UTCDateTime(2013, 1, 1)
#end = UTCDateTime(2018, 1, 1)
start = UTCDateTime(2016,1,1)
end = UTCDateTime(2016,12,31)

for yr in range(start.year, end.year + 1):
    for jday in range(358,366): #upto 365
        print(yr,jday)
        
        plt.close('all')        
        dt = UTCDateTime(yr, julday = jday)
        st = Stream()
        std = Stream()
        st = read('/auto/proj/Cascadia/PermStatWF/*/*[HE]HZ.%s.%s' % (yr, jday))
            
        for tr in st:
            num = tr.stats.npts
            samp = tr.stats.sampling_rate
            
            if num >= (samp*86400)*.80:
                std.append(tr)
                
        if len(std) > 0: # need wf in stream to cont.
            std.sort(['starttime'])
            std.merge()
            std1=std.copy()
            
            # want full day of waveform - trim to start - end time
            starttime1 = dt            
            if jday == 365: #handles end of year
                endtime1 = UTCDateTime(year = yr + 1, julday = 1, hour = 0, minute = 0)
            else:
                endtime1 = dt + 86400 #1 day
            std1.trim(starttime=starttime1, endtime=endtime1)
            
            #pre-process day waveform data -- needs to be same as processing for templates
            std_filter = pre_processing.dayproc(std1, lowcut=3, highcut=10, filt_order=4, samp_rate=25, 
                                                debug=0, starttime=starttime1,  parallel=True, num_cores=10)
            print("MAKING DETECTIONS.", starttime1)
                 
            #match filtering
            detections = match_filter.match_filter(template_names=template_names, template_list=templates, st=std_filter,
                                                   threshold=10, threshold_type='MAD', trig_int=6.0, 
                                                   plotvar = False, plotdir = '.', cores=10, debug=2)
            
            print("PLOTTING DETECTIONS AND SAVING TO FOLDER.")
#            print(detections)
            
            for detection in detections:
                if detection.detect_val/detection.no_chans >= 0.6 and detection.no_chans >= 3: #Only save and plot detections with avg CC >= 0.6 with min 3 channels 
                    with open('Detections.csv', 'a') as csvfile:
                        detwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        detwriter.writerow([detection.template_name, detection.detect_time, detection.no_chans, detection.detect_val, detection.detect_val/detection.no_chans])
                        csvfile.close()
                        print('We made a total of ' + str(len(detections)) + ' detections')
                        print('Detection at :' + str(detection.detect_time) + ' for template ' + detection.template_name + ' with a cross-correlation sum of: ' + str(detection.detect_val))
                        stplot2 = std_filter.copy()
                        template = templates[template_names.index(detection.template_name)]
                        lags2 = sorted([tr.stats.starttime for tr in template])
                        maxlag2 = lags2[-1] - lags2[0]
                        starttime = detection.detect_time
                        stplot2.trim(starttime=starttime - 10, endtime=starttime + maxlag2 + 10)
                        plotting.detection_multiplot(stplot2, template, [detection.detect_time.datetime], size=[24.0, 11.77], 
    						                 save = True, savefile = os.getcwd() + '/Detection_Plots/Detection_' + str(starttime) + '.png')
                        
            #Clear streams to keep memory usage low 
            std1.clear()
            std_filter.clear()
            std.clear()
            st.clear()
    
        	#Delete automatically generated template*.npy files 
            filelist=glob.glob(os.getcwd() + "/template_*.npy")
            for file in filelist:
                os.remove(file)

print('Script ran for %.1f seconds' % (UTCDateTime.now() - t_init))
