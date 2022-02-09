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

month_start	= 6 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end	= 11	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...

temp_present		= ma.masked_all((5, 280, 354))
temp_future			= ma.masked_all((5, 280, 354))
temp_global_present	= ma.masked_all(5)
temp_global_future	= ma.masked_all(5)

TOA_present		= ma.masked_all((5, 684, 1152))
TOA_future		= ma.masked_all((5, 684, 1152))
SHF_present		= ma.masked_all((5, 684, 1152))
SHF_future		= ma.masked_all((5, 684, 1152))
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
		fh 			= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/TEMP_2m_NA_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')

		lon			= fh.variables['lon'][:]
		lat			= fh.variables['lat'][:]
		temp		= fh.variables['TEMP'][:]
		temp_global	= fh.variables['TEMP_global'][:]

		fh.close()

		fh 			= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/TOA_SHF_month_1-12.nc', 'r')
		lon_2		= fh.variables['lon'][:]
		lat_2		= fh.variables['lat'][:]
		TOA			= fh.variables['TOA'][:]
		SHF			= fh.variables['SHF'][:]

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			temp_present[ensemble_i]		= temp
			temp_global_present[ensemble_i]	= temp_global
			TOA_present[ensemble_i]			= TOA
			SHF_present[ensemble_i]			= SHF

		else:
			#Future ensemble
			temp_future[ensemble_i]			= temp
			temp_global_future[ensemble_i]	= temp_global
			TOA_future[ensemble_i]			= TOA
			SHF_future[ensemble_i]			= SHF


#Take ensemble mean
temp_present_plot	= np.mean(temp_present, axis = 0)
temp_future_plot	= np.mean(temp_future, axis = 0)
temp_global_present	= np.mean(temp_global_present, axis = 0)
temp_global_future	= np.mean(temp_global_future, axis = 0)
temp_future_plot	= temp_future_plot - temp_present_plot - (temp_global_future - temp_global_present)
print('Global mean 2-meter surface temperature increase:', temp_global_future - temp_global_present)


TOA_present_plot	= np.mean(TOA_present, axis = 0)
TOA_future_plot		= np.mean(TOA_future, axis = 0)
SHF_present_plot	= np.mean(SHF_present, axis = 0)
SHF_future_plot		= np.mean(SHF_future, axis = 0)

TOA_plot		= TOA_future_plot - TOA_present_plot
SHF_plot		= -(SHF_future_plot - SHF_present_plot)
NET_plot		= TOA_plot + ma.filled(SHF_plot, fill_value = 0.0)
NET_plot		= ma.masked_array(NET_plot, mask = SHF_plot.mask)

lon_min			= 280
lon_max			= 360
lat_min			= -3.1
lat_max			= 61.1

lon_min_index	= (fabs(lon_2 - lon_min)).argmin()
lon_max_index	= (fabs(lon_2 - lon_max)).argmin() + 1
lat_min_index	= (fabs(lat_2 - lat_min)).argmin()
lat_max_index	= (fabs(lat_2 - lat_max)).argmin() + 1

lat_heat		= lat_2[lat_min_index:lat_max_index]
heat_plot		= np.mean(NET_plot[lat_min_index:lat_max_index, lon_min_index:lon_max_index], axis = 1)

y_heat			= np.log(np.tan(np.pi/4.0 + lat_heat * np.pi / (2.0 * 180)))
ticks_heat		= np.log(np.tan(np.pi/4.0 + np.arange(0, 61, 10) * np.pi / (2.0 * 180)))
y_heat_min		= np.log(np.tan(np.pi/4.0 + -3 * np.pi / (2.0 * 180)))
y_heat_max		= np.log(np.tan(np.pi/4.0 + 61 * np.pi / (2.0 * 180)))

#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=250, urcrnrlon=360.0001, resolution='i') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, temp_future_plot, levels = np.arange(-3, 3.1, 0.1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-3, 3.1, 1))
cbar.set_label('2-meter surface temperature difference ($^{\circ}$C)')

ax2 = fig.add_axes([0.125, 0.146, 0.075, 0.707])

ax2.set_xlim(-25, 25)
ax2.set_ylim(y_heat_min, y_heat_max)
ax2.plot(heat_plot, y_heat, '-k', linewidth = 2.0)
ax2.fill_betweenx(y_heat, 0, heat_plot, where=heat_plot >= 0, facecolor='red')
ax2.fill_betweenx(y_heat, 0, heat_plot, where=heat_plot <= 0, facecolor='deepskyblue')


for tick_i in ticks_heat:
	ax2.axhline(y = tick_i, color = 'k', linestyle = ':')

ax2.axvline(x = 0, color = 'k', linestyle = ':')

ax2.set_xticks([-25, 0, 25])
ax2.set_yticks(ticks_heat)
ax2.set_xticklabels([])
ax2.set_yticklabels([])

ax.set_title('b) 2-meter surface temperature and net atmospheric energy input')

show()


