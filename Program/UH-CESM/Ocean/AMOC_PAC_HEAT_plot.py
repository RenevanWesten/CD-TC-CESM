#Program plot the total meridional heat transport

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

#Bot for yearly and TC season
heat_AMOC_present	= ma.masked_all((5, 2, 5, 220))
heat_AMOC_future	= ma.masked_all((5, 2, 5, 220))
heat_PAC_present	= ma.masked_all((5, 2, 5, 220))
heat_PAC_future		= ma.masked_all((5, 2, 5, 220))

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		print(ensemble_i)
		fh 			= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/AMOC_PAC_HEAT_meridional_month_1-12.nc', 'r')
		lat			= fh.variables['lat'][:]
		heat_AMOC	= fh.variables['HEAT_AMOC'][:]	
		heat_PAC	= fh.variables['HEAT_PAC'][:]	

		fh.close()

		#Only for the Atlantic
		fh 					= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/AMOC_PAC_HEAT_meridional_month_6-11.nc', 'r')
		heat_AMOC_season	= fh.variables['HEAT_AMOC'][:]	
		fh.close()

		#Only for the Indian Pacific
		fh 				= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/AMOC_PAC_HEAT_meridional_month_5-11.nc', 'r')
		heat_PAC_season	= fh.variables['HEAT_PAC'][:]	
		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			heat_AMOC_present[ensemble_i, 0]= heat_AMOC
			heat_PAC_present[ensemble_i, 0]	= heat_PAC
			heat_AMOC_present[ensemble_i, 1]= heat_AMOC_season
			heat_PAC_present[ensemble_i, 1]	= heat_PAC_season

		else:
			#Future ensemble
			heat_AMOC_future[ensemble_i, 0]	= heat_AMOC
			heat_PAC_future[ensemble_i, 0]	= heat_PAC
			heat_AMOC_future[ensemble_i, 1]	= heat_AMOC_season
			heat_PAC_future[ensemble_i, 1]	= heat_PAC_season

print(np.mean(heat_AMOC_present[:, 0, :, 125]), np.std(heat_AMOC_present[:, 0, :, 125]))
print(np.mean(heat_AMOC_future[:, 0, :, 125]), np.std(heat_AMOC_future[:, 0, :, 125]))

#Take the ensemble mean
heat_AMOC_present	= np.mean(np.mean(heat_AMOC_present, axis = 2), axis = 0)
heat_AMOC_future	= np.mean(np.mean(heat_AMOC_future, axis = 2), axis = 0)
heat_PAC_present	= np.mean(np.mean(heat_PAC_present, axis = 2), axis = 0)
heat_PAC_future		= np.mean(np.mean(heat_PAC_future, axis = 2), axis = 0)

print(np.argmax(heat_AMOC_present[0]), lat[125])
print(np.argmax(heat_AMOC_future[0]))

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8,6))

ax.plot(lat, heat_AMOC_present[1], linestyle = '--', color = 'dimgray', linewidth = 2.0)
ax.plot(lat, heat_AMOC_future[1], linestyle = '--', color = 'firebrick', linewidth = 2.0)
graph_1		= ax.plot(lat, heat_AMOC_present[0], '-k', linewidth = 2.0, label = 'UH-CESM$^{\mathrm{PD}}$')
graph_2		= ax.plot(lat, heat_AMOC_future[0], '-r', linewidth = 2.0, label = 'UH-CESM$^{\mathrm{F}}$')

ax.set_ylim(0, 1.4)
ax.set_ylabel('Meridional heat transport (PW)')
ax.grid()

ax2 	= ax.twinx()

ax2.plot(lat, heat_AMOC_future[1] - heat_AMOC_present[1], linestyle = '--', color = 'royalblue', linewidth = 2.0)
graph_3	= ax2.plot(lat, heat_AMOC_future[0] - heat_AMOC_present[0], '-b', linewidth = 2.0, label = '$\Delta$UH-CESM')

ax2.set_ylabel('Meridional heat transport difference (PW)')
ax2.set_xlim(-30, 70)
ax2.set_ylim(-0.25, 0.25)

ax.set_xticks(np.arange(-20, 60.1, 20))
ax.set_xticklabels(['20$^{\circ}$S', 'Eq', '20$^{\circ}$N', '40$^{\circ}$N', '60$^{\circ}$N'])

graphs		= graph_1 + graph_2 + graph_3
legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper left', ncol=1, numpoints = 1, framealpha = 1.0)

graph_year	= ax.plot([-100, -100], [-100, -100], '-k', linewidth = 2.0, label = 'Jan - Dec')
graph_season	= ax.plot([-100, -100], [-100, -100], '--k', linewidth = 2.0, label = 'Jun - Nov')

graphs	      	= graph_year + graph_season

legend_labels 	= [l.get_label() for l in graphs]
legend_2	= ax.legend(graphs, legend_labels, bbox_to_anchor=(0.29, 0.17), ncol=1, numpoints = 1, framealpha = 1.0)
ax.add_artist(legend_1)

ax.set_title('e) Atlantic meridional heat transport')

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8,6))

ax.plot(lat, heat_PAC_present[1], linestyle = '--', color = 'dimgray', linewidth = 2.0)
ax.plot(lat, heat_PAC_future[1], linestyle = '--', color = 'firebrick', linewidth = 2.0)
graph_1		= ax.plot(lat, heat_PAC_present[0], '-k', linewidth = 2.0, label = 'UH-CESM$^{\mathrm{PD}}$')
graph_2		= ax.plot(lat, heat_PAC_future[0], '-r', linewidth = 2.0, label = 'UH-CESM$^{\mathrm{F}}$')

ax.set_ylim(-4, 2)
ax.set_ylabel('Meridional heat transport (PW)')
ax.grid()

ax2 	= ax.twinx()

ax2.plot(lat, heat_PAC_future[1] - heat_PAC_present[1], linestyle = '--', color = 'royalblue', linewidth = 2.0)
graph_3	= ax2.plot(lat, heat_PAC_future[0] - heat_PAC_present[0], '-b', linewidth = 2.0, label = '$\Delta$UH-CESM')

ax2.set_ylabel('Meridional heat transport difference (PW)')
ax2.set_xlim(-30, 70)
ax2.set_ylim(-0.5, 0.5)

ax.set_xticks(np.arange(-20, 60.1, 20))
ax.set_xticklabels(['20$^{\circ}$S', 'Eq', '20$^{\circ}$N', '40$^{\circ}$N', '60$^{\circ}$N'])

graphs		= graph_1 + graph_2 + graph_3
legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper right', ncol=1, numpoints = 1, framealpha = 1.0)

graph_year	= ax.plot([-100, -100], [-100, -100], '-k', linewidth = 2.0, label = 'Jan - Dec')
graph_season	= ax.plot([-100, -100], [-100, -100], '--k', linewidth = 2.0, label = 'May - Nov')

graphs	      	= graph_year + graph_season

legend_labels 	= [l.get_label() for l in graphs]
legend_2	= ax.legend(graphs, legend_labels, bbox_to_anchor=(1.0, 0.17), ncol=1, numpoints = 1, framealpha = 1.0)
ax.add_artist(legend_1)

ax.set_title('f) Indian-Pacific meridional heat transport')

show()


