#Program plots the TCs tracks

from pylab import *
import numpy
import datetime
import time
import glob, os
import netCDF4 as netcdf
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.basemap import Basemap

#Making pathway to folder with all data
directory 		= '../../Data/IBTrACS/'

font = {'size'   : 16}
matplotlib.rc('font', **font)

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------	

year_start	= 1993
year_end	= 2017

#-----------------------------------------------------------------------------------------	

fig, ax	= subplots(figsize = (14, 8))

m = Basemap(projection='robin',lon_0=180,resolution='i', area_thresh = 250, ax = ax)
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-90,101,30),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(-180,181,60),labels=[0,0,0,1])

#Loop over each ensemble
fh 				= netcdf.Dataset(directory+'IBTrACS_TC_tracks_year_'+str(year_start)+'-'+str(year_end)+'.nc', 'r')
track_number	= fh.variables['track_number'][:]
track_all		= fh.variables['TC_tracks'][:]
	
fh.close()

for track_i in range(len(track_all)):
	#Loop over each track
	track		= track_all[track_i]
	lon_track	= track[:, 1]
	lat_track	= track[:, 2]
	vel_track	= track[:, 3]

	#Remove masked elements
	mask_index	= np.where(lon_track.mask == True)[0][0]

	lon_track	= lon_track[:mask_index]
	lat_track	= lat_track[:mask_index]
	vel_track	= vel_track[:mask_index]

	#Check for jumps between 360 to 0
	lon_diff	= fabs(lon_track[1:] - lon_track[:-1])

	if np.max(lon_diff) > 300:
		#Jump in array
		index			= np.where(lon_track < 50)[0][0]

		#Seperate the tracks east of 360
		lon_track_2		= lon_track[index:]
		lat_track_2		= lat_track[index:]
		vel_track_2		= vel_track[index:]

		#Tracks west of 360
		lon_track		= lon_track[:index]
		lat_track		= lat_track[:index]
		vel_track		= vel_track[:index]

		#Mercator plot
		lon_track_2, lat_track_2	= m(lon_track_2, lat_track_2)

		#Only plot the eastern half
		points 		= np.array([lon_track_2, lat_track_2]).T.reshape(-1, 1, 2)
		segments 	= np.concatenate([points[:-1], points[1:]], axis=1)

		#Create a continuous norm to map from data points to colors
		norm 	= plt.Normalize(17, 70)
		lc 		= LineCollection(segments, cmap='Spectral_r', norm=norm)

		# Set the values used for colormapping
		lc.set_array(vel_track_2)
		lc.set_linewidth(2)
		line = ax.add_collection(lc)

	#Mercator plot
	lon_track, lat_track	= m(lon_track, lat_track)

	#Create a set of line segments so that we can color them individually
	#This creates the points as a N x 1 x 2 array so that we can stack points
	#together easily to get the segments. The segments array for line collection
	#needs to be (numlines) x (points per line) x 2 (for x and y)
	points 		= np.array([lon_track, lat_track]).T.reshape(-1, 1, 2)
	segments 	= np.concatenate([points[:-1], points[1:]], axis=1)

	#Create a continuous norm to map from data points to colors
	norm 	= plt.Normalize(17, 70)
	lc 		= LineCollection(segments, cmap='Spectral_r', norm=norm)

	# Set the values used for colormapping
	lc.set_array(vel_track)
	lc.set_linewidth(1.5)
	line = ax.add_collection(lc)

cbar	= m.colorbar(line, ax=ax, extend = 'both', ticks = np.arange(20, 70.1, 10))
cbar.set_label('Maximum wind speed (m s$^{-1}$)')

ax.set_title('c) IBTrACS v4.0, 1993 - 2017')

print('Total number of TCs', len(track_all))

show()

	
