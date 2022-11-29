#Program plots the vertically-integrated (surface to 200 hPa) temperature

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

month_start	= 1
month_end	= 12

#-----------------------------------------------------------------------------------------

temp_present		= ma.masked_all((5, 768, 1152))
temp_future			= ma.masked_all((5, 768, 1152))

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
		fh 				= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/TEMP_200_hPa_surf_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lon				= fh.variables['lon'][:]
		lat				= fh.variables['lat'][:]
		temp			= np.mean(fh.variables['TEMP'][:], axis = 0)
		temp_global		= np.mean(fh.variables['TEMP_global'][:], axis = 0)

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			temp_present[ensemble_i]		= temp
			temp_global_present[ensemble_i]	= temp_global

		else:
			#Future ensemble
			temp_future[ensemble_i]			= temp
			temp_global_future[ensemble_i]	= temp_global

#Take the ensemble mean
temp_present		= np.mean(temp_present, axis = 0)
temp_future			= np.mean(temp_future, axis = 0)

temp_global_present	= np.mean(temp_global_present, axis = 0)
temp_global_future	= np.mean(temp_global_future, axis = 0)
#-----------------------------------------------------------------------------------------

temp_plot	= temp_future - temp_present - (temp_global_future - temp_global_present)
print('Global mean temperature increase:', temp_global_future - temp_global_present)
#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-68, urcrnrlat=68, llcrnrlon=0, urcrnrlon=360.00001, resolution='l') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,20),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,60),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= m.contourf(x, y, temp_plot, levels = np.arange(-0.6, 0.61, 0.05), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-0.6, 0.61, 0.3))
cbar.set_label('Temperature difference ($^{\circ}$C)')

ax.set_title('c) Vertically-averaged (surface to 200 hPa) temperature, $\Delta$UH-CESM')

show()



