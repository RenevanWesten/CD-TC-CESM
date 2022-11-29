#Plots the TC minimum pressure

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf
import matplotlib.colors as colors
import matplotlib.patches as mpatches

#Making pathway to folder with all data
directory_cesm 		= '../../../Data/UH-CESM'
directory_ibtracs 	= '../../../Data/IBTrACS/'

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------


pres_present	= []
pres_future	= []

for ensemble_i in range(1, 11):
	#Add genesis latitidue for the North Atlantic
	print(ensemble_i)
	fh = netcdf.Dataset(directory_cesm+'_'+str(ensemble_i).zfill(3)+'/Atmosphere/TC_tracker.nc', 'r')

	#Writing data to correct variable	
	track_all	= fh.variables['TC_tracks'][:]

	fh.close()

	for track_i in range(len(track_all)):
		#Add to general array
		pres_TC = np.min(track_all[track_i, :, 3])

		if ensemble_i <= 5:
			pres_present.append(pres_TC)
					
		if ensemble_i >= 6:
			pres_future.append(pres_TC)


#-----------------------------------------------------------------------------------------

fh = netcdf.Dataset(directory_ibtracs+'IBTrACS_TC_tracks_year_1993-2017.nc', 'r')

#Writing data to correct variable	
pres_ibtracs	= np.min(fh.variables['TC_tracks'][:, :, 4], axis = 1)

fh.close()

#-----------------------------------------------------------------------------------------
bins				= 10
pres_bins			= np.arange(855, 1020.1, bins)
pres				= np.arange(pres_bins[0] + bins / 2.0, pres_bins[-1], bins)
TC_pres_present		= np.zeros((len(pres_bins)))
TC_pres_future		= np.zeros((len(pres_bins)))
TC_pres_ibtracs		= np.zeros((len(pres_bins)))

for pres_i in range(len(pres_present)):
	#Get the pres boundaries
	index					= np.where(pres_present[pres_i] >= pres_bins)[0][-1]
	TC_pres_present[index] 	+= 1.0

for pres_i in range(len(pres_future)):
	#Get the pres boundaries
	index					= np.where(pres_future[pres_i] >= pres_bins)[0][-1]
	TC_pres_future[index] 	+= 1.0

for pres_i in range(len(pres_ibtracs)):
	#Get the pres boundaries
	if pres_ibtracs[pres_i] is ma.masked:
		continue
	index					= np.where(pres_ibtracs[pres_i] >= pres_bins)[0][-1]
	TC_pres_ibtracs[index] 	+= 1.0

#-----------------------------------------------------------------------------------------

bar_width = 3

fig, ax	= subplots(figsize = (12, 4.5))

ax.bar(pres - 1.5 * bar_width, TC_pres_present[:-1] / np.sum(TC_pres_present), bar_width, color='black', alpha = 1.0, linewidth = 0.0, label = 'UH-CESM$^{\mathrm{PD}}$')
ax.bar(pres - 0.5 * bar_width, TC_pres_future[:-1] / np.sum(TC_pres_future), bar_width, color='red', alpha = 1.0, linewidth = 0.0, label = 'UH-CESM$^{\mathrm{F}}$')
ax.bar(pres + 0.5 * bar_width, TC_pres_ibtracs[:-1] / np.sum(TC_pres_future), bar_width, color='blue', alpha = 1.0, linewidth = 0.0, label = 'IBTrACS ')

ax.set_xlim(860, 1020)
ax.set_xticks(pres)
ax.set_ylabel('Frequency')
ax.set_xlabel('Pressure (hPa)')
ax.grid()

graph_present	= mpatches.Patch(facecolor='black', label='UH-CESM$^{\mathrm{PD}}$')
graph_future	= mpatches.Patch(facecolor='red', label='UH-CESM$^{\mathrm{F}}$')
graph_ibtracs	= mpatches.Patch(facecolor='blue', label='IBTrACS v4.0')

ax.legend(handles=[graph_present, graph_future, graph_ibtracs], loc='upper left', ncol=1)
ax.set_title('f) Tropical cyclone pressure minimum')

show()

#-----------------------------------------------------------------------------------------

