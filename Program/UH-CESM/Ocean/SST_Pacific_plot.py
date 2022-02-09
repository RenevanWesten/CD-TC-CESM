#Program plots the zonal SST gradient

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

month_start			= 1 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end			= 12	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...

temp_present		= ma.masked_all((5, 518, 1821))
temp_future			= ma.masked_all((5, 518, 1821))
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
		fh = netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/SST_Pacific_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')

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
			
#-----------------------------------------------------------------------------------------

#Take the ensemble mean
temp_present            = np.mean(temp_present, axis = 0)
temp_future             = np.mean(temp_future, axis = 0)
temp_global_diff        = np.mean(temp_global_future) - np.mean(temp_global_present)
temp_diff               = temp_future - temp_present - temp_global_diff

#-----------------------------------------------------------------------------------------

fig, ax = subplots(figsize = (8, 4))

m = Basemap(projection = 'merc', llcrnrlat=-25, urcrnrlat=25, llcrnrlon=120, urcrnrlon=300.00001, resolution='l')
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,20),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,60),labels=[0,0,0,1])


x, y    = np.meshgrid(lon, lat)
x, y    = m(x, y)
CS      = m.contourf(x, y, temp_diff, levels = np.arange(-1.5, 1.51, 0.1), extend = 'both', cmap = 'RdBu_r')
cbar    = m.colorbar(CS, ticks = np.arange(-1.5, 1.51, 0.5))
cbar.set_label('SST difference ($^{\circ}$C)')

ax.set_title('a) Sea surface temperature, $\Delta$UH-CESM')

show()
