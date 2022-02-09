#Program plots the 700 hPa relative humidity and the 500 hPa vertical velocity

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

month_start	= 1
month_end	= 12

RH_present		= ma.masked_all((5, 5, 514))
RH_future		= ma.masked_all((5, 5, 514))
w_vel_present	= ma.masked_all((5, 5, 514))
w_vel_future	= ma.masked_all((5, 5, 514))

#-----------------------------------------------------------------------------------------

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		fh 	= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/RH_700_hPa_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lat	= fh.variables['lat'][:]		
		RH	= fh.variables['RH'][:]	#Relative humidity (%)

		fh.close()
		
		fh 		= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/WVEL_500_hPa_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')
		lat		= fh.variables['lat'][:]		
		w_vel	= fh.variables['OMEGA'][:] * -86400.0 / 100.0	#Vertical velocity (hPa / day)

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			RH_present[ensemble_i]		= RH
			w_vel_present[ensemble_i]	= w_vel

		else:
			#Future ensemble
			RH_future[ensemble_i]		= RH
			w_vel_future[ensemble_i]	= w_vel
#-----------------------------------------------------------------------------------------
#Take the ensemble mean
RH_plot		= np.mean(np.mean(RH_future, axis = 1), axis = 0) - np.mean(np.mean(RH_present, axis = 1), axis = 0)
w_vel_plot	= np.mean(np.mean(w_vel_future, axis = 1), axis = 0) - np.mean(np.mean(w_vel_present, axis = 1), axis = 0)

#-----------------------------------------------------------------------------------------
fig, ax	= subplots()

graph_present	= ax.plot(lat, RH_plot, '-b', linewidth = 2.0, label = '$\Delta$RH')

ax.set_ylabel('Relative humidity difference ($\%$)')
ax.set_xlim(-60, 60)
ax.set_ylim(-5, 5)
ax.grid()

ax2 	= ax.twinx()
graph_delta	= ax2.plot(lat, w_vel_plot, '-k', linewidth = 2.0, label = '$-\Delta \omega$')

ax2.set_ylabel('Vertical velocity difference (hPa day$^{-1}$)')
ax2.set_ylim(-5, 5)
ax2.set_xlim(-60, 60)

ax.set_xticklabels(['60$^{\circ}$S', '40$^{\circ}$S', '20$^{\circ}$S', 'Eq', '20$^{\circ}$N', '40$^{\circ}$N', '60$^{\circ}$N'])

graphs	      = graph_present + graph_delta

legend_labels = [l.get_label() for l in graphs]
ax.legend(graphs, legend_labels, loc='upper left',
 		  ncol=1, fancybox=True, shadow=False, numpoints = 1)

ax.set_title('c) Relative humidity (700 hPa) and vertical velocity (500 hPa), $\Delta$UH-CESM')

show()
