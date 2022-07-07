#Program plots the NA SSTs difference

from pylab import *
import numpy
import glob, os
import netCDF4 as netcdf
import matplotlib.colors as colors
from scipy import stats
from mpl_toolkits.basemap import Basemap


#Making pathway to folder with all data
directory 		= '../../../Data/UH-CESM/Ocean/'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------


fh 			= netcdf.Dataset(directory+'SST_WP_2003-01-01.nc', 'r')

lon			= fh.variables['lon'][:]
lat			= fh.variables['lat'][:]
temp		= fh.variables['TEMP'][:]
		
fh.close()

temp_diff_max	= np.max(temp, axis = 0) - np.min(temp, axis = 0)

#-----------------------------------------------------------------------------------------
fig, ax	= subplots()

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

x, y	= m(lon, lat)
CS	= contourf(x, y, temp_diff_max, levels = np.arange(0, 4.051, 0.1), extend = 'max', cmap = 'Spectral_r')
cbar	= m.colorbar(CS, ticks = np.arange(0, 4.1, 1))
cbar.set_label('Sea surface temperature difference ($^{\circ}$C)')

ax.set_title('b) Sea surface temperature difference, 1 January 2003')

show()


