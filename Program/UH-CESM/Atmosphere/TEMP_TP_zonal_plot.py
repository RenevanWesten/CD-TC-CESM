#Program plots the zonal mean atmospheric temperature

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf
import matplotlib.colors as colors

#Making pathway to folder with all data
directory 		= '../../../Data/UH-CESM/'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

month_start	= 1
month_end	= 12

#-----------------------------------------------------------------------------------------
fh 			        = netcdf.Dataset(directory+'Atmosphere/TEMP_TP_zonal_mean_PRESENT_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
pres			    = fh.variables['lev'][:]
lat			        = fh.variables['lat'][:]
temp_present		= fh.variables['TEMP'][:]
temp_tp_present		= fh.variables['TEMP_tp'][:]
temp_ex_tp_present	= fh.variables['TEMP_ex_tp'][:]
trop_present		= fh.variables['TPH'][:]

fh.close()

fh 			        = netcdf.Dataset(directory+'Atmosphere/TEMP_TP_zonal_mean_FUTURE_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
pres			    = fh.variables['lev'][:]
lat			        = fh.variables['lat'][:]
temp_future		    = fh.variables['TEMP'][:]
temp_tp_future		= fh.variables['TEMP_tp'][:]
temp_ex_tp_future	= fh.variables['TEMP_ex_tp'][:]
trop_future		    = fh.variables['TPH'][:]

fh.close()
#-----------------------------------------------------------------------------------------


fig, ax	= subplots()

x, y	= np.meshgrid(lat, pres)
CS	= contourf(x, y, temp_future - temp_present, levels = np.arange(-5, 5.1, 0.25), extend = 'both', cmap = 'RdBu_r')
cbar	= colorbar(CS, ticks = np.arange(-5, 5.1, 1))
cbar.set_label('Temperature difference ($^{\circ}$C)')

graph_trop_1	= ax.plot(lat, trop_present, '-k', linewidth = 2.0, label = 'Tropopause$^{\mathrm{PD}}$')
graph_trop_2	= ax.plot(lat, trop_future, '--k', linewidth = 2.0, label = 'Tropopause$^{\mathrm{F}}$')

ax.set_ylabel('Pressure (hPa)')
ax.set_xlim(-70, 70)
ax.set_ylim(950, 20)
ax.set_yscale('log')
ax.grid()

graphs	= graph_trop_1 + graph_trop_2

legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper left', ncol=1, numpoints = 1)

ax.set_xticks(np.arange(-60, 60.1, 20))
ax.set_xticklabels(['60$^{\circ}$S', '40$^{\circ}$S', '20$^{\circ}$S', 'Eq', '20$^{\circ}$N', '40$^{\circ}$N', '60$^{\circ}$N'])
ax.set_yticks([20, 30, 50, 100, 200, 300, 500, 850])
ax.set_yticklabels([20, 30, 50, 100, 200, 300, 500, 850])

ax.set_title('c) Zonal mean temperature, $\Delta$UH-CESM')

#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

graph_1	= ax.plot(temp_tp_future - temp_tp_present, pres, '-r', linewidth = 2.0, label = 'Low latitudes')
graph_2	= ax.plot(temp_ex_tp_future - temp_ex_tp_present, pres, '-k', linewidth = 2.0, label = 'Mid latitudes')

ax.set_xlabel('Temperature difference ($^{\circ}$C)')
ax.set_ylabel('Pressure (hPa)')
ax.set_xlim(-5, 5)
ax.set_ylim(950, 20)
ax.set_yscale('log')
ax.grid()

graphs	= graph_1 + graph_2

legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper right', ncol=1, numpoints = 1)

ax.set_xticks(np.arange(-5, 5.1, 1))
ax.set_yticks([20, 30, 50, 100, 200, 300, 500, 850])
ax.set_yticklabels([20, 30, 50, 100, 200, 300, 500, 850])

ax.set_title('d) Vertical temperature, $\Delta$UH-CESM')

show()