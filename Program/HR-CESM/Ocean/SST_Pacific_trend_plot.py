#Program plots the equatorial SST trend

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap

#Making pathway to folder with all data
directory 		= '../../../Data/HR-CESM/'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------      

fh = netcdf.Dataset(directory+'Ocean/SST_Pacific_trend_year_2000-2100_month_1-12.nc', 'r')

lon             = fh.variables['lon'][:]
lat             = fh.variables['lat'][:]
temp_trend      = fh.variables['TEMP_trend_norm'][:]
trend_sig       = fh.variables['TEMP_trend_norm_sig'][:]

fh.close()

#-----------------------------------------------------------------------------------------

fig, ax = subplots(figsize = (8, 4))

m = Basemap(projection = 'merc', llcrnrlat=-25, urcrnrlat=25, llcrnrlon=120, urcrnrlon=300.00001, resolution='l')
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,20),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,60),labels=[0,0,0,1])


x, y    = np.meshgrid(lon, lat)
x, y    = m(x, y)
CS      = m.contourf(x, y, temp_trend, levels = np.arange(-1.5, 1.51, 0.1), extend = 'both', cmap = 'RdBu_r')
cbar    = m.colorbar(CS, ticks = np.arange(-1.5, 1.51, 0.5))
cbar.set_label('SST trend ($^{\circ}$C per century)')

for lat_i in range(12, len(lat), 25):
        for lon_i in range(0, len(lon), 30):

                if trend_sig[lat_i, lon_i] >= 0.95:

                        x, y = m(lon[lon_i], lat[lat_i])
                        m.scatter(x, y, marker = 'o', edgecolor = 'k' , s = 10, facecolors='none')
                        
ax.set_title('b) Sea surface temperature trend, HR-CESM')

show()

                                                                                                      
