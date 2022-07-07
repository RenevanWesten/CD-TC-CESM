#Program plots the (zonal) vertical wind shear

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
month_start	= 6
month_end	= 11

u_vel_present	= ma.masked_all((5, 280, 354))
u_vel_future	= ma.masked_all((5, 280, 354))

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
		fh 		= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/Vertical_wind_shear_NA_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lon		= fh.variables['lon'][:]
		lat		= fh.variables['lat'][:]
		u_vel	= fh.variables['UVEL'][:]

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			u_vel_present[ensemble_i]		= u_vel

		else:
			#Future ensemble
			u_vel_future[ensemble_i]		= u_vel

#Take the ensemble mean
u_vel_present_plot	= np.mean(u_vel_present, axis = 0)
u_vel_future_plot	= np.mean(u_vel_future, axis = 0)
u_vel_plot			= u_vel_future_plot - u_vel_present_plot

#-----------------------------------------------------------------------------------------


fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=250, urcrnrlon=360.0001, resolution='i') 
m.drawcoastlines()
#m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

#Set mask
x_field	= [250, 360]
y_field	= [-5, 65]
x_field, y_field	= m(x_field, y_field)
ax.fill_between(x_field, y_field[0], y_field[-1], facecolor='#cc9966')

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, u_vel_future_plot - u_vel_present_plot, levels = np.arange(-5, 5.1, 0.1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-5, 5.1, 1))
cbar.set_label('Zonal vertical wind shear difference (m s$^{-1}$)')
CS_2	= m.contour(x, y, u_vel_present_plot, levels = [12.5], colors = 'gray', linewidths = 2.5, label = '10')
CS_3	= m.contour(x, y, u_vel_future_plot, levels = [12.5], colors = 'k', linewidths = 2.5, label = '10')

CS1	= m.plot([-1, -1], [-1, -1], linestyle = '-', color = 'gray', linewidth = 2.5, label = '12.5 m s$^{-1}$ (PD)')
CS2	= m.plot([-1, -1], [-1, -1], '-k', linewidth = 2.5, label = '12.5 m s$^{-1}$ (F)')

graphs	= CS1 + CS2

legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper left', ncol=1, numpoints = 1)

ax.set_title('f) Zonal vertical wind shear, $\Delta$UH-CESM')

show()



