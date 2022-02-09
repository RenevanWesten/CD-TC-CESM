#Program plots the zonal SST gradient

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf
import matplotlib.colors as colors
from scipy import stats

#Making pathway to folder with all data
directory 		= '../../../Data/HR-CESM/'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

fh = netcdf.Dataset(directory+'Ocean/SST_Pacific_mean.nc', 'r')

lon		= fh.variables['lon'][:]
temp	= fh.variables['TEMP'][:]

fh.close()

#-----------------------------------------------------------------------------------------
#Take the 10-yr and remove the minimum
temp_present		= temp[3:8]
temp_future			= temp[93:98]
temp_present_plot	= np.mean(temp_present, axis = 0)
temp_future_plot	= np.mean(temp_future, axis = 0)

#-----------------------------------------------------------------------------------------
lon_min_index		= (fabs(lon - 150)).argmin()
lon_max_index		= (fabs(lon - 240)).argmin() + 1
lon_section		= lon[lon_min_index:lon_max_index]
temp_present_section	= temp_present[:, lon_min_index:lon_max_index]
temp_future_section	= temp_future[:, lon_min_index:lon_max_index]

trend_present_all	= np.zeros((5, 2))
trend_future_all	= np.zeros((5, 2))

for year_i in range(5):	
	#Determine the temperature trends
	trend_present, base_present 	= polyfit(lon_section, temp_present_section[year_i] - np.min(temp_present_plot), 1)
	trend_future, base_future 	= polyfit(lon_section, temp_future_section[year_i] - np.min(temp_future_plot), 1)
	
	trend_present_all[year_i] 	= [trend_present, base_present]
	trend_future_all[year_i]  	= [trend_future, base_future]

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize=(8,6))

graph_present = ax.plot(lon, temp_present_plot - np.min(temp_present_plot), '-k', linewidth = 2.0, label = 'HR-CESM$^{\mathrm{PD}}$')
graph_future = ax.plot(lon, temp_future_plot - np.min(temp_future_plot), '-r', linewidth = 2.0, label = 'HR-CESM$^{\mathrm{F}}$')

ax.set_xlim(120, 300)
ax.set_ylim(-1, 6)
ax.set_xticks(np.arange(120, 300.1, 30))
ax.set_ylabel('Sea surface temperature relative to minimum ($^{\circ}$C)')
ax.grid()

ax2 	= ax.twinx()

graph_diff = ax2.plot(lon, temp_future_plot - np.min(temp_future_plot) - (temp_present_plot - np.min(temp_present_plot)), '-b', linewidth = 2.0, label = '$\Delta$HR-CESM')

ax2.set_ylabel('Sea surface temperature difference ($^{\circ}$C)')
ax2.set_xlim(120, 300)
ax2.set_ylim(-2, 0.8)
ax2.set_yticks(np.arange(-2, 0.81, 0.4))

ax.plot([268.1, 268.10], [-1, 0], '--k', linewidth = 2.0)
ax.text(268.1-1, -0.7, str(round(np.min(temp_present_plot), 1)), verticalalignment='bottom', horizontalalignment='right', color = 'k', fontsize=14)
ax.text(268.1+1, -0.7, str(round(np.min(temp_future_plot), 1)), verticalalignment='bottom', horizontalalignment='left', color = 'r', fontsize=14)

graphs	      = graph_present + graph_future + graph_diff
legend_labels = [l.get_label() for l in graphs]
legend        = ax.legend(graphs, legend_labels, loc = 'upper right', ncol=1, fancybox=True, numpoints = 1)

#Plot the trends
ax.plot(lon_section, np.mean(trend_present_all[:, 0]) * lon_section + np.mean(trend_present_all[:, 1]), linestyle = '--', color = 'dimgray', linewidth = 2.0)
ax.plot(lon_section, np.mean(trend_future_all[:, 0]) * lon_section + np.mean(trend_future_all[:, 1]), linestyle = '--', color = 'firebrick', linewidth = 2.0)

ax.plot([150, 240], [0, 0], '-k', linewidth = 2.0)
ax.plot([150, 150], [-0.25, 0.25], '-k', linewidth = 2.0)
ax.plot([240, 240], [-0.25, 0.25], '-k', linewidth = 2.0)

ax.text(190, 0.0, '$\Delta T^{\mathrm{PD}}$ = '+str(round(np.mean(trend_present_all[:, 0])*(lon_section[-1]-lon_section[0]), 1))+' $\pm$ '+str(round(np.std(trend_present_all[:, 0])*(lon_section[-1]-lon_section[0]), 2)), verticalalignment='bottom', horizontalalignment='center', color = 'k', fontsize=14)
ax.text(190, -0.1, '$\Delta T^{\mathrm{F}}$ = '+str(round(np.mean(trend_future_all[:, 0])*(lon_section[-1]-lon_section[0]), 1))+' $\pm$ '+str(round(np.std(trend_future_all[:, 0])*(lon_section[-1]-lon_section[0]), 2)), verticalalignment='top', horizontalalignment='center', color = 'k', fontsize=14)

ax.set_xticklabels(['120$^{\circ}$E', '150$^{\circ}$E', '180$^{\circ}$', '150$^{\circ}$W', '120$^{\circ}$W', '90$^{\circ}$W', '60$^{\circ}$W'])
ax.set_title('d) Meridional mean sea surface temperature, HR-CESM')
show()

