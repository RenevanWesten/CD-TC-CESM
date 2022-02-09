#Program plots the NA SSTs difference

from pylab import *
import numpy
import glob, os
import netCDF4 as netcdf
import matplotlib.colors as colors
from scipy import stats
from mpl_toolkits.basemap import Basemap


#Making pathway to folder with all data
directory 		= '../../../Data/UH-CESM'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

month_start			= 6 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end			= 11	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...

temp_present		= ma.masked_all((5, 960, 1101))
temp_future			= ma.masked_all((5, 960, 1101))
temp_global_present	= ma.masked_all(5)
temp_global_future	= ma.masked_all(5)

heat_present		= ma.masked_all((5, 220))
heat_future			= ma.masked_all((5, 220))
#-----------------------------------------------------------------------------------------

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		fh 			= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/SST_NA_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lon			= fh.variables['lon'][:]
		lat			= fh.variables['lat'][:]
		temp		= fh.variables['TEMP'][:]
		temp_global	= fh.variables['TEMP_global'][:]
		
		fh.close()

		fh 			= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/AMOC_PAC_HEAT_meridional_month_1-12.nc', 'r')
		lat_heat	= fh.variables['lat'][:]
		heat		= np.mean(fh.variables['HEAT_AMOC'][:], axis = 0)	
	
		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			temp_present[ensemble_i]		= temp
			temp_global_present[ensemble_i]	= temp_global
			heat_present[ensemble_i]		= heat

		else:
			#Future ensemble
			temp_future[ensemble_i]			= temp
			temp_global_future[ensemble_i]	= temp_global
			heat_future[ensemble_i]			= heat

#-----------------------------------------------------------------------------------------

#Take ensemble mean
temp_present_plot	= np.mean(temp_present, axis = 0)
temp_future			= np.mean(temp_future, axis = 0)
temp_global_present	= np.mean(temp_global_present, axis = 0)
temp_global_future	= np.mean(temp_global_future, axis = 0)
temp_future_plot	= temp_future - temp_present_plot - (temp_global_future - temp_global_present)
print('Global mean SST increase:', temp_global_future - temp_global_present)

heat_present	= np.mean(heat_present, axis = 0)
heat_future		= np.mean(heat_future, axis = 0)

lat_min			= -3
lat_max			= 61

lat_min_index	= (fabs(lat_heat - lat_min)).argmin()
lat_max_index	= (fabs(lat_heat - lat_max)).argmin() + 1
lat_heat		= lat_heat[lat_min_index:lat_max_index]
heat_plot		= heat_future[lat_min_index:lat_max_index] - heat_present[lat_min_index:lat_max_index]

y_heat			= np.log(np.tan(np.pi/4.0 + lat_heat * np.pi / (2.0 * 180)))
ticks_heat		= np.where(lat_heat % 10.0 == 0)[0]
#-----------------------------------------------------------------------------------------

#Rescale the temperature plot
scale	= 4.0
cut_off	= 0.4
temp_future_plot[temp_future_plot < -cut_off]	= (temp_future_plot[temp_future_plot < -cut_off] - -cut_off) / scale - cut_off
temp_future_plot[temp_future_plot > cut_off]	= (temp_future_plot[temp_future_plot > cut_off] - cut_off) / scale + cut_off

fig, ax	= subplots()

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=250, urcrnrlon=360.0001, resolution='i') 
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

x, y	= m(lon, lat)
CS	= contourf(x, y, temp_future_plot, levels = np.arange(-1.05, 1.051, 0.05), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = [-1.05, -0.8, -0.55, -0.4, -0.2, 0, 0.2, 0.4, 0.55, 0.80, 1.05])
cbar.ax.set_yticklabels([-3, -2, -1, -0.4, -0.2, 0, 0.2, 0.4, 1, 2, 3])
cbar.set_label('Sea surface temperature difference ($^{\circ}$C)')
CS2	= m.contour(x, y, temp_present_plot, levels = [25], colors = 'gray', linestyle = '-', linewidths = 2.5)
CS3	= m.contour(x, y, temp_future, levels = [25], colors = 'k', linewidths = 2.5)

CS1	= m.plot([-1, -1], [-1, -1], linestyle = '-', color = 'gray', linewidth = 2.5, label = '25$^{\circ}$C (PD)')
CS2	= m.plot([-1, -1], [-1, -1], '-k', linewidth = 2.5, label = '25$^{\circ}$C (F)')
graphs	= CS1 + CS2

legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = (0.12, 0.81), ncol=1, numpoints = 1)

ax2 = fig.add_axes([0.125, 0.146, 0.075, 0.707])

ax2.set_xlim(-0.25, 0.25)
ax2.set_ylim(y_heat[0], y_heat[-1])
ax2.plot(heat_plot, y_heat, '-k', linewidth = 2.0)
ax2.fill_betweenx(y_heat, 0, heat_plot, where=heat_plot >= 0, facecolor='red')
ax2.fill_betweenx(y_heat, 0, heat_plot, where=heat_plot <= 0, facecolor='deepskyblue')


for tick_i in ticks_heat:
	ax2.axhline(y = y_heat[tick_i], color = 'k', linestyle = ':')

ax2.axvline(x = 0, color = 'k', linestyle = ':')

ax2.set_xticks([-0.25, 0, 0.25])
ax2.set_yticks(y_heat[ticks_heat])
ax2.set_xticklabels([])
ax2.set_yticklabels([])

ax.set_title('a) Sea surface temperature and meridional heat transport')

show()


