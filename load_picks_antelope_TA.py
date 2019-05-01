#!/opt/antelope/python2.7.8
# have to >>> addpackage antelope 

# T. Alongi 2018-11-12 for cross correlation GrowClust importint cascadia data
# Heather Shaddox, updated 5/24/17
# Edited from G. Barcheck
# the datascope/python docs are at: /opt/antelope/5.6/html/pythondatascope.html
# can type into browser: file:///opt/antelope/5.6/html/pythondatascope.html

import os
import sys

# add the antelope python package to the pythonpath
sys.path.append( os.environ['ANTELOPE'] + '/data/python' )


import antelope.datascope as datascope
from antelope.datascope import dbopen
from antelope.datascope import closing
from antelope.datascope import freeing
import pickle
import csv

os.chdir('/auto/proj/Cascadia/MERGED') #location of the antelope database

database_name='cascadia' #antelope database name

with closing(dbopen(database_name,'r')) as db:

    # open the origin table 
    db_origin_raw=db.lookup(table = 'origin') #has null records (-1)
    db_origin=db_origin_raw.subset('orid > -1') #no longer has null records; should be able to crunch but can't

    # open the event table
    db_event_raw=db.lookup(table = 'event') #has null records
    db_event=db_event_raw.subset('evid > -1') #no longer has null records


    print('fields in db_event are: ' + str(db_event_raw.query(datascope.dbTABLE_FIELDS)))
    print('fields in db_origin are: ' + str(db_origin_raw.query(datascope.dbTABLE_FIELDS)))
    
    #join event and origin
    db_origin_event=db_origin.join(db_event)

    #subset to only events where orid=prefor
    db_subset=db_origin_event.subset('orid==prefor') #will only load pick times of preferred origins

    # find number of events
    n_events=db_subset.query(datascope.dbRECORD_COUNT)  

    print ('there are ' + str(n_events) + ' events picked')
    
    #join with assoc, arrival, site to pull out picks
    db1=db_subset.join('assoc')
    db2=db1.join('arrival')
    dbjoined=db2.join('site')
    db4=dbjoined.join('wfdisc') #Added to get waveform file path later

    out={} 
    ii=-1  

    # for each event picked, make a subset db and pull out station, channel, arrival time, and phase
    # could also pull origin time or other useful info; didn't need for my project
    for rec in db_subset.iter_record(0,n_events,1):    
        tmp_list=[]   
        ii=ii+1
        tmp=rec.getv('orid') #pulls as tuple, one record for 
        orid=tmp[0] #need as int
        #print orid
        dbtmp=db4.subset('prefor == ' + str(orid)) #subset db so only 1 event is pulled
        nrec=dbtmp.query(datascope.dbRECORD_COUNT) #number of arrivals (number of records in the subset db)
        for rec in dbtmp.iter_record(0,nrec,1): #loop through arrival records
            print rec.getv('evid', 'time', 'sta', 'chan','phase','arrival.time', 'lat', 'lon', 'orid', 'depth', 'ml', 'fm')
            tmp_list+=rec.getv('evid', 'time', 'sta', 'chan','phase','arrival.time', 'lat', 'lon', 'orid', 'depth', 'ml', 'fm') # save to a temporary list
        out[ii]=tmp_list  # append the list to the end of a list of all arrivals per event
        # out[event][0], out[event][1], out[event][2], out[event][3] should be all of the info for a single arrival 
        dbtmp.free()
# save as a pickled file; way to transfer between python environments

# dir to save pickle to --TA--
#os.chdir('/auto/proj/Cascadia/scripts/Events')
os.chdir('/auto/home/talongi/Cascadia/Data_tables/Events')

import time
now=time.localtime()

pickle.dump(out,open('all_event_arrivals_' + str(now.tm_mon) + '.' + str(now.tm_mday) + '.' + str(now.tm_year) + '.pkl','wb'))

### to read back in:
#out=pickle.load(open('all_event_arrivals_9.13.2016.pkl','rb')) 















