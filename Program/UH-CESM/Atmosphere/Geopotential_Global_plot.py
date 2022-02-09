#Program plots the geopotential 

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

Z3_200_present			= ma.masked_all((5, 768,1152))
Z3_200_future			= ma.masked_all((5, 768,1152))
Z3_850_present			= ma.masked_all((5, 768,1152))
Z3_850_future			= ma.masked_all((5, 768,1152))

Z3_200_global_present	= ma.masked_all(5)
Z3_200_global_future	= ma.masked_all(5)
Z3_850_global_present	= ma.masked_all(5)
Z3_850_global_future	= ma.masked_all(5)

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
		fh 				= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/Geopotential_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lon				= fh.variables['lon'][:]
		lat				= fh.variables['lat'][:]
		Z3_200			= fh.variables['Z3_200'][:]
		Z3_850			= fh.variables['Z3_850'][:]
		Z3_200_global	= fh.variables['Z3_200_global'][:]
		Z3_850_global	= fh.variables['Z3_850_global'][:]

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			Z3_200_present[ensemble_i]			= Z3_200
			Z3_850_present[ensemble_i]			= Z3_850
			Z3_200_global_present[ensemble_i]	= Z3_200_global
			Z3_850_global_present[ensemble_i]	= Z3_850_global

		else:
			#Future ensemble
			Z3_200_future[ensemble_i]			= Z3_200
			Z3_850_future[ensemble_i]			= Z3_850
			Z3_200_global_future[ensemble_i]	= Z3_200_global
			Z3_850_global_future[ensemble_i]	= Z3_850_global

#Take the ensemble mean
Z3_200_present			= np.mean(Z3_200_present, axis = 0)
Z3_200_future			= np.mean(Z3_200_future, axis = 0)
Z3_850_present			= np.mean(Z3_850_present, axis = 0)
Z3_850_future			= np.mean(Z3_850_future, axis = 0)

Z3_200_global_present	= np.mean(Z3_200_global_present, axis = 0)
Z3_200_global_future	= np.mean(Z3_200_global_future, axis = 0)
Z3_850_global_present	= np.mean(Z3_850_global_present, axis = 0)
Z3_850_global_future	= np.mean(Z3_850_global_future, axis = 0)

#-----------------------------------------------------------------------------------------

Z_850_plot		= Z3_850_future - Z3_850_present - (Z3_850_global_future - Z3_850_global_present)
Z_200_plot		= Z3_200_future - Z3_200_present - (Z3_200_global_future - Z3_200_global_present)

print('Global mean 850 GZ increase:', Z3_850_global_future - Z3_850_global_present)
print('Global mean 200 GZ increase:', Z3_200_global_future - Z3_200_global_present)
#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-68, urcrnrlat=68, llcrnrlon=0, urcrnrlon=360.00001, resolution='l') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,20),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,60),labels=[0,0,0,1])

#Set mask
x_field	= [0, 360]
y_field	= [-70, 70]
x_field, y_field	= m(x_field, y_field)
ax.fill_between(x_field, y_field[0], y_field[-1], facecolor='#cc9966')

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= m.contourf(x, y, Z_850_plot, levels = np.arange(-15, 15.1, 0.5), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-15, 15.1, 5))
cbar.set_label('Geopotential height difference (m)')

ax.set_title('b) 850 hPa geopotential height, $\Delta$UH-CESM')
#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-68, urcrnrlat=68, llcrnrlon=0, urcrnrlon=360.00001, resolution='l') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,20),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,60),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= m.contourf(x, y, Z_200_plot, levels = np.arange(-50, 50.1, 2.5), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-50, 50.1, 10))
cbar.set_label('Geopotential height difference (m)')

ax.set_title('a) 200 hPa geopotential height, $\Delta$UH-CESM')
show()



