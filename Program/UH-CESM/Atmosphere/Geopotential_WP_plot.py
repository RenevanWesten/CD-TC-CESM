#Program plots the geopotential and horizontal velocities

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

month_start		= 5
month_end		= 11

#-----------------------------------------------------------------------------------------

Z3_200_present			= ma.masked_all((5, 280, 355))
Z3_200_future			= ma.masked_all((5, 280, 355))
Z3_850_present			= ma.masked_all((5, 280, 355))
Z3_850_future			= ma.masked_all((5, 280, 355))

Z3_200_global_present	= ma.masked_all(5)
Z3_200_global_future	= ma.masked_all(5)
Z3_850_global_present	= ma.masked_all(5)
Z3_850_global_future	= ma.masked_all(5)

u_vel_200_present		= ma.masked_all((5, 280, 355))
u_vel_200_future		= ma.masked_all((5, 280, 355))
u_vel_850_present		= ma.masked_all((5, 280, 355))
u_vel_850_future		= ma.masked_all((5, 280, 355))

v_vel_200_present		= ma.masked_all((5, 280, 355))
v_vel_200_future		= ma.masked_all((5, 280, 355))
v_vel_850_present		= ma.masked_all((5, 280, 355))
v_vel_850_future		= ma.masked_all((5, 280, 355))
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
		fh 				= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/Geopotential_WP_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lon				= fh.variables['lon'][:]
		lat				= fh.variables['lat'][:]
		Z3_200			= fh.variables['Z3_200'][:]
		Z3_850			= fh.variables['Z3_850'][:]
		Z3_200_global	= fh.variables['Z3_200_global'][:]
		Z3_850_global	= fh.variables['Z3_850_global'][:]

		fh.close()

		fh 			= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/UV_WP_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		u_vel_200	= fh.variables['UVEL_200'][:]
		u_vel_850	= fh.variables['UVEL_850'][:]
		v_vel_200	= fh.variables['VVEL_200'][:]
		v_vel_850	= fh.variables['VVEL_850'][:]

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			Z3_200_present[ensemble_i]			= Z3_200
			Z3_850_present[ensemble_i]			= Z3_850
			Z3_200_global_present[ensemble_i]	= Z3_200_global
			Z3_850_global_present[ensemble_i]	= Z3_850_global
			u_vel_200_present[ensemble_i]		= u_vel_200
			u_vel_850_present[ensemble_i]		= u_vel_850
			v_vel_200_present[ensemble_i]		= v_vel_200
			v_vel_850_present[ensemble_i]		= v_vel_850

		else:
			#Future ensemble
			Z3_200_future[ensemble_i]			= Z3_200
			Z3_850_future[ensemble_i]			= Z3_850
			Z3_200_global_future[ensemble_i]	= Z3_200_global
			Z3_850_global_future[ensemble_i]	= Z3_850_global
			u_vel_200_future[ensemble_i]		= u_vel_200
			u_vel_850_future[ensemble_i]		= u_vel_850
			v_vel_200_future[ensemble_i]		= v_vel_200
			v_vel_850_future[ensemble_i]		= v_vel_850


#Take the ensemble mean
Z3_200_present			= np.mean(Z3_200_present, axis = 0)
Z3_200_future			= np.mean(Z3_200_future, axis = 0)
Z3_850_present			= np.mean(Z3_850_present, axis = 0)
Z3_850_future			= np.mean(Z3_850_future, axis = 0)

Z3_200_global_present	= np.mean(Z3_200_global_present, axis = 0)
Z3_200_global_future	= np.mean(Z3_200_global_future, axis = 0)
Z3_850_global_present	= np.mean(Z3_850_global_present, axis = 0)
Z3_850_global_future	= np.mean(Z3_850_global_future, axis = 0)

u_vel_200_present		= np.mean(u_vel_200_present, axis = 0)
u_vel_200_future		= np.mean(u_vel_200_future, axis = 0)
u_vel_850_present		= np.mean(u_vel_850_present, axis = 0)
u_vel_850_future		= np.mean(u_vel_850_future, axis = 0)

v_vel_200_present		= np.mean(v_vel_200_present, axis = 0)
v_vel_200_future		= np.mean(v_vel_200_future, axis = 0)
v_vel_850_present		= np.mean(v_vel_850_present, axis = 0)
v_vel_850_future		= np.mean(v_vel_850_future, axis = 0)

#-----------------------------------------------------------------------------------------

Z_850_plot			= Z3_850_future - Z3_850_present - (Z3_850_global_future - Z3_850_global_present)
Z_200_plot			= Z3_200_future - Z3_200_present - (Z3_200_global_future - Z3_200_global_present)
u_vel_850_plot		= u_vel_850_future - u_vel_850_present
v_vel_850_plot		= v_vel_850_future - v_vel_850_present
u_vel_200_plot		= u_vel_200_future - u_vel_200_present
v_vel_200_plot		= v_vel_200_future - v_vel_200_present

print('Global mean 850 GZ increase:', Z3_850_global_future - Z3_850_global_present)
print('Global mean 200 GZ increase:', Z3_200_global_future - Z3_200_global_present)

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

#Set mask
x_field	= [89, 201]
y_field	= [-5, 65]
x_field, y_field	= m(x_field, y_field)
ax.fill_between(x_field, y_field[0], y_field[-1], facecolor='#cc9966')

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, Z_850_plot, levels = np.arange(-15, 15.1, 0.5), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-15, 15.1, 5))
cbar.set_label('Geopotential height difference (m)')

scale_arrow	= 12
Q		= m.quiver(x[::scale_arrow, ::scale_arrow], y[::scale_arrow, ::scale_arrow], u_vel_850_plot[::scale_arrow, ::scale_arrow], v_vel_850_plot[::scale_arrow, ::scale_arrow], scale = 30)

ax2 	= fig.add_axes([0.1315, 0.1725, 0.092, 0.08])
ax2.set_xlim(-1, 1)
ax2.set_ylim(-1, 1)
ax2.set_xticks([-1, 1])
ax2.set_yticks([-1, 1])
ax2.set_xticklabels([])
ax2.set_yticklabels([])

#Make reference scale
x_field	= [251, 265]
y_field	= [0, 9]
x_field, y_field	= m(x_field, y_field)
ax.fill_between(x_field, y_field[0], y_field[-1], facecolor='white')

qk = quiverkey(Q, 0.185, 0.23, 2, '2 m s$^{-1}$', labelpos = 'S', coordinates='figure')

ax.set_title('d) 850 hPa geopotential height and velocity')

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, Z_200_plot, levels = np.arange(-50, 50.1, 2.5), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-50, 50.1, 10))
cbar.set_label('Geopotential height difference (m)')

scale_arrow	= 12
Q = m.quiver(x[::scale_arrow, ::scale_arrow], y[::scale_arrow, ::scale_arrow], u_vel_200_plot[::scale_arrow, ::scale_arrow], v_vel_200_plot[::scale_arrow, ::scale_arrow], scale = 60)

ax2 	= fig.add_axes([0.1315, 0.1725, 0.092, 0.08])
ax2.set_xlim(-1, 1)
ax2.set_ylim(-1, 1)
ax2.set_xticks([-1, 1])
ax2.set_yticks([-1, 1])
ax2.set_xticklabels([])
ax2.set_yticklabels([])

#Make reference scale
x_field	= [251, 265]
y_field	= [0, 9]
x_field, y_field	= m(x_field, y_field)
ax.fill_between(x_field, y_field[0], y_field[-1], facecolor='white')

qk = quiverkey(Q, 0.185, 0.23, 4, '4 m s$^{-1}$', labelpos = 'S', coordinates='figure')

ax.set_title('c) 200 hPa geopotential height and velocity')

show()



