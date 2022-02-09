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
directory 		= '../../../Data/ERA5/'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------
month_start	= 5
month_end	= 11

year_start	= 1993
year_end	= 2017

fh = netcdf.Dataset(directory+'/Atmosphere/Vertical_wind_shear_WP_month_'+str(month_start)+'-'+str(month_end)+'_'+str(year_start)+'-'+str(year_end)+'.nc', 'r')

lon		= fh.variables['lon'][:]
lat		= fh.variables['lat'][:]
u_vel	= fh.variables['UVEL'][:]			

fh.close()

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()
#m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

#Set mask
x_field	= [89, 200]
y_field	= [-5, 65]
x_field, y_field	= m(x_field, y_field)
ax.fill_between(x_field, y_field[0], y_field[-1], facecolor='#cc9966')

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, u_vel, levels = np.arange(0, 25.1, 0.5), extend = 'max', cmap = 'Spectral_r')
cbar	= m.colorbar(CS, ticks = np.arange(0, 25.1, 5))
cbar.set_label('Zonal vertical wind shear (m s$^{-1}$)')
CS2	= m.contour(x, y, u_vel, levels = [12.5], colors = 'gray', linewidths = 2.5, label = '10')

CS1	= m.plot([-1, -1], [-1, -1], '-', color = 'gray', linewidth = 2.5, label = '12.5 m s$^{-1}$')
graphs	= CS1

legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper left', ncol=1, numpoints = 1)

ax.set_title('b) Reanalysis (ERA5), May - November')

show()



