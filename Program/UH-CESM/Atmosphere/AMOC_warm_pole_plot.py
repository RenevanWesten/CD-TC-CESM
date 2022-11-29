#Program plots the surface to 200 hPa temperature, 200 hPa geopoential height and SSTs near the AMOC warm pole

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap

#Making pathway to folder with all data
directory 		= '../../../Data/UH-CESM'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

month_start	= 1
month_end	= 12

#-----------------------------------------------------------------------------------------

temp_present		= ma.masked_all((5, 768,1152))
temp_future			= ma.masked_all((5, 768,1152))
Z3_200_present		= ma.masked_all((5, 768,1152))
Z3_200_future		= ma.masked_all((5, 768,1152))
sst_present			= ma.masked_all((5, 960, 1101))
sst_future			= ma.masked_all((5, 960, 1101))
sst_global_present	= ma.masked_all(5)
sst_global_future	= ma.masked_all(5)


Z3_200_global_present	= ma.masked_all(5)
Z3_200_global_future	= ma.masked_all(5)
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
		fh = netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/TEMP_200_hPa_surf_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')

		lon			= fh.variables['lon'][:]
		lat			= fh.variables['lat'][:]
		temp		= np.mean(fh.variables['TEMP'][:], axis = 0)
		temp_global	= np.mean(fh.variables['TEMP_global'][:], axis = 0)

		fh.close()

		fh = netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/Geopotential_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')

		Z3_200			= fh.variables['Z3_200'][:]
		Z3_200_global	= fh.variables['Z3_200_global'][:]

		fh.close()

		fh = netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/SST_NA_month_6-11.nc', 'r')

		lon_ocn		= fh.variables['lon'][:]
		lat_ocn		= fh.variables['lat'][:]
		sst			= fh.variables['TEMP'][:]
		sst_global	= fh.variables['TEMP_global'][:]

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			temp_present[ensemble_i]			= temp
			temp_global_present[ensemble_i]		= temp_global
			Z3_200_present[ensemble_i]			= Z3_200
			Z3_200_global_present[ensemble_i]	= Z3_200_global
			sst_present[ensemble_i]				= sst
			sst_global_present[ensemble_i]		= sst_global


		else:
			#Future ensemble
			temp_future[ensemble_i]			= temp
			temp_global_future[ensemble_i]	= temp_global
			Z3_200_future[ensemble_i]		= Z3_200
			Z3_200_global_future[ensemble_i]= Z3_200_global
			sst_future[ensemble_i]			= sst
			sst_global_future[ensemble_i]	= sst_global

#Take the ensemble mean
temp_present	= np.mean(temp_present, axis = 0)
temp_future		= np.mean(temp_future, axis = 0)
Z3_200_present	= np.mean(Z3_200_present, axis = 0)
Z3_200_future	= np.mean(Z3_200_future, axis = 0)
sst_present		= np.mean(sst_present, axis = 0)
sst_future		= np.mean(sst_future, axis = 0)

Z3_200_global_present	= np.mean(Z3_200_global_present, axis = 0)
Z3_200_global_future	= np.mean(Z3_200_global_future, axis = 0)
temp_global_present	= np.mean(temp_global_present, axis = 0)
temp_global_future	= np.mean(temp_global_future, axis = 0)
sst_global_present	= np.mean(sst_global_present, axis = 0)
sst_global_future	= np.mean(sst_global_future, axis = 0)


lon_min_index	= (np.abs(lon - 275)).argmin()
lon_max_index	= (np.abs(lon - 345)).argmin()+1
lat_min_index	= (np.abs(lat - 20)).argmin()
lat_max_index	= (np.abs(lat - 60)).argmin()+1

#Get the relevant fields over given region
temp_diff	= temp_future[lat_min_index:lat_max_index, lon_min_index:lon_max_index] - temp_present[lat_min_index:lat_max_index, lon_min_index:lon_max_index] - (temp_global_future - temp_global_present)
Z3_200_diff	= Z3_200_future[lat_min_index:lat_max_index, lon_min_index:lon_max_index] - Z3_200_present[lat_min_index:lat_max_index, lon_min_index:lon_max_index] - (Z3_200_global_future - Z3_200_global_present)
sst_diff	= sst_future - sst_present - (sst_global_future - sst_global_present)

lon		= lon[lon_min_index:lon_max_index]
lat		= lat[lat_min_index:lat_max_index]

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=28, urcrnrlat=52, llcrnrlon=278, urcrnrlon=342.0001, resolution='i') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)

CS		= m.contourf(x, y, temp_diff, levels = np.arange(-0.6, 0.61, 0.05), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-0.6, 0.61, 0.3))
cbar.set_label('Temperature difference ($^{\circ}$C)')

CS2	= m.contour(x, y, Z3_200_diff, levels = [10], colors = 'k', linewidths = 2.5, linestyles = '-')
CS3	= m.contour(x, y, Z3_200_diff, levels = [13], colors = 'k', linewidths = 2.5,  linestyles = '--')

x, y	= m(lon_ocn, lat_ocn)
CS5	= m.contour(x, y, sst_diff, levels = [0.5], colors = 'firebrick', linewidths = 2.5, linestyles = '-')
CS6	= m.contour(x, y, sst_diff, levels = [1.5], colors = 'firebrick', linewidths = 2.0, linestyles = '--')

graph_1	= ax.plot([-1, -1], [-1, -1], linestyle = '-', linewidth = 2.5, color = 'k', label = 'GZ: +10 m')
graph_2	= ax.plot([-1, -1], [-1, -1], linestyle = '--', linewidth = 2.5, color = 'k', label = 'GZ: +13 m')
graph_3	= ax.plot([-1, -1], [-1, -1], linestyle = '-', linewidth = 2.5, color = 'firebrick', label = 'SST: +0.5$^{\circ}$C')
graph_4	= ax.plot([-1, -1], [-1, -1], linestyle = '--', linewidth = 2.5, color = 'firebrick', label = 'SST: +1.5$^{\circ}$C')

graphs	= graph_1 + graph_2 + graph_3 + graph_4

legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'lower left', ncol=1, numpoints = 1, prop ={'size': 12})

ax.set_title('d) Atmospheric temperature, geopotential height and SST')

show()
