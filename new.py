# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 09:57:14 2022

@author: Gijsbert
all data from PVLIB is in Watt!

Assumptions:
    - All energy demand is for electricity use (no heat of cooling) because these are from geothermal
    - Electricity demand is taken from Evert Vrins and equally divided for all hours in the year
"""
import pvlib
import pandas as pd

#define location (Tilburg Wijkevoort)
latitude =  51.553866393756785
longitude = 4.9621837164611415

# define PV parameters
peakpower_east = 13000   #installed PV capacity in Kwpeak [kWp]
peakpower_west = 13000   #installed PV capacity in Kwpeak [kWp]
TotalPV_losses = 10      # percentage
annual_E_demand = 19368889 # kwh

# Get TMY data from PVGIS
data = pvlib.iotools.get_pvgis_tmy(latitude, longitude, outputformat='json', 
                                 usehorizon=True, userhorizon=None, startyear=2005,
                                 endyear=2016, url='https://re.jrc.ec.europa.eu/api/',
                                  timeout=30)
# get PV potential data 
PV_gen_east = pvlib.iotools.get_pvgis_hourly(latitude, longitude,
                                       start=2005, end=2016,
                                       raddatabase=None, components=True, 
                                       surface_tilt=30, surface_azimuth=-90,
                                       outputformat='json', usehorizon=True,
                                       userhorizon=None, pvcalculation=True,
                                       peakpower=peakpower_east, pvtechchoice='crystSi',
                                       mountingplace='free', loss=TotalPV_losses, trackingtype=0,
                                       optimal_surface_tilt=False, optimalangles=False, 
                                       url='https://re.jrc.ec.europa.eu/api/', map_variables=True, 
                                       timeout=30)
df2 = PV_gen_east[0] 
df2.index = pd.to_datetime(df2.index).tz_localize(None)
df2.index = df2.index - pd.Timedelta(minutes=10) # make datetime index of hourly the same as TMY

PV_gen_west = pvlib.iotools.get_pvgis_hourly(latitude, longitude,
                                       start=2005, end=2016,
                                       raddatabase=None, components=True, 
                                       surface_tilt=30, surface_azimuth=90,
                                       outputformat='json', usehorizon=True,
                                       userhorizon=None, pvcalculation=True,
                                       peakpower=peakpower_west, pvtechchoice='crystSi',
                                       mountingplace='free', loss=TotalPV_losses, trackingtype=0,
                                       optimal_surface_tilt=False, optimalangles=False, 
                                       url='https://re.jrc.ec.europa.eu/api/', map_variables=True, 
                                       timeout=30)
df3 = PV_gen_west[0] 
df3.index = pd.to_datetime(df3.index).tz_localize(None)
df3.index = df3.index - pd.Timedelta(minutes=10) # make datetime index of hourly the same as TMY

# merge dataframes
data[0].index = pd.to_datetime(data[0].index)
tmy = data[0]
tmy.index = tmy.index.tz_localize(None)
df2=df2.rename(columns = {'P':'P_east'})
df3=df3.rename(columns = {'P':'P_west'})
merge = pd.merge(tmy, df2, left_index=True, right_index=True)
merge = pd.merge(merge, df3['P_west'], left_index=True, right_index=True)

merge['E_demand'] = (annual_E_demand/8760)*1e3        #Watt
TotPVproduction = (merge['P_west']+merge['P_east']).sum()/1e3 #KWh
PV_surplus = TotPVproduction-annual_E_demand # kwh

#%%
merge['DeltaP'] = (merge['P_east']+merge['P_west'])-merge['E_demand'] 
# check to see if annually the PV exceeds the E demand
print(merge['DeltaP'].sum()/1e3) # should be the same as 'PV_surplus' = TRUE  in kwh

Storage_no_wind = merge['DeltaP']

#%% storage needed when wind energy is applied
amount_of_turbines = 500 # powernest eqivalent  one powernest = 3kw peak

merge['Pwind'] = (3/10*merge['WS10m']-0.6)*1000*amount_of_turbines #watt
merge['Pwind'][merge['Pwind']<0] = 0

merge['DeltaP_wind'] = (merge['P_east']+merge['P_west']+merge['Pwind'])-merge['E_demand']
Storage_with_wind = merge['DeltaP_wind']


#%%
summerweek_start = '2011-09-10 00:00'
summerweek_end = '2011-09-18 23:00'

winterweek_start = '2014-12-10 00:00'
winterweek_end = '2014-12-18 23:00'

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.figure(1)
plt.plot(Storage_no_wind.sort_index().truncate(before = summerweek_start,after = summerweek_end)/1e3)
formatter = mdates.DateFormatter('%d-%m')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xticks(rotation = 45)
plt.ylim(-2500,10000)
plt.xlabel('Dates')
plt.ylabel('Delta P [kW]')
plt.title('Storage needed summerweek without wind energy')
plt.savefig('DP_summer.eps')


plt.figure(2)
plt.plot(Storage_with_wind.sort_index().truncate(before = summerweek_start,after = summerweek_end)/1e3)
formatter = mdates.DateFormatter('%d-%m')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xticks(rotation = 45)
plt.ylim(-2500,10000)
plt.xlabel('Dates')
plt.ylabel('Delta P [kW]')
plt.title('Storage needed summerweek with wind energy')
plt.savefig('DP_summer_wind.eps')



plt.figure(3)
plt.plot(Storage_no_wind.sort_index().truncate(before = winterweek_start,after = winterweek_end)/1e3)
formatter = mdates.DateFormatter('%d-%m')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xticks(rotation = 45)
plt.ylim(-2500,2800)
plt.xlabel('Dates')
plt.ylabel('Delta P [kW]')
plt.title('Storage needed winterweek without wind energy')
plt.savefig('DP_winter.eps')


plt.figure(4)
plt.plot(Storage_with_wind.sort_index().truncate(before = winterweek_start,after = winterweek_end)/1e3)
formatter = mdates.DateFormatter('%d-%m')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xticks(rotation = 45)
plt.ylim(-2500,2800)
plt.xlabel('Dates')
plt.ylabel('Delta P [kW]')
plt.title('Storage needed winterweek with wind energy')
plt.savefig('DP_winter_wind.eps')

#%%

print((Storage_no_wind.sort_index().truncate(before = winterweek_start,after = winterweek_end)/1e3).sum())
print((Storage_with_wind.sort_index().truncate(before = winterweek_start,after = winterweek_end)/1e3).sum())


x = (Storage_with_wind.sort_index().truncate(before = winterweek_start,after = winterweek_end)/1e3).index
y = (Storage_with_wind.sort_index().truncate(before = winterweek_start,after = winterweek_end)/1e3)
plt.figure(4)

plt.fill_between(x, 0, y,color='g', where=(y > 0))
plt.fill_between(x, 0, y,color='orange',where=(y<=0))
formatter = mdates.DateFormatter('%d-%m')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xticks(rotation = 45)
plt.ylim(-2500,2800)
plt.xlabel('Dates')
plt.ylabel('Delta P [kW]')
plt.title('Storage needed winterweek with wind energy')

 

#%% EMS 1
StorageSize = 100000000 #Wh
merge.at[merge.index[0],'Bat']=0
merge['Grid']=0

for x in range(1,len(merge.index)):
    if merge.at[merge.index[x],'DeltaP'] > 0: 
        merge.at[merge.index[x],'Bat'] = merge.at[merge.index[x-1],'Bat'] + merge.at[merge.index[x],'DeltaP']
        if  merge.at[merge.index[x],'Bat'] > StorageSize:
            merge.at[merge.index[x],'Bat'] = StorageSize
    else:
        merge.at[merge.index[x],'Bat'] = merge.at[merge.index[x-1],'Bat'] + merge.at[merge.index[x],'DeltaP']
        if merge.at[merge.index[x],'Bat'] < 0:
            merge.at[merge.index[x],'Grid'] = -1*merge.at[merge.index[x],'Bat']
            merge.at[merge.index[x],'Bat'] = 0
            
#%% EMS 2
treshold = 0.5*(peakpower_east + peakpower_west)

#for x in range(1,len(merge.index)):
#    if merge.at[merge.index[x],'DeltaP'] > 0:
#        merge.at[merge.index[x],'Bat'] = merge.at[merge.index[x-1],'Bat'] + merge.at[merge.index[x],'DeltaP']
#        if  merge.at[merge.index[x],'Bat'] > StorageSize:
#            merge.at[merge.index[x],'Bat'] = StorageSize
#    elif merge.at[merge.index[x],'E_demand'] - (merge.at[merge.index[x],'P_east'] + merge.at[merge.index[x],'P_west']) < treshold:
#        merge.at[merge.index[x],'Bat'] = merge.at[merge.index[x-1],'Bat'] + merge.at[merge.index[x],'DeltaP']
#        if  merge.at[merge.index[x],'Bat'] > StorageSize:
#            merge.at[merge.index[x],'Bat'] = StorageSize
#    else:
#        merge.at[merge.index[x],'Bat'] = merge.at[merge.index[x-1],'Bat'] + merge.at[merge.index[x],'DeltaP']
#        if merge.at[merge.index[x],'Bat'] < 0:
#            merge.at[merge.index[x],'Grid'] = -1*merge.at[merge.index[x],'Bat']
#            merge.at[merge.index[x],'Bat'] = 0

#%%   
plt.figure(5)
plt.plot(merge['Bat'].sort_index().truncate(before = winterweek_start,after = winterweek_end)/1e3)
formatter = mdates.DateFormatter('%d-%m-%y')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xticks(rotation = 45)
plt.xlabel('Dates')
plt.ylabel('Battery storage [kWh]')
plt.title('Typical winterweek stored energy')    
plt.savefig('St_winter.eps')

plt.figure(6)
plt.plot(merge['Bat'].sort_index().truncate(before = summerweek_start,after = summerweek_end)/1e3)
formatter = mdates.DateFormatter('%d-%m-%y')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xticks(rotation = 45)
plt.xlabel('Dates')
plt.ylabel('Battery storage [kWh]')
plt.title('Typical summer week stored energy')  
plt.savefig('St_summer.eps') 

plt.figure(7)
plt.plot(merge['Grid'].sort_index().truncate(before = winterweek_start,after = winterweek_end)/1e3)
formatter = mdates.DateFormatter('%d-%m-%y')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xticks(rotation = 45)
plt.xlabel('Dates')
plt.ylabel('Grid [kWh]')
plt.title('Typical winterweek grid delivery')    
plt.savefig('Gr_winter.eps')

plt.figure(8)
plt.plot(merge['Grid'].sort_index().truncate(before = summerweek_start,after = summerweek_end)/1e3)
formatter = mdates.DateFormatter('%d-%m-%y')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xticks(rotation = 45)
plt.xlabel('Dates')
plt.ylabel('Grid [kWh]')
plt.title('Typical summerweek grid delivery')    
plt.savefig('Gr_sumer.eps')

