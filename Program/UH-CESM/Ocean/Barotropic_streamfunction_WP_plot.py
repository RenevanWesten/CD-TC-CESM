#Program determines the Nino 3.4 index

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
from scipy.ndimage import gaussian_filter

#Making pathway to folder with all data
directory 		= '../../../Data/UH-CESM'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------
month_start		= 1
month_end		= 12

#-----------------------------------------------------------------------------------------
BSF_present			= ma.masked_all((5, 780, 1302))
BSF_future			= ma.masked_all((5, 780, 1302))
WIND_present		= ma.masked_all((5, 782,1104))
WIND_future			= ma.masked_all((5, 782,1104))
wind_zonal_present	= ma.masked_all((5, 131))
wind_zonal_future	= ma.masked_all((5, 131))

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
		fh 		= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/Barotropic_streamfunction_WP_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lon		= fh.variables['lon'][:]
		lat		= fh.variables['lat'][:]
		BSF		= fh.variables['BSF'][:]
		
		fh.close()
		
		fh 		= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/Wind_stress_curl_WP_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lon_wind= fh.variables['lon'][:]
		lat_wind= fh.variables['lat'][:]
		wind	= fh.variables['WIND'][:]
		
		fh.close()
		
		fh 				= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/Wind_stress_curl_Pacific_basin_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lat_zonal_wind	= fh.variables['lat'][:]
		lat_weight		= fh.variables['lat_weight'][:]
		zonal_wind		= np.mean(fh.variables['WIND'][:], axis = 0)
		
		fh.close()
				
		#Continue for plotting
		lon[lon < -50]	= lon[lon < -50] + 360.0

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			BSF_present[ensemble_i]			= BSF
			WIND_present[ensemble_i]		= wind
			wind_zonal_present[ensemble_i]	= zonal_wind

		else:
			#Future ensemble
			BSF_future[ensemble_i]			= BSF
			WIND_future[ensemble_i]			= wind
			wind_zonal_future[ensemble_i]	= zonal_wind


#Take ensemble mean
BSF_present_plot		= np.mean(BSF_present, axis = 0)
BSF_future_plot			= np.mean(BSF_future, axis = 0)
BSF_future_diff_plot	= BSF_future_plot - BSF_present_plot
wind_present_plot		= np.mean(WIND_present, axis = 0) * 10**7.0
wind_future_plot		= np.mean(WIND_future, axis = 0) * 10**7.0
wind_zonal_present_plot	= np.mean(wind_zonal_present, axis = 0) * 10**7.0
wind_zonal_future_plot	= np.mean(wind_zonal_future, axis = 0) * 10**7.0
wind_present_plot		= gaussian_filter(wind_present_plot, sigma = 10)
wind_present_plot		= ma.masked_array(wind_present_plot, mask = WIND_present[0].mask)
wind_future_plot		= gaussian_filter(wind_future_plot, sigma = 10)
wind_future_plot		= ma.masked_array(wind_future_plot, mask = WIND_present[0].mask)
wind_future_diff_plot	= wind_future_plot - wind_present_plot

lat_min					= -3
lat_max					= 61
lat_min_index			= (fabs(lat_zonal_wind - lat_min)).argmin()
lat_max_index			= (fabs(lat_zonal_wind - lat_max)).argmin() + 1
lat_zonal_wind			= lat_zonal_wind[lat_min_index:lat_max_index]
lat_weight				= lat_weight[lat_min_index:lat_max_index]
lat_weight				= lat_weight / np.sum(lat_weight)
wind_zonal_present_plot	= wind_zonal_present_plot[lat_min_index:lat_max_index]
wind_zonal_future_plot	= wind_zonal_future_plot[lat_min_index:lat_max_index]
wind_zonal_diff_plot	= wind_zonal_future_plot - wind_zonal_present_plot
y_lat					= np.log(np.tan(np.pi/4.0 + lat_zonal_wind * np.pi / (2.0 * 180)))
ticks_heat				= np.where(lat_zonal_wind % 10.0 == 0)[0]

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------


#Rescale the BSF plot
scale	= 5.0
cut_off	= 3
BSF_future_diff_plot[BSF_future_diff_plot < -cut_off]	= (BSF_future_diff_plot[BSF_future_diff_plot < -cut_off] - -cut_off) / scale - cut_off
BSF_future_diff_plot[BSF_future_diff_plot > cut_off]	= (BSF_future_diff_plot[BSF_future_diff_plot > cut_off] - cut_off) / scale + cut_off

#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

x, y	= m(lon, lat)
CS		= contourf(x, y, BSF_present_plot, levels = np.arange(-30, 60.1, 2.5), extend = 'both', cmap = 'Spectral_r')
cbar	= m.colorbar(CS, ticks = np.arange(-30, 60.1, 10))
cbar.set_label('Barotropic streamfunction (Sv)')

x_2, y_2		= m(lon_wind, lat_wind)
CS1_a			= m.contour(x_2, y_2, wind_present_plot, levels = [0], colors = 'gray', linestyles = '-', linewidths = 2.5)
CS1				= m.plot([-1, -1], [-1, -1], linestyle = '-', color = 'gray', linewidth = 2.5, label = '0$^{\mathrm{PD}}$')
graphs	      	= CS1
legend_labels 	= [l.get_label() for l in graphs]
legend_1      	= ax.legend(graphs, legend_labels, loc = (0.12, 0.88), ncol=1, numpoints = 1)

ax2 = fig.add_axes([0.125, 0.146, 0.075, 0.707])

ax2.set_xlim(-1.5, 1.5)
ax2.set_ylim(y_lat[0], y_lat[-1])
ax2.plot(wind_zonal_present_plot, y_lat, '-k', linewidth = 2.0)
ax2.fill_betweenx(y_lat, 0, wind_zonal_present_plot, where=wind_zonal_present_plot >= 0, facecolor='lightsalmon')
ax2.fill_betweenx(y_lat, 0, wind_zonal_present_plot, where=wind_zonal_present_plot <= 0, facecolor='lightskyblue')

for tick_i in ticks_heat:
	ax2.axhline(y = y_lat[tick_i], color = 'k', linestyle = ':')

ax2.axvline(x = 0, color = 'k', linestyle = ':')

ax2.set_xticks([-2.5, 0, 2.5])
ax2.set_yticks(y_lat[ticks_heat])
ax2.set_xticklabels([])
ax2.set_yticklabels([])

ax.set_title('b) Barotropic streamfunction and wind stress curl, UH-CESM$^{\mathrm{PD}}$')

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

CS		= contourf(x, y, BSF_future_diff_plot, levels = np.arange(-6, 6.1, 0.5), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-6, 6.1, 1))
cbar.ax.set_yticklabels([-18, -13, -8, -3, -2, 1, 0, 1, 2, 3, 8, 13, 18])
cbar.set_label('Barotropic streamfunction difference (Sv)')

x_2, y_2		= m(lon_wind, lat_wind)
CS1_a			= m.contour(x_2, y_2, wind_future_plot, levels = [0], colors = 'k', linestyles = '-', linewidths = 2.5)
CS1				= m.plot([-1, -1], [-1, -1], linestyle = '-', color = 'k', linewidth = 2.5, label = '0$^{\mathrm{F}}$')
CS2_a			= m.contour(x_2, y_2, wind_present_plot, levels = [0], colors = 'gray', linestyles = '-', linewidths = 2.5)
CS2				= m.plot([-1, -1], [-1, -1], linestyle = '-', color = 'gray', linewidth = 2.5, label = '0$^{\mathrm{PD}}$')
graphs	      	= CS1 + CS2
legend_labels 	= [l.get_label() for l in graphs]
legend_1      	= ax.legend(graphs, legend_labels, loc = (0.12, 0.81), ncol=1, numpoints = 1)

ax2 = fig.add_axes([0.125, 0.146, 0.075, 0.707])

ax2.set_xlim(-0.3, 0.3)
ax2.set_ylim(y_lat[0], y_lat[-1])
ax2.plot(wind_zonal_diff_plot, y_lat, '-k', linewidth = 2.0)
ax2.fill_betweenx(y_lat, 0, wind_zonal_diff_plot, where=wind_zonal_diff_plot >= 0, facecolor='red')
ax2.fill_betweenx(y_lat, 0, wind_zonal_diff_plot, where=wind_zonal_diff_plot <= 0, facecolor='deepskyblue')

for tick_i in ticks_heat:
	ax2.axhline(y = y_lat[tick_i], color = 'k', linestyle = ':')

ax2.axvline(x = 0, color = 'k', linestyle = ':')

ax2.set_xticks([-0.3, 0, 0.3])
ax2.set_yticks(y_lat[ticks_heat])
ax2.set_xticklabels([])
ax2.set_yticklabels([])

ax.set_title('d) Barotropic streamfunction and wind stress curl, $\Delta$UH-CESM')

show()
#-----------------------------------------------------------------------------------------
