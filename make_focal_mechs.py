"""
Use dictionarys to plot first arrivals on stereoenets
by, talongi
2019-04-30
"""

import matplotlib.pyplot as plt
import numpy as np
import mplstereonet
from matplotlib.pyplot import cm
plt.close('all')

"""convert az & toa to trend & plunge"""
evid7174 = {'az': np.array([19, 109,237,243,196,150]),
            'toa': np.array([145, 155, 151, 124, 136, 90]),
            'pol': np.array([0,0,1,1,1,0])} #down = 0; up = 1

evid1319 = {'az': np.array([39,88,239,203,199,182]),
            'toa' : np.array([125,140,140,94,89,122]),
            'pol' : np.array([0,0,1,0,0,1])}

#evid1149 = {'az' : np.array([33,320,84,234,245,224,177,223,216,151,84,187]),
#            'toa' : np.array([124,144,142,175,137,125,139,110,93,72,83,122]),
#            'pol' : np.array([0,0,0,0,1,1,1,1,1,1,1,1])}

evid2139 = {'az' : np.array([32,85,232,245,206]),
            'toa' : np.array([125,143,174,137,94]),
            'pol' : np.array([0,0,1,1,0])}

evid6655 = {'az' : np.array([38,81,140]),
            'toa' : np.array([119,134,83]),
            'pol' : np.array([0,0,0])}

evid2031 = {'az' : np.array([36,85,191,243,221,214,204]),
            'toa' : np.array([125,141,177,140,127,95,100]),
            'pol' : np.array([0,0,0,1,1,0,0])}

evid7127 = {'az' : np.array([36,321,87,202,242,221,205]),
            'toa' : np.array([124,145,140,175,137,124,92]),
            'pol' : np.array([0,0,0,1,1,1,0])}

evid6761 = {'az' : np.array([337,268,222,211,206]),
            'toa' : np.array([164,130,92,93,87]),
            'pol' : np.array([1,1,0,0,0])}

evid1129 = {'az' : np.array([125, 96, 238, 84, 182, 187]),
            'toa' : np.array([107,89,112,81,124,89]),
            'pol' : np.array([1,1,1,1,1,0])}

evid1155 = {'az' : np.array([125,238,84,183]),
            'toa' : np.array([107,111,80,123]),
            'pol' : np.array([1,1,1,1])}

evid1236 = {'az' : np.array([200,235,85,183,142]),
            'toa' : np.array([83,103,77,114,80]),
            'pol' : np.array([1,1,1,1,0])}

evids = {7174 : evid7174, 
         1319 : evid1319,
#         1149 : evid1149, #omit inconsistent with other events
         2139 : evid2139,
         6655 : evid6655,
         2031 : evid2031,
         7127 : evid7127,
         6761 : evid6761,
         1129 : evid1129,
         1155 : evid1155,
         1236 : evid1236}

# do correction for azimuth and take off angle to trend and plunge for stereonet
for k in evids.keys():
    trend = []
    plunge = []
    evnt = evids[k]
    
    if len(evnt['toa']) != len(evnt['az']):
        break
    
    for i in np.arange(len(evnt['toa'])):
        if evnt['toa'][i] >= 90:
            if evnt['az'][i] <= 180:
                trend.append(evnt['az'][i] + 180)
                plunge.append(evnt['toa'][i] - 90)
            else:
                trend.append(evnt['az'][i] - 180)
                plunge.append(evnt['toa'][i] - 90)
        else:
            trend.append(evnt['az'][i])
            plunge.append(90 - evnt['toa'][i])
            
        evnt['trend'] = np.asarray(trend)
        evnt['plunge'] = np.asarray(plunge)
        
# make plot of all events
fig = plt.figure(99, figsize=(18,10))
ax = fig.add_subplot(111, projection = 'stereonet')
color = iter(cm.rainbow(np.linspace(0,1, len(evids.keys()))))

for k in evids.keys():
    ev = evids[k]
    c = next(color)
    c = 'k'
    # plot up arrivals
    ax.line(ev['plunge'][ev['pol'] == 1], 
            ev['trend'][ev['pol'] == 1], 
            c = c, label = k)
    
    # plot down arrivals
    ax.line(ev['plunge'][ev['pol'] == 0], 
            ev['trend'][ev['pol'] == 0], 
            c = c, label = k,
            fillstyle = 'none')
    ax.set_title('Composite Mechanism \n Using %d Events' % len(evids.keys()),
                 fontsize = 18, loc = 'left')
ax.grid()

       
 # make individual plots
color = iter(cm.rainbow(np.linspace(0,1, len(evids.keys()))))
for k in evids.keys():
    fig = plt.figure(k,figsize=(18,10))
    ax = fig.add_subplot(111, projection = 'stereonet')
    
    ev = evids[k]
#    c = next(color)
    c = 'k'
    ax.line(ev['plunge'][ev['pol'] == 1], 
            ev['trend'][ev['pol'] == 1], 
            c = c, label = k)
    
    ax.line(ev['plunge'][ev['pol'] == 0], 
            ev['trend'][ev['pol'] == 0], 
            c = c, label = k,
            fillstyle = 'none')

    title_string = 'Event ID = ' + str(k)
    ax.set_title(title_string, fontsize = 18, loc = 'left')
    ax.grid()

   