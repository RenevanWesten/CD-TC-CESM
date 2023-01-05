#Program plots the density of the TC tracks

from pylab import *
import numpy
import datetime
import time
import glob, os
import netCDF4 as netcdf
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap

#Making pathway to folder with all data
directory_cesm	    = '../../../Data/UH-CESM'
directory_ibtracs	= '../../../Data/IBTrACS/'

font = {'size'   : 16}
matplotlib.rc('font', **font)

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------	

grid_size	= 5.0
lon_start	= 0
lon_end		= 360.0
lat_start	= -70
lat_end		= 70

year_start	= 1993
year_end	= 2017


#Generate the lon/lat points for the tracks
lon				= np.arange(lon_start - grid_size / 2.0, lon_end + grid_size / 2.0 + 0.01, grid_size)
lat				= np.arange(lat_start - grid_size / 2.0, lat_end + grid_size / 2.0 + 0.01, grid_size)
field_present	= np.zeros((len(lat), len(lon)))
field_future	= np.zeros((len(lat), len(lon)))
field_obs		= np.zeros((len(lat), len(lon)))

track_cesm_present_total 	= 0
track_cesm_future_total 	= 0
#-----------------------------------------------------------------------------------------

for ensemble_i in [1, 2, 3, 4, 5]:
	#Get the present-day ensemble
	fh = netcdf.Dataset(directory_cesm+'_'+str(ensemble_i).zfill(3)+'/Atmosphere/TC_tracker.nc', 'r')

	#Writing data to correct variable	
	track_all	= fh.variables['TC_tracks'][:]

	fh.close()

	for track_i in range(len(track_all)):
		#Loop over each track
		TC_field	= np.zeros((len(lat), len(lon)))
		track		= track_all[track_i]
		lon_track	= track[:, 1]
		lat_track	= track[:, 2]

		#Remove masked elements
		mask_index	= np.where(lon_track.mask == True)[0][0]
		lon_track	= lon_track[:mask_index]
		lat_track	= lat_track[:mask_index]

		for time_i in range(len(lon_track)):
			#Determine the index
			lon_index	= (np.fabs(lon - lon_track[time_i])).argmin()
			lat_index	= (np.fabs(lat - lat_track[time_i])).argmin()

			if TC_field[lat_index, lon_index] == 0:
				#Only count each grid cell once per TC
				TC_field[lat_index, lon_index] += 1.0

		#Add the TC field to general array
		field_present += TC_field

	#Count total number of tracks
	track_cesm_present_total += len(track_all) / 25.0
	
for ensemble_i in [6, 7, 8, 9, 10]:
	#Get the present-day ensemble
	fh = netcdf.Dataset(directory_cesm+'_'+str(ensemble_i).zfill(3)+'/Atmosphere/TC_tracker.nc', 'r')

	#Writing data to correct variable	
	track_all	= fh.variables['TC_tracks'][:]

	fh.close()

	for track_i in range(len(track_all)):
		#Loop over each track
		TC_field	= np.zeros((len(lat), len(lon)))
		track		= track_all[track_i]
		lon_track	= track[:, 1]
		lat_track	= track[:, 2]

		#Remove masked elements
		mask_index	= np.where(lon_track.mask == True)[0][0]
		lon_track	= lon_track[:mask_index]
		lat_track	= lat_track[:mask_index]

		for time_i in range(len(lon_track)):
			#Determine the index
			lon_index	= (np.fabs(lon - lon_track[time_i])).argmin()
			lat_index	= (np.fabs(lat - lat_track[time_i])).argmin()

			if TC_field[lat_index, lon_index] == 0:
				#Only count each grid cell once per TC
				TC_field[lat_index, lon_index] += 1.0

		#Add the TC field to general array
		field_future += TC_field

	#Count total number of tracks
	track_cesm_future_total += len(track_all) / 25.0
	
#-----------------------------------------------------------------------------------------
fh = netcdf.Dataset(directory_ibtracs+'IBTrACS_TC_tracks_year_'+str(year_start)+'-'+str(year_end)+'.nc', 'r')

#Writing data to correct variable	
track_all	= fh.variables['TC_tracks'][:]

fh.close()

for track_i in range(len(track_all)):
	#Loop over each track
	TC_field	= np.zeros((len(lat), len(lon)))
	track		= track_all[track_i]
	lon_track	= track[:, 1]
	lat_track	= track[:, 2]

	#Remove masked elements
	mask_index	= np.where(lon_track.mask == True)[0][0]
	lon_track	= lon_track[:mask_index]
	lat_track	= lat_track[:mask_index]

	for time_i in range(len(lon_track)):
		#Determine the index
		lon_index	= (np.fabs(lon - lon_track[time_i])).argmin()
		lat_index	= (np.fabs(lat - lat_track[time_i])).argmin()

		if TC_field[lat_index, lon_index] == 0:
			#Only count each grid cell once per TC
			TC_field[lat_index, lon_index] += 1.0

	#Add the TC field to general array
	field_obs += TC_field

track_ibtracs_total	= len(track_all) / 25.0

#-----------------------------------------------------------------------------------------
#Determine the difference in TC density (scaled to global TC rate)
field_diff		= (field_present / track_cesm_present_total) -  (field_obs / track_ibtracs_total)
cNorm  			= colors.Normalize(vmin=-1, vmax= 1.0) 		#Probablility
scalarMap 		= cm.ScalarMappable(norm=cNorm, cmap='RdBu_r') 	#Using colormap

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

fig, ax	= subplots()	
x, y 	= np.meshgrid(lon, lat)
levels 	= np.arange(-1, 1.1, 0.1)
cs 	= contourf(x,y, field_diff, levels, extend = 'both', cmap='RdBu_r', norm=cNorm)

fig, ax	= subplots(figsize = (14, 8))

m = Basemap(projection='robin',lon_0=180,resolution='i', area_thresh = 250, ax = ax)
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-90,101,30),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(-180,181,60),labels=[0,0,0,1])

deviation 	= grid_size / 2.0 - 0.2

for lat_i in range(len(lat)):
	for lon_i in range(len(lon)):
		if field_diff[lat_i, lon_i] == 0:
			continue

		x1,y1 = m(lon[lon_i] - deviation, lat[lat_i] - deviation) #Bottom left
		x2,y2 = m(lon[lon_i] - deviation, lat[lat_i] + deviation) #Top left
		x3,y3 = m(lon[lon_i] + deviation, lat[lat_i] + deviation) #Top right
		x4,y4 = m(lon[lon_i] + deviation, lat[lat_i] - deviation) #Bottom right
		color_count =  scalarMap.to_rgba(field_diff[lat_i, lon_i])
		p = Polygon([(x1,y1),(x2,y2),(x3,y3),(x4,y4)],facecolor=color_count, linewidth=0) 
		plt.gca().add_patch(p) 		
	
cbar = m.colorbar(cs, cmap = scalarMap, norm = cNorm, ticks = np.arange(-1, 1.1, 1))
cbar.set_label('TC trajectory density difference')
ax.set_title('e) UH-CESM$^{\mathrm{PD}}$ minus IBTrACS v4.0')

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

#Determine the difference in TC density (scaled to global TC rate)
field_cesm_diff	= (field_future / track_cesm_future_total) -  (field_present / track_cesm_present_total)
cNorm_2  		= colors.Normalize(vmin=-0.7/3., vmax= 0.7/3.) 		#Probablility
scalarMap_2		= cm.ScalarMappable(norm=cNorm_2, cmap='RdBu_r') 	#Using colormap

fig, ax	= subplots()	
x, y 	= np.meshgrid(lon, lat)
levels 	= np.arange(-0.7/3., 0.7/3. + 0.0001, 0.1/3)

cs_2 	= contourf(x,y, field_cesm_diff, levels, extend = 'both', cmap='RdBu_r', norm=cNorm_2)

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#Rescale the CESM difference plot
scale				= 3
cut_off				= 0.1
field_cesm_diff[field_cesm_diff < -cut_off]	= (field_cesm_diff[field_cesm_diff < -cut_off] - -cut_off) / scale - cut_off
field_cesm_diff[field_cesm_diff > cut_off]	= (field_cesm_diff[field_cesm_diff > cut_off] - cut_off) / scale + cut_off

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (14, 8))

m = Basemap(projection='robin',lon_0=180,resolution='i', area_thresh = 250, ax = ax)
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-90,101,30),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(-180,181,60),labels=[0,0,0,1])

deviation 	= grid_size / 2.0 - 0.2

for lat_i in range(len(lat)):
	for lon_i in range(len(lon)):
		if field_cesm_diff[lat_i, lon_i] == 0:
			continue

		x1,y1 = m(lon[lon_i] - deviation, lat[lat_i] - deviation) #Bottom left
		x2,y2 = m(lon[lon_i] - deviation, lat[lat_i] + deviation) #Top left
		x3,y3 = m(lon[lon_i] + deviation, lat[lat_i] + deviation) #Top right
		x4,y4 = m(lon[lon_i] + deviation, lat[lat_i] - deviation) #Bottom right
		color_count =  scalarMap_2.to_rgba(field_cesm_diff[lat_i, lon_i])
		p = Polygon([(x1,y1),(x2,y2),(x3,y3),(x4,y4)],facecolor=color_count, linewidth=0) 
		plt.gca().add_patch(p) 		
		
cbar = m.colorbar(cs_2, cmap = scalarMap_2, norm = cNorm_2, ticks = [-0.7/3, -0.5/3, -0.3/3, 0, 0.3/3, 0.5/3, 0.7/3])
cbar.ax.set_yticklabels([-0.5, -0.3, -0.1, 0, 0.1, 0.3, 0.5])

cbar.set_label('TC trajectory density difference')
ax.set_title('d) $\Delta$UH-CESM')

show()
