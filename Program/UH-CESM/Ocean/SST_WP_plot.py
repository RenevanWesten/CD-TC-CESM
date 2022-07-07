#Program plots the WP SSTs difference

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

month_start			= 5 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end			= 11	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...

temp_present		= ma.masked_all((5, 780, 1102))
temp_future			= ma.masked_all((5, 780, 1102))
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
		fh 			= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/SST_WP_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
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

#-----------------------------------------------------------------------------------------

#Take ensemble mean
temp_present_plot	= np.mean(temp_present, axis = 0)
temp_future			= np.mean(temp_future, axis = 0)
temp_global_present	= np.mean(temp_global_present, axis = 0)
temp_global_future	= np.mean(temp_global_future, axis = 0)
temp_future_plot	= temp_future - temp_present_plot - (temp_global_future - temp_global_present)
print('Global mean SST increase:', temp_global_future - temp_global_present)

TOA_present_plot	= np.mean(TOA_present, axis = 0)
TOA_future_plot		= np.mean(TOA_future, axis = 0)
SHF_present_plot	= np.mean(SHF_present, axis = 0)
SHF_future_plot		= np.mean(SHF_future, axis = 0)

TOA_plot		= TOA_future_plot - TOA_present_plot
SHF_plot		= -(SHF_future_plot - SHF_present_plot)
NET_plot		= TOA_plot + ma.filled(SHF_plot, fill_value = 0.0)
NET_plot		= ma.masked_array(NET_plot, mask = SHF_plot.mask)

lon_min			= 100
lon_max			= 180
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

#Rescale the temperature plot
scale	= 4.0
cut_off	= 0.4
temp_future_plot[temp_future_plot < -cut_off]	= (temp_future_plot[temp_future_plot < -cut_off] - -cut_off) / scale - cut_off
temp_future_plot[temp_future_plot > cut_off]	= (temp_future_plot[temp_future_plot > cut_off] - cut_off) / scale + cut_off

fig, ax	= subplots()

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
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

ax.set_title('b) Sea surface temperature, $\Delta$UH-CESM')

show()


