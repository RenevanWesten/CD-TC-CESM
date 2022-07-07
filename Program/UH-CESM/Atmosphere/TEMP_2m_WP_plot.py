#Program plots the 2-meter surface temperature

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

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

month_start	= 5 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end	= 11	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...

temp_present		= ma.masked_all((5, 280, 355))
temp_future			= ma.masked_all((5, 280, 355))
temp_global_present	= ma.masked_all(5)
temp_global_future	= ma.masked_all(5)

#-----------------------------------------------------------------------------------------

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		print(ensemble_i)
		fh 			= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/TEMP_2m_WP_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		
		lon			= fh.variables['lon'][:]
		lat			= fh.variables['lat'][:]
		temp		= fh.variables['TEMP'][:]
		temp_global	= fh.variables['TEMP_global'][:]

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			temp_present[ensemble_i]		= temp
			temp_global_present[ensemble_i]	= temp_global

		else:
			#Future ensemble
			temp_future[ensemble_i]			= temp
			temp_global_future[ensemble_i]	= temp_global


#Take ensemble mean
temp_present_plot	= np.mean(temp_present, axis = 0)
temp_future_plot	= np.mean(temp_future, axis = 0)
temp_global_present	= np.mean(temp_global_present, axis = 0)
temp_global_future	= np.mean(temp_global_future, axis = 0)
temp_future_plot	= temp_future_plot - temp_present_plot - (temp_global_future - temp_global_present)
print('Global mean 2-meter surface temperature increase:', temp_global_future - temp_global_present)
#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, temp_future_plot, levels = np.arange(-3, 3.1, 0.1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-3, 3.1, 1))
cbar.set_label('2-meter surface temperature difference ($^{\circ}$C)')

ax.set_title('d) 2-meter surface temperature, $\Delta$UH-CESM')

show()


