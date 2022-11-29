#Program plots the dynamic genesis potential index

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
import matplotlib.patches as mpatches

#Making pathway to folder with all data
directory 		= '../../../Data/UH-CESM/'

def YearlyAverage(lon, lat, field, month_start = 1, month_end = 12):
	"""Determine the yearly-averaged values"""

	#Take twice the amount of years for the month day
	month_days	= np.asarray([31., 28., 31., 30., 31., 30., 31., 31., 30., 31., 30., 31., 31., 28., 31., 30., 31., 30., 31., 31., 30., 31., 30., 31.])
	month_days	= month_days[month_start - 1:month_end]
	month_days	= month_days / np.sum(month_days)

	#Fill the array's with the same dimensions
	month_days_all	= ma.masked_all((len(month_days), len(lat), len(lon)))

	for month_i in range(len(month_days)):
		month_days_all[month_i]		= month_days[month_i]

	#Determine the mean
	field_mean	= np.sum(field * month_days_all, axis = 0)

	return field_mean
	
#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

month_start	= 6
month_end	= 11

#-----------------------------------------------------------------------------------------

fh = netcdf.Dataset(directory+'Atmosphere/DGPI_fields_PRESENT_NA_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')

months			= fh.variables['month'][:]
lon				= fh.variables['lon'][:]
lat				= fh.variables['lat'][:]
omega_present	= fh.variables['OMEGA'][:] 			
VWS_present		= fh.variables['VWS'][:] 			
abs_vor_present	= fh.variables['ABS_VOR'][:] 
du_dy_present	= fh.variables['du_dy'][:]		
area			= fh.variables['AREA'][:] 

fh.close()

#-----------------------------------------------------------------------------------------

fh 		= netcdf.Dataset(directory+'Atmosphere/DGPI_fields_FUTURE_NA_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')

omega_future	= fh.variables['OMEGA'][:] 			
VWS_future		= fh.variables['VWS'][:] 			
abs_vor_future	= fh.variables['ABS_VOR'][:] 
du_dy_future	= fh.variables['du_dy'][:]

fh.close()

#-----------------------------------------------------------------------------------------


#Get the DGPI where only one variable is altered
fh 		= netcdf.Dataset(directory+'Atmosphere/DGPI_changes_NA_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')

DGPI_present		= fh.variables['DGPI_PD'][:] 
DGPI_future			= fh.variables['DGPI_F'][:] 
DGPI_future_VWS		= fh.variables['DGPI_F_VWS'][:] 
DGPI_future_du_dy	= fh.variables['DGPI_F_du_dy'][:] 			
DGPI_future_omega	= fh.variables['DGPI_F_omega'][:] 			
DGPI_future_vor		= fh.variables['DGPI_F_abs_vor'][:] 

fh.close()

#-----------------------------------------------------------------------------------------

DGPI_present_plot	= YearlyAverage(lon, lat, DGPI_present, month_start, month_end)
DGPI_future_plot	= YearlyAverage(lon, lat, DGPI_future, month_start, month_end)
omega_present_plot	= YearlyAverage(lon, lat, omega_present, month_start, month_end)
omega_future_plot	= YearlyAverage(lon, lat, omega_future, month_start, month_end)
vor_present_plot	= YearlyAverage(lon, lat, abs_vor_present, month_start, month_end)
vor_future_plot		= YearlyAverage(lon, lat, abs_vor_future, month_start, month_end)
du_dy_present_plot	= YearlyAverage(lon, lat, du_dy_present, month_start, month_end)
du_dy_future_plot	= YearlyAverage(lon, lat, du_dy_future, month_start, month_end)
VWS_present_plot	= YearlyAverage(lon, lat, VWS_present, month_start, month_end)
VWS_future_plot		= YearlyAverage(lon, lat, VWS_future, month_start, month_end)

#-----------------------------------------------------------------------------------------

#Determine statistics over the MDR region
lon_min			= 275
lon_max			= 345
lat_min			= 10
lat_max			= 20

lon_min_index	= (fabs(lon - lon_min)).argmin()
lon_max_index	= (fabs(lon - lon_max)).argmin() + 1
lat_min_index	= (fabs(lat - lat_min)).argmin()
lat_max_index	= (fabs(lat - lat_max)).argmin() + 1

DGPI_MDR_present		= DGPI_present[:, lat_min_index:lat_max_index, lon_min_index:lon_max_index]
DGPI_MDR_future			= DGPI_future[:, lat_min_index:lat_max_index, lon_min_index:lon_max_index]
DGPI_MDR_future_VWS		= DGPI_future_VWS[:, lat_min_index:lat_max_index, lon_min_index:lon_max_index]
DGPI_MDR_future_du_dy	= DGPI_future_du_dy[:, lat_min_index:lat_max_index, lon_min_index:lon_max_index]
DGPI_MDR_future_omega	= DGPI_future_omega[:, lat_min_index:lat_max_index, lon_min_index:lon_max_index]
DGPI_MDR_future_vor		= DGPI_future_vor[:, lat_min_index:lat_max_index, lon_min_index:lon_max_index]

area					= area[lat_min_index:lat_max_index, lon_min_index:lon_max_index]
area					= ma.masked_array(area, mask = DGPI_MDR_present[0].mask)
area					= area / np.sum(area)

DGPI_MDR_present_season			= np.zeros(len(months))
DGPI_MDR_future_season			= np.zeros(len(months))
DGPI_MDR_future_vor_season		= np.zeros(len(months))
DGPI_MDR_future_omega_season	= np.zeros(len(months))
DGPI_MDR_future_du_dy_season	= np.zeros(len(months))
DGPI_MDR_future_VWS_season		= np.zeros(len(months))

for time_i in range(len(months)):
	#Determine the spatially-averaged DGPI, first set the same zeros in the DGPI future to the GDPI components
	DGPI_MDR_present_season[time_i]		= np.sum(DGPI_MDR_present[time_i] * area)
	DGPI_MDR_future_season[time_i]		= np.sum(DGPI_MDR_future[time_i] * area)
	DGPI_MDR_future_VWS_season[time_i]	= np.sum(DGPI_MDR_future_VWS[time_i] * area)
	DGPI_MDR_future_du_dy_season[time_i]= np.sum(DGPI_MDR_future_du_dy[time_i] * area)
	DGPI_MDR_future_omega_season[time_i]= np.sum(DGPI_MDR_future_omega[time_i] * area)
	DGPI_MDR_future_vor_season[time_i]	= np.sum(DGPI_MDR_future_vor[time_i] * area)
	
	
bar_width = 0.15

fig, ax	= subplots(figsize = (8, 6))

ax.bar(months - 3.0 * bar_width, DGPI_MDR_present_season, bar_width, color='black', alpha = 1.0, linewidth = 0.0, label = 'UH-CESM$^{\mathrm{PD}}$')
ax.bar(months - 2.0 * bar_width, DGPI_MDR_future_season, bar_width, color='red', alpha = 1.0, linewidth = 0.0, label = 'UH-CESM$^{\mathrm{F}}$')
ax.bar(months - 1.0 * bar_width, DGPI_MDR_future_vor_season, bar_width, color='lightskyblue', alpha = 1.0, linewidth = 0.0)
ax.bar(months + 0.0 * bar_width, DGPI_MDR_future_omega_season, bar_width, color='lightsalmon', alpha = 1.0, linewidth = 0.0)
ax.bar(months + 1.0 * bar_width, DGPI_MDR_future_du_dy_season, bar_width, color='royalblue', alpha = 1.0, linewidth = 0.0)
ax.bar(months + 2.0 * bar_width, DGPI_MDR_future_VWS_season, bar_width, color='firebrick', alpha = 1.0, linewidth = 0.0)

ax.set_ylim(0, 3)
ax.set_xticks(np.arange(month_start, month_end+1, 1))
ax.set_xticklabels(['June', 'July', 'Aug.', 'Sep.', 'Oct.', 'Nov.'])
ax.set_ylabel('Dynamic Genesis Potential Index')
ax.grid()

graph_present	= mpatches.Patch(facecolor='black', label='UH-CESM$^{\mathrm{PD}}$')
graph_future	= mpatches.Patch(facecolor='red', label='UH-CESM$^{\mathrm{F}}$')
graph_1			= mpatches.Patch(facecolor='lightskyblue', label=r'$\Delta \zeta_{a,850}$ only')
graph_2			= mpatches.Patch(facecolor='lightsalmon', label=r'$\Delta \omega_{500}$ only')
graph_3			= mpatches.Patch(facecolor='royalblue', label=r'$\Delta \frac{\mathrm{d}u_{500}}{\mathrm{d}y}$ only')
graph_4			= mpatches.Patch(facecolor='firebrick', label=r'$\Delta \mathrm{VWS}$ only')

ax.legend(handles=[graph_present, graph_future, graph_1, graph_2, graph_3, graph_4], loc='upper left', ncol=1)
ax.set_title('d) DGPI MDR, North Atlantic') 

#-----------------------------------------------------------------------------------------

DGPI_diff_plot		= DGPI_future_plot - DGPI_present_plot

#Rescale the GPI plot
scale				= 5
cut_off				= 0.4
DGPI_diff_plot[DGPI_diff_plot < -cut_off]	= (DGPI_diff_plot[DGPI_diff_plot < -cut_off] - -cut_off) / scale - cut_off
DGPI_diff_plot[DGPI_diff_plot > cut_off]	= (DGPI_diff_plot[DGPI_diff_plot > cut_off] - cut_off) / scale + cut_off

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=250, urcrnrlon=360.0001, resolution='i') 
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, DGPI_diff_plot, levels = np.arange(-0.92, 0.921, 0.02), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = [-0.92, -0.72, -0.52, -0.4, -0.2, 0, 0.2, 0.4, 0.52, 0.72, 0.92])
cbar.ax.set_yticklabels([-3, -2, -1, -0.4, -0.2, 0, 0.2, 0.4, 1, 2, 3])
cbar.set_label('Dynamic Genesis Potential Index difference')

x	= [275, 275, 345, 345, 275]
y	= [10, 20, 20, 10, 10]
x, y	= m(x, y)
m.plot(x, y, '--k', linewidth = 2.5)

ax.set_title('c) Dynamic Genesis Potential Index, $\Delta$UH-CESM')

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=250, urcrnrlon=360.0001, resolution='i') 
m.drawcoastlines()
#m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

#Set mask
x_field	= [249, 360]
y_field	= [-5, 65]
x_field, y_field	= m(x_field, y_field)
ax.fill_between(x_field, y_field[0], y_field[-1], facecolor='#cc9966')

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, (omega_future_plot - omega_present_plot) * 86400 / 100, levels = np.arange(-20, 20.1, 1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-20, 20.1, 5))
cbar.set_label('Vertical velocity difference (hPa day$^{-1}$)')

ax.set_title('g) 500 hPa vertical velocity ($\omega$), $\Delta$UH-CESM')

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=250, urcrnrlon=360.0001, resolution='i') 
m.drawcoastlines()
#m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

#Set mask
x_field	= [249, 360]
y_field	= [-5, 65]
x_field, y_field	= m(x_field, y_field)
ax.fill_between(x_field, y_field[0], y_field[-1], facecolor='#cc9966')

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, (du_dy_future_plot - du_dy_present_plot) * 10**6.0, levels = np.arange(-3, 3.1, 0.1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-3, 3.1, 1))
cbar.set_label(r'Meridional shear vorticity ($\times 10^{-6}$ s$^{-1}$)')

ax.set_title('e) 500 hPa Meridional shear vorticity, $\Delta$UH-CESM')

show()
