#Program plots the ITCZ latitude

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf
import matplotlib.colors as colors
from scipy import stats
from mpl_toolkits.basemap import Basemap

#Making pathway to folder with all data
directory 		= '../../../Data/UH-CESM'

def PeriodicBoundaries(lon, lat, field, lon_grids = 1):
	"""Add periodic zonal boundaries for 3D field"""

	#Empty field with additional zonal boundaries
	lon_2				= np.zeros(len(lon) + lon_grids * 2)
	field_2				= ma.masked_all((len(field), len(lat), len(lon_2)))
	
	#Get the left boundary, which is the right boundary of the original field
	lon_2[:lon_grids]		= lon[-lon_grids:] - 360.0
	field_2[:, :, :lon_grids]	= field[:, :, -lon_grids:]

	#Same for the right boundary
	lon_2[-lon_grids:]		= lon[:lon_grids] + 360.0
	field_2[:, :, -lon_grids:]	= field[:, :, :lon_grids]

	#And the complete field
	lon_2[lon_grids:-lon_grids]		= lon
	field_2[:, :, lon_grids:-lon_grids] 	= field

	return lon_2, field_2	

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

month_start		= 6
month_end		= 11

ITCZ_present	= ma.masked_all((5, 60, 214, 1154))
ITCZ_future		= ma.masked_all((5, 60, 214, 1154))
#-----------------------------------------------------------------------------------------

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		print(ensemble_number[ensemble_i])
		fh 			= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/ITCZ_latitude.nc', 'r')
		lon			= fh.variables['lon'][:]
		lat			= fh.variables['lat'][:]
		ITCZ		= fh.variables['ITCZ'][:]
		lon, ITCZ	= PeriodicBoundaries(lon, lat, ITCZ)	

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			ITCZ_present[ensemble_i]	= ITCZ

		else:
			#Future ensemble
			ITCZ_future[ensemble_i]		= ITCZ

#-----------------------------------------------------------------------------------------
lon_min_index		= (fabs(lon - 275)).argmin()
lon_max_index		= (fabs(lon - 345)).argmin() + 1

index				= [x for x in range(60) if ((x+1) % 12 >= month_start) and ((x+1) % 12 <= month_end)]
ITCZ_present_season	= np.sum(ITCZ_present[:, index, :, lon_min_index:lon_max_index], axis = (0, 1, 3))
ITCZ_future_season	= np.sum(ITCZ_future[:, index, :, lon_min_index:lon_max_index], axis = (0, 1, 3))
ITCZ_present_season	= ITCZ_present_season / np.sum(ITCZ_present_season)
ITCZ_future_season	= ITCZ_future_season / np.sum(ITCZ_future_season)
lat_mean_present	= np.sum(lat * ITCZ_present_season)
lat_mean_future		= np.sum(lat * ITCZ_future_season)

#-----------------------------------------------------------------------------------------

index				= [x for x in range(60) if ((x+1) % 12 >= month_start) and ((x+1) % 12 <= month_end)]
ITCZ_present_plot	= np.zeros((len(lat), len(lon)))
ITCZ_future_plot	= np.zeros((len(lat), len(lon)))

for lon_i in range(len(lon)):
	#For each longitude, determine the PDF of the ITCZ
	ITCZ_lon_1	= np.sum(ITCZ_present[:, index, :, lon_i], axis = (0, 1))
	ITCZ_lon_2	= np.sum(ITCZ_future[:, index, :, lon_i], axis = (0, 1))

	ITCZ_present_plot[:, lon_i]	= ITCZ_lon_1 / np.sum(ITCZ_lon_1)
	ITCZ_future_plot[:, lon_i]	= ITCZ_lon_2 / np.sum(ITCZ_lon_2)

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8.2, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=250, urcrnrlon=360.0001, resolution='i') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

levels	= [x / 10000.0 for x in range(-100, 101, 5) if x != 0.0]

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, ITCZ_future_plot - ITCZ_present_plot, levels = levels, extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-0.01, 0.011, 0.01))
cbar.set_label('ITCZ PDF difference')

x	= [275, 275, 345, 345, 275]
y	= [10, 20, 20, 10, 10]
x, y	= m(x, y)
m.plot(x, y, '--k', linewidth = 2.5)

ax2 = fig.add_axes([0.28, 0.44, 0.54, 0.35])

graph_present	= ax2.plot(lat, ITCZ_present_season, linewidth = 2.0, linestyle = '-', color = 'black', label = 'ITCZ$^{\mathrm{PD}}$')
graph_future	= ax2.plot(lat, ITCZ_future_season, linewidth = 2.0, linestyle = '-', color = 'red', label = 'ITCZ$^{\mathrm{F}}$')

ax2.axvline(x = lat_mean_present, linestyle = '--', color = 'black', linewidth = 2.0)
ax2.axvline(x = lat_mean_future, linestyle = '--', color = 'red', linewidth = 2.0)
ax2.set_ylabel('ITCZ PDF')
ax2.grid()

ax2.set_xlim(-25, 25)
ax2.set_ylim(-0.001, 0.05)
ax2.set_xticks(np.arange(-20, 20.1, 10))
ax2.set_xticklabels(['20$^{\circ}$S', '10$^{\circ}$S', 'Eq', '10$^{\circ}$N', '20$^{\circ}$N'])

ax2.text(np.mean(lat_mean_present) + 1.0, 0.048, str(round(np.mean(lat_mean_present), 1)), verticalalignment='top', horizontalalignment='left', color = 'k', fontsize=14)
ax2.text(np.mean(lat_mean_future) - 1, 0.048, str(round(np.mean(lat_mean_future), 1)), verticalalignment='top', horizontalalignment='right', color = 'r', fontsize=14)

graphs	      = graph_present + graph_future
legend_labels = [l.get_label() for l in graphs]
legend        = ax2.legend(graphs, legend_labels, loc = 'upper left', ncol=1, fancybox=True, numpoints = 1)

ax.set_title('c) ITCZ latitude, June - November')
show()
