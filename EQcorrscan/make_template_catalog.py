"""
Make catalog of template events
t.alongi 2019/9/25
"""
import pandas as pd
import os
import os.path

# get event id's to match
temp_list = os.listdir('/auto/proj/Cascadia/EQcorrscan/Plate_interface/Run2/Template_gen/Template_plots')
temp_evid_list = [int(evid.split('-')[-1].split('.')[0]) for evid in temp_list]

# dataframe of catalog
cat_file = '/auto/home/talongi/Cascadia/Data_tables/Events/growclust_cat_run4.txt'
hdr_names = ['yr','mon','day','hr','min','sec',
             'eID', 
             'latR','lonR','depR',
             'mag', 
             'qID','cID','nbranch',
             'qnpair', 'qndiffP', 'qndiffS',
             'rmsP', 'rmsS',
             'eh', 'ez', 'et',
             'latC', 'lonC', 'depC'] 
df = pd.read_csv(cat_file, sep = '\s+', names = hdr_names)

df_temp = pd.DataFrame(columns = hdr_names) # new dataframe for templates
for ev in temp_evid_list:
    catalog_event = df[df.eID == ev]
    df_temp = df_temp.append(catalog_event)
    
df_temp.to_csv('template_catalog.txt', sep = ' ', index = False, header = False)

    
    

