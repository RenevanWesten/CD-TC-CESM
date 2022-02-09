#Program plots the energy budget

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

month_start	= 1 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end	= 12	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...

TOA_present		= ma.masked_all((5, 322, 257))
TOA_future		= ma.masked_all((5, 322, 257))
LW_present		= ma.masked_all((5, 322, 257))
LW_future		= ma.masked_all((5, 322, 257))
SW_present		= ma.masked_all((5, 322, 257))
SW_future		= ma.masked_all((5, 322, 257))
LH_present		= ma.masked_all((5, 322, 257))
LH_future		= ma.masked_all((5, 322, 257))
SH_present		= ma.masked_all((5, 322, 257))
SH_future		= ma.masked_all((5, 322, 257))
SHF_present		= ma.masked_all((5, 322, 257))
SHF_future		= ma.masked_all((5, 322, 257))
#-----------------------------------------------------------------------------------------

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		print(ensemble_i)
		fh = netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/TOA_SHF_SW_LW_WP_month_'+str(month_start)+'-'+str(month_end)+'.nc', 'r')

		lon		= fh.variables['lon'][:]
		lat		= fh.variables['lat'][:]
		TOA		= fh.variables['TOA'][:]
		LH		= fh.variables['LH'][:]
		SH		= fh.variables['SH'][:]
		LW		= fh.variables['LW'][:]
		SW		= fh.variables['SW'][:]
		SHF		= fh.variables['SHF'][:]

		fh.close()


		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			TOA_present[ensemble_i]		= TOA
			SHF_present[ensemble_i]		= SHF
			LH_present[ensemble_i]		= LH
			SH_present[ensemble_i]		= SH
			LW_present[ensemble_i]		= LW
			SW_present[ensemble_i]		= SW

		else:
			#Future ensemble
			TOA_future[ensemble_i]		= TOA
			SHF_future[ensemble_i]		= SHF
			LH_future[ensemble_i]		= LH
			SH_future[ensemble_i]		= SH
			LW_future[ensemble_i]		= LW
			SW_future[ensemble_i]		= SW

#-----------------------------------------------------------------------------------------

#Take ensemble mean
TOA_present_plot	= np.mean(TOA_present, axis = 0)
TOA_future_plot		= np.mean(TOA_future, axis = 0)
SHF_present_plot	= np.mean(SHF_present, axis = 0)
SHF_future_plot		= np.mean(SHF_future, axis = 0)
LH_present_plot		= np.mean(LH_present, axis = 0)
LH_future_plot		= np.mean(LH_future, axis = 0)
SH_present_plot		= np.mean(SH_present, axis = 0)
SH_future_plot		= np.mean(SH_future, axis = 0)
LW_present_plot		= np.mean(LW_present, axis = 0)
LW_future_plot		= np.mean(LW_future, axis = 0)
SW_present_plot		= np.mean(SW_present, axis = 0)
SW_future_plot		= np.mean(SW_future, axis = 0)

TOA_plot			= TOA_future_plot - TOA_present_plot
SHF_plot			= SHF_future_plot - SHF_present_plot
LH_plot				= LH_future_plot - LH_present_plot
SH_plot				= SH_future_plot - SH_present_plot
LW_plot				= LW_future_plot - LW_present_plot
SW_plot				= SW_future_plot - SW_present_plot
SHF_atm_plot		= SW_plot - LH_plot - SH_plot - LW_plot
NET_plot			= TOA_plot - ma.filled(ma.masked_array(SHF_atm_plot, mask = SHF_plot.mask), fill_value = 0.0)

#-----------------------------------------------------------------------------------------

#Only take the means above ocean
TOA_basin_plot		= ma.masked_array(TOA_plot, mask = SHF_plot.mask)
SHF_atm_basin_plot	= ma.masked_array(SHF_atm_plot, mask = SHF_plot.mask)
NET_basin_plot		= ma.masked_array(NET_plot, mask = SHF_plot.mask)
LH_basin_plot		= ma.masked_array(LH_plot, mask = SHF_plot.mask)
SH_basin_plot		= ma.masked_array(SH_plot, mask = SHF_plot.mask)
LW_basin_plot		= ma.masked_array(LW_plot, mask = SHF_plot.mask)
SW_basin_plot		= ma.masked_array(SW_plot, mask = SHF_plot.mask)

lon_min				= 120
lon_max				= 200
lat_min				= -10.1
lat_max				= 65.1

lon_min_index		= (fabs(lon - lon_min)).argmin()
lon_max_index		= (fabs(lon - lon_max)).argmin() + 1
lat_min_index		= (fabs(lat - lat_min)).argmin()
lat_max_index		= (fabs(lat - lat_max)).argmin() + 1

lat_heat			= lat[lat_min_index:lat_max_index]
NET_basin_plot		= np.mean(NET_basin_plot[lat_min_index:lat_max_index, lon_min_index:lon_max_index], axis = 1)
SHF_atm_basin_plot	= np.mean(SHF_atm_basin_plot[lat_min_index:lat_max_index, lon_min_index:lon_max_index], axis = 1)
TOA_basin_plot		= np.mean(TOA_basin_plot[lat_min_index:lat_max_index, lon_min_index:lon_max_index], axis = 1)
LH_basin_plot		= np.mean(LH_basin_plot[lat_min_index:lat_max_index, lon_min_index:lon_max_index], axis = 1)
SH_basin_plot		= np.mean(SH_basin_plot[lat_min_index:lat_max_index, lon_min_index:lon_max_index], axis = 1)
LW_basin_plot		= np.mean(LW_basin_plot[lat_min_index:lat_max_index, lon_min_index:lon_max_index], axis = 1)
SW_basin_plot		= np.mean(SW_basin_plot[lat_min_index:lat_max_index, lon_min_index:lon_max_index], axis = 1)

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (5, 6))

graph_atm 		= ax.plot(TOA_basin_plot, lat_heat, '-r', linewidth = 2.0, label = 'TOA input')
graph_ocn 		= ax.plot(-SHF_atm_basin_plot, lat_heat, '-b', linewidth = 2.0, label = 'Ocean uptake')
graph_net 		= ax.plot(NET_basin_plot, lat_heat, '-k', linewidth = 2.0, label = 'Net effect')

ax.set_xlim(-35, 35)
ax.set_ylim(-10, 65)
ax.grid()

ax.set_xlabel('Atmospheric energy input (W m$^{-2}$)')

ax.set_yticks(np.arange(-10, 60.1, 10))
ax.set_yticklabels(['10$^{\circ}$S', 'Eq', '10$^{\circ}$N', '20$^{\circ}$N', '30$^{\circ}$N', '40$^{\circ}$N', '50$^{\circ}$N', '60$^{\circ}$N'])

graphs			= graph_net + graph_atm + graph_ocn
legend_labels 	= [l.get_label() for l in graphs]
legend_1      	= ax.legend(graphs, legend_labels, loc = (0.564, 0.33), ncol=1, numpoints = 1, fontsize = 11.5)

ax.set_title('e) Western Pacific energy budget, $\Delta$UH-CESM')
#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

graph_ocn 	= ax.plot(lat_heat, -SHF_atm_basin_plot, '-b', linewidth = 2.0, label = 'Ocean uptake')
graph_LH	= ax.plot(lat_heat, LH_basin_plot, '-c', linewidth = 2.0, label = 'Latent heat')
graph_SH 	= ax.plot(lat_heat, SH_basin_plot, '-r', linewidth = 2.0, label = 'Sensible heat')
graph_LW	= ax.plot(lat_heat, LW_basin_plot, linestyle = '-', color = 'k', linewidth = 2.0, label = 'Net longwave')
graph_SW	= ax.plot(lat_heat, -SW_basin_plot, linestyle = '-', color = 'darkorange', linewidth = 2.0, label = 'Net shortwave')

ax.set_xlim(-10, 65)
ax.set_ylim(-35, 35)
ax.grid()

ax.set_ylabel('Atmospheric energy input (W m$^{-2}$)')

ax.set_xticks(np.arange(-10, 60.1, 10))
ax.set_xticklabels(['10$^{\circ}$S', 'Eq', '10$^{\circ}$N', '20$^{\circ}$N', '30$^{\circ}$N', '40$^{\circ}$N', '50$^{\circ}$N', '60$^{\circ}$N'])

graphs		= graph_ocn + graph_LH + graph_SH + graph_LW + graph_SW
legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper left', ncol=2, numpoints = 1)

ax.set_title('g) Western Pacific energy budget, $\Delta$UH-CESM')
	
show()

