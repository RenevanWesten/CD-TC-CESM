#Program plots the TOA and SHF

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

month_start	= 1 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end	= 12	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...

TOA_present	= ma.masked_all((5, 684, 1152))
TOA_future	= ma.masked_all((5, 684, 1152))
SHF_present	= ma.masked_all((5, 684, 1152))
SHF_future	= ma.masked_all((5, 684, 1152))
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
		fh = netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/TOA_SHF_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')

		lon		= fh.variables['lon'][:]
		lat		= fh.variables['lat'][:]
		TOA		= fh.variables['TOA'][:]
		SHF		= fh.variables['SHF'][:]

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			TOA_present[ensemble_i]		= TOA
			SHF_present[ensemble_i]		= SHF
			
		else:
			#Future ensemble
			TOA_future[ensemble_i]		= TOA
			SHF_future[ensemble_i]		= SHF

#-----------------------------------------------------------------------------------------

#Take ensemble mean
TOA_present_plot	= np.mean(TOA_present, axis = 0)
TOA_future_plot		= np.mean(TOA_future, axis = 0)
SHF_present_plot	= np.mean(SHF_present, axis = 0)
SHF_future_plot		= np.mean(SHF_future, axis = 0)

TOA_plot			= TOA_future_plot - TOA_present_plot
SHF_plot			= SHF_future_plot - SHF_present_plot
NET_plot			= TOA_plot - ma.filled(ma.masked_array(SHF_plot, mask = SHF_plot.mask), fill_value = 0.0)

#-----------------------------------------------------------------------------------------

#Rescale the plots
scale	= 2.5
cut_off	= 10
TOA_plot[TOA_plot < -cut_off]	= (TOA_plot[TOA_plot < -cut_off] - -cut_off) / scale - cut_off
TOA_plot[TOA_plot > cut_off]	= (TOA_plot[TOA_plot > cut_off] - cut_off) / scale + cut_off
SHF_plot[SHF_plot < -cut_off]	= (SHF_plot[SHF_plot < -cut_off] - -cut_off) / scale - cut_off
SHF_plot[SHF_plot > cut_off]	= (SHF_plot[SHF_plot > cut_off] - cut_off) / scale + cut_off
NET_plot[NET_plot < -cut_off]	= (NET_plot[NET_plot < -cut_off] - -cut_off) / scale - cut_off
NET_plot[NET_plot > cut_off]	= (NET_plot[NET_plot > cut_off] - cut_off) / scale + cut_off
#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-70, urcrnrlat=70, llcrnrlon=0, urcrnrlon=360.0001, resolution='l') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,81,20),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,60),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, TOA_plot, levels = np.arange(-30, 30.1, 1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = [-30, -18, -10, -5, 0, 5, 10, 18, 30])
cbar.ax.set_yticklabels([-60, -30, -10, -5, 0, 5, 10, 30, 60])

cbar.set_label('Top of atmosphere energy input (W m$^{-2}$)')

ax.set_title('a) Contribution of top of atmosphere (TOA), $\Delta$UH-CESM')

#-----------------------------------------------------------------------------------------
fig, ax	= subplots(figsize = (8, 6))
m = Basemap(projection = 'merc', llcrnrlat=-70, urcrnrlat=70, llcrnrlon=0, urcrnrlon=360.0001, resolution='l') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,81,20),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,60),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, SHF_plot, levels = np.arange(-30, 30.1, 1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = [-30, -18, -10, -5, 0, 5, 10, 18, 30])
cbar.ax.set_yticklabels([-60, -30, -10, -5, 0, 5, 10, 30, 60])
cbar.set_label('Ocean energy uptake (W m$^{-2}$)')

ax.set_title('b) Contribution of ocean uptake, $\Delta$UH-CESM')

#-----------------------------------------------------------------------------------------
fig, ax	= subplots(figsize = (8, 6))
m = Basemap(projection = 'merc', llcrnrlat=-70, urcrnrlat=70, llcrnrlon=0, urcrnrlon=360.0001, resolution='l') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,81,20),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,60),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, NET_plot, levels = np.arange(-30, 30.1, 1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = [-30, -18, -10, -5, 0, 5, 10, 18, 30])
cbar.ax.set_yticklabels([-60, -30, -10, -5, 0, 5, 10, 30, 60])
cbar.set_label('Net atmospheric energy input (W m$^{-2}$)')

lon_box	= [280, 280, 360, 360, 280]
lat_box	= [-10, 65, 65, -10, -10]
x, y	= m(lon_box, lat_box)
m.plot(x, y, '-k', linewidth = 3.0)

lon_box	= [120, 120, 200, 200, 120]
lat_box	= [-10, 65, 65, -10, -10]
x, y	= m(lon_box, lat_box)
m.plot(x, y, linestyle = '-', color = 'gray', linewidth = 3.0)

ax.set_title('d) Net atmospheric energy input (NET), $\Delta$UH-CESM')


show()

