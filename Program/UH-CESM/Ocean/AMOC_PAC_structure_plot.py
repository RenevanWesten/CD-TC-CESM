#Plots the meridional stream function strength

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
directory 		= '../../../Data/UH-CESM'


#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

AMOC_present= ma.masked_all((5, 42, 221))
AMOC_future	= ma.masked_all((5, 42, 221))
PAC_present	= ma.masked_all((5, 42, 221))
PAC_future	= ma.masked_all((5, 42, 221))

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		print(ensemble_i)
		fh 		= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/AMOC_PAC_structure.nc', 'r')
		depth	= fh.variables['depth'][:]
		lat		= fh.variables['lat'][:]
		AMOC	= np.mean(fh.variables['AMOC'][:], axis = 0)			
		PAC		= np.mean(fh.variables['PAC'][:], axis = 0)			

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			AMOC_present[ensemble_i]	= AMOC
			PAC_present[ensemble_i]		= PAC

		else:
			#Future ensemble
			AMOC_future[ensemble_i]	= AMOC
			PAC_future[ensemble_i]	= PAC

#Take the ensemble mean
AMOC_present= np.mean(AMOC_present, axis = 0)
AMOC_future	= np.mean(AMOC_future, axis = 0)
PAC_present	= np.mean(PAC_present, axis = 0)
PAC_future	= np.mean(PAC_future, axis = 0)

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8,6))

x, y	= np.meshgrid(lat, depth)
CS	= ax.contourf(x, y, AMOC_present, levels = np.arange(-6, 21.1, 0.5), extend = 'both', cmap = 'Spectral_r')
cbar	= colorbar(CS, ticks = np.arange(-6, 21.1, 3))
cbar.set_label('Atlantic Meridional Overturning Circulation (Sv)')

CS_1	= ax.contour(x, y, AMOC_present, levels = [15], colors = 'k', linewidths = 2)
CS_2	= ax.contour(x, y, AMOC_present, levels = [12], colors = 'r', linewidths = 2)
CS_3	= ax.contour(x, y, AMOC_present, levels = [9], colors = 'b', linewidths = 2)
CS_4	= ax.contour(x[10:], y[10:], AMOC_present[10:], levels = [-3], colors = 'k', linewidths = 2)

ax.set_xlim(-30, 70)
ax.set_ylim(5200, 0)
ax.set_ylabel('Depth (m)')

CS_1		= plot([90, 90], [-1, -1], linestyle = '-', color = 'k', linewidth = 2, label = '15 Sv')
CS_2		= plot([90, 90], [-1, -1], linestyle = '-', color = 'r', linewidth = 2, label = '12 Sv')
CS_3		= plot([90, 90], [-1, -1], linestyle = '-', color = 'b', linewidth = 2, label = '9 Sv')
CS_4		= plot([90, 90], [-1, -1], linestyle = '--', color = 'k', linewidth = 2, label = '-3 Sv')

graphs		= CS_1 + CS_2 + CS_3 + CS_4
legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'lower right', ncol=1, numpoints = 1, framealpha = 1.0)

ax.set_xticks(np.arange(-20, 60.1, 20))
ax.set_xticklabels(['20$^{\circ}$S', 'Eq', '20$^{\circ}$N', '40$^{\circ}$N', '60$^{\circ}$N'])

ax.set_title('a) Atlantic Ocean, UH-CESM$^{\mathrm{PD}}$')

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8,6))

x, y	= np.meshgrid(lat, depth)
CS	= ax.contourf(x, y, AMOC_future - AMOC_present, levels = np.arange(-8, 8.1, 0.25), extend = 'both', cmap = 'RdBu_r')
cbar	= colorbar(CS, ticks = np.arange(-8, 8.1, 2))
cbar.set_label('Atlantic Meridional Overturning Circulation difference (Sv)')

CS_1	= ax.contour(x, y, AMOC_future, levels = [15], colors = 'k', linewidths = 2)
CS_2	= ax.contour(x, y, AMOC_future, levels = [12], colors = 'r', linewidths = 2)
CS_3	= ax.contour(x, y, AMOC_future, levels = [9], colors = 'b', linewidths = 2)
CS_4	= ax.contour(x[10:], y[10:], AMOC_future[10:], levels = [-3], colors = 'k', linewidths = 2)


CS_1		= plot([90, 90], [-1, -1], linestyle = '-', color = 'k', linewidth = 2, label = '15 Sv')
CS_2		= plot([90, 90], [-1, -1], linestyle = '-', color = 'r', linewidth = 2, label = '12 Sv')
CS_3		= plot([90, 90], [-1, -1], linestyle = '-', color = 'b', linewidth = 2, label = '9 Sv')
CS_4		= plot([90, 90], [-1, -1], linestyle = '--', color = 'k', linewidth = 2, label = '-3 Sv')
graphs		= CS_1 + CS_2 + CS_3 + CS_4

legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'lower right', ncol=1, numpoints = 1, framealpha = 1.0)

ax.set_xlim(-30, 70)
ax.set_ylim(5200, 0)
ax.set_ylabel('Depth (m)')

ax.set_xticks(np.arange(-20, 60.1, 20))
ax.set_xticklabels(['20$^{\circ}$S', 'Eq', '20$^{\circ}$N', '40$^{\circ}$N', '60$^{\circ}$N'])

ax.set_title('c) Atlantic Ocean, $\Delta$UH-CESM')

#-----------------------------------------------------------------------------------------

#Rescale the streamfunction  plot
scale		 = 5.0
cut_off		 = 5
PAC_present_plot = np.copy(PAC_present)

PAC_present_plot[PAC_present_plot < -cut_off]	= (PAC_present_plot[PAC_present_plot < -cut_off] - -cut_off) / scale - cut_off
PAC_present_plot[PAC_present_plot > cut_off]	= (PAC_present_plot[PAC_present_plot > cut_off] - cut_off) / scale + cut_off


fig, ax	= subplots(figsize = (8,6))

x, y	= np.meshgrid(lat, depth)
CS	= ax.contourf(x, y, PAC_present_plot, levels = np.arange(-10, 10.1, 0.5), extend = 'both', cmap = 'Spectral_r')
cbar	= colorbar(CS, ticks = [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10])
cbar.ax.set_yticklabels([-30, -20, -10, 4, 2, 0, 2, 4, 10, 20, 30])

cbar.set_label('Pacific Meridional Overturning Circulation (Sv)')

CS_1	= ax.contour(x, y, PAC_present, levels = [15], colors = 'k', linewidths = 2)
CS_2	= ax.contour(x, y, PAC_present, levels = [0], colors = 'r', linewidths = 2)
CS_3	= ax.contour(x, y, -PAC_present, levels = [15], colors = 'b', linewidths = 2)

ax.set_xlim(-30, 70)
ax.set_ylim(5200, 0)
ax.set_ylabel('Depth (m)')

CS_1		= plot([90, 90], [-1, -1], linestyle = '-', color = 'k', linewidth = 2, label = '15 Sv')
CS_2		= plot([90, 90], [-1, -1], linestyle = '-', color = 'r', linewidth = 2, label = '0 Sv')
CS_3		= plot([90, 90], [-1, -1], linestyle = '-', color = 'b', linewidth = 2, label = '-15 Sv')

graphs		= CS_1 + CS_2 + CS_3
legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'lower right', ncol=1, numpoints = 1, framealpha = 1.0)

ax.set_xticks(np.arange(-20, 60.1, 20))
ax.set_xticklabels(['20$^{\circ}$S', 'Eq', '20$^{\circ}$N', '40$^{\circ}$N', '60$^{\circ}$N'])

ax.set_title('b) Indian-Pacific Ocean, UH-CESM$^{\mathrm{PD}}$')

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8,6))

x, y	= np.meshgrid(lat, depth)
CS	= ax.contourf(x, y, PAC_future - PAC_present, levels = np.arange(-8, 8.1, 0.25), extend = 'both', cmap = 'RdBu_r')
cbar	= colorbar(CS, ticks = np.arange(-8, 8.1, 2))
cbar.set_label('Pacific Meridional Overturning Circulation difference (Sv)')

CS_1	= ax.contour(x, y, PAC_future, levels = [15], colors = 'k', linewidths = 2)
CS_2	= ax.contour(x, y, PAC_future, levels = [0], colors = 'r', linewidths = 2)
CS_3	= ax.contour(x, y, -PAC_future, levels = [15], colors = 'b', linewidths = 2)

ax.set_xlim(-30, 70)
ax.set_ylim(5200, 0)
ax.set_ylabel('Depth (m)')

CS_1		= plot([90, 90], [-1, -1], linestyle = '-', color = 'k', linewidth = 2, label = '15 Sv')
CS_2		= plot([90, 90], [-1, -1], linestyle = '-', color = 'r', linewidth = 2, label = '0 Sv')
CS_3		= plot([90, 90], [-1, -1], linestyle = '-', color = 'b', linewidth = 2, label = '-15 Sv')

graphs		= CS_1 + CS_2 + CS_3
legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'lower right', ncol=1, numpoints = 1, framealpha = 1.0)

ax.set_xticks(np.arange(-20, 60.1, 20))
ax.set_xticklabels(['20$^{\circ}$S', 'Eq', '20$^{\circ}$N', '40$^{\circ}$N', '60$^{\circ}$N'])

ax.set_title('d) Indian-Pacific Ocean, $\Delta$UH-CESM')

show()

