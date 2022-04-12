#Program plots the NA SSTs difference w.r.t. ERA5

from pylab import *
import numpy
import glob, os
import netCDF4 as netcdf
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap

#Making pathway to folder with all data
directory_era 		= '../../../Data/ERA5/'
directory_cesm 		= '../../../Data/UH-CESM/'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

month_start			= 5 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end			= 11	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...
year_start			= 1993
year_end			= 2017

#-----------------------------------------------------------------------------------------

#Get the ERA5 SSTs
fh 			= netcdf.Dataset(directory_era+'Ocean/SST_WP_month_'+str(month_start)+'-'+str(month_end)+'_'+str(year_start)+'-'+str(year_end)+'.nc', 'r')
lon			= fh.variables['lon'][:]
lat			= fh.variables['lat'][:]
temp_era	= fh.variables['TEMP'][:]

fh.close()

#Get the UH-CESM present-day ensemble (already converted to ERA5 grid)
fh 			= netcdf.Dataset(directory_cesm+'Ocean/SST_PRESENT_ERA5_grid_WP_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
lon			= fh.variables['lon'][:]
lat			= fh.variables['lat'][:]
temp_cesm	= fh.variables['TEMP'][:]

fh.close()

#Take the ensemble mean differences
temp_diff_plot	= np.mean(temp_cesm, axis = 0) - np.mean(temp_era, axis = 0)

#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()
m.fillcontinents(color='#cc9966',lake_color='#99ffff')

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, temp_diff_plot, levels = np.arange(-5, 5.01, 0.1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-5, 5.1, 1))
cbar.set_label('Sea surface temperature difference ($^{\circ}$C)')

CS2	= m.contour(x, y, np.mean(temp_cesm, axis = 0), levels = [25], colors = 'gray', linestyle = '-', linewidths = 2.5)
CS3	= m.contour(x, y, np.mean(temp_era, axis = 0), levels = [25], colors = 'k', linewidths = 2.5)

CS1	= m.plot([-1, -1], [-1, -1], linestyle = '-', color = 'gray', linewidth = 2.5, label = '25$^{\circ}$C (PD)')
CS2	= m.plot([-1, -1], [-1, -1], '-k', linewidth = 2.5, label = '25$^{\circ}$C (ERA5)')

graphs	= CS1 + CS2

legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper left', ncol=1, numpoints = 1)

ax.set_title('h) Sea surface temperature, UH-CESM$^{\mathrm{PD}}$ minus ERA5')

show()


