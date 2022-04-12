#Get the relevant TCs trajectories from the original IBTrACS dataset

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf

#Making pathway to folder with all data
directory 		= '../../Data/IBTrACS/'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------	

year_start	= 1993
year_end	= 2017

#-----------------------------------------------------------------------------------------	
fh = netcdf.Dataset(directory+'IBTrACS.since1980.v04r00.nc', 'r')

number	= fh.variables['number'][:]
lon		= fh.variables['lon'][:]
lat		= fh.variables['lat'][:]
time	= fh.variables['iso_time'][:]
wind	= fh.variables['wmo_wind'][:] * 0.5144444444	#Convert to m/s
agency	= fh.variables['wmo_agency'][:]
nature	= fh.variables['nature'][:]

fh.close()

#-----------------------------------------------------------------------------------------	
#-----------------------------------------------------------------------------------------	

counter	= 0

for storm_i in range(len(number)):
	#Loop over each storm
	year_genesis	= int(time[storm_i, 0, 0] + time[storm_i, 0, 1] + time[storm_i, 0, 2] + time[storm_i, 0, 3])

	if year_genesis < year_start or year_genesis > year_end:
		continue

	#Get the current track information
	time_storm		= time[storm_i]
	lon_storm		= lon[storm_i]
	lat_storm		= lat[storm_i]
	wind_storm		= wind[storm_i]
	nature_storm	= nature[storm_i]
	agency_storm	= agency[storm_i]

	#Mask index where there is no velocity input
	index		= np.where(wind_storm.mask == False)[0]
	if len(index) == 0: 
		continue

	#Get only the relevant points
	time_storm		= time_storm[index]
	lon_storm		= lon_storm[index]
	lat_storm		= lat_storm[index]
	wind_storm		= wind_storm[index]
	nature_storm	= nature_storm[index]
	agency_storm	= agency_storm[index]

	#Set the correct toordinal time form
	time_storm_2	= np.zeros(len(time_storm))
	
	for time_i in range(len(time_storm)):
		#Read in the time stamp
		year_storm		= int(time_storm[time_i, 0] + time_storm[time_i, 1] + time_storm[time_i, 2] + time_storm[time_i, 3])
		month_storm		= int(time_storm[time_i, 5] + time_storm[time_i, 6])
		day_storm		= int(time_storm[time_i, 8] + time_storm[time_i, 9])
		hour_storm		= int(time_storm[time_i, 11] + time_storm[time_i, 12])
		minute_storm	= int(time_storm[time_i, 14] + time_storm[time_i, 15])
		second_storm	= int(time_storm[time_i, 17] + time_storm[time_i, 18])

		#Save in toordinal form
		time_storm_2[time_i]	= datetime.datetime(year_storm, month_storm, day_storm).toordinal() + (hour_storm / 24.0) + (minute_storm / (24 * 60)) + (second_storm / (24 * 3660))

	#Get agency for each measurement
	for time_i in range(len(time_storm)):	
		index		= np.where(agency_storm[time_i].mask == False)[0]
		agency_time	= ''
		
		for i in range(len(index)): 
			agency_time += agency_storm[time_i, index[i]].decode('utf-8')
		
		if agency_time == 'hurdat_atl' or agency_time == 'hurdat_epa' or agency_time == 'atcf' or agency_time == 'cphc' or agency_time == 'newdelhi':
			#Is already in 1-minute maximum sustained wind speed
			pass

		elif agency_time == 'wellington' or agency_time == 'nadi' or agency_time == 'tokyo' or agency_time == 'bom' or agency_time == 'reunion':
			#Convert 10-minute U10 wind speed to 1-minute
			wind_storm[time_i]	= wind_storm[time_i] * (1 / 0.91)

		else:
			print('Undefined agency')
			sys.exit()

	time_index	= []
	for time_i in range(len(lon_storm)):
		#Check when storm develops into TS
		system		= nature_storm[time_i, 0].decode('utf-8') + nature_storm[time_i, 1].decode('utf-8')

		if len(time_index) == 0:
			#Start tracking after first Tropical Storm classification
			if system == 'TS':
				time_index.append(time_i)

		else:
			if system == 'ET':
				#System develops into extratropical dismiss remaining part
				break
			
			#Get the corresponding indices
			time_index.append(time_i)

	if len(time_index) < 2:
		#No data or only 1 data point
		continue

	#Retain the corresponding TC indices
	time_storm	= time_storm_2[time_index]
	lon_storm	= lon_storm[time_index]
	lat_storm	= lat_storm[time_index]
	wind_storm	= wind_storm[time_index]

	#Check whether longitude has negative values, set to 0 - 360E
	lon_storm[lon_storm < 0] = lon_storm[lon_storm < 0] + 360

	#Save the track data
	data_track	= ma.masked_all((len(time_storm), 4))
	data_track[:, 0]= time_storm
	data_track[:, 1]= lon_storm
	data_track[:, 2]= lat_storm
	data_track[:, 3]= wind_storm

	#Initiate new track
	exec('TRACK_ID_'+str(counter)+' = data_track')
	counter		+= 1

#-----------------------------------------------------------------------------------------

#Determine the maximum track time
time_max	= 0

for track_i in range(counter):

	exec('track = TRACK_ID_'+str(track_i))

	if len(track) > time_max:
		#Update maximum time
		time_max	= len(track)

#-----------------------------------------------------------------------------------------

#Raise time max by 1 (easy to remove masked objects for post-processing)
time_max	+= 1

track_all	= ma.masked_all((counter, time_max, 4))

for track_i in range(counter):
	#Save data to general array
	exec('track = TRACK_ID_'+str(track_i))
	track_all[track_i, :len(track)]	= track

#-----------------------------------------------------------------------------------------
#Save the coordinates for each track
fh = netcdf.Dataset(directory+'IBTrACS_TC_tracks_year_'+str(year_start)+'-'+str(year_end)+'.nc', 'w')

fh.createDimension('track_number', len(track_all))
fh.createDimension('time', time_max)
fh.createDimension('data', 4)

fh.createVariable('track_number', float, ('track_number'), zlib=True)
fh.createVariable('time', float, ('time'), zlib=True)
fh.createVariable('data', float, ('data'), zlib=True)
fh.createVariable('TC_tracks', float, ('track_number', 'time', 'data'), zlib=True)

fh.variables['track_number'].longname 	= 'Track number'
fh.variables['time'].longname 			= 'Lifetime TC'
fh.variables['data'].longname 			= 'Time, lon (RV), lat (RV), Wind speed (1-min)'

#Writing data to correct variable	
fh.variables['track_number'][:] 	= np.arange(len(track_all)) + 1
fh.variables['time'][:] 			= np.arange(time_max)
fh.variables['data'][:] 			= np.arange(4)
fh.variables['TC_tracks'][:] 		= track_all


