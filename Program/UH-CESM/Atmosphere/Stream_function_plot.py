#Program plots the Summer Stream function strength

from pylab import *
import numpy
import datetime
import time
import glob, os
import netCDF4 as netcdf
import matplotlib.colors as colors
from scipy import stats

#Making pathway to folder with all data
directory 		= '../../../Data/UH-CESM'

def YearlyConverter(data, month_list):
	"""Determines yearly averaged, over different months of choice,
	default is set to January - December"""

	#Take twice the amount of years for the month day
	month_days	= np.asarray([31., 28., 31., 30., 31., 30., 31., 31., 30., 31., 30., 31.])
	month_days	= month_days[np.asarray(month_list) - 1]
	month_days	= month_days / np.sum(month_days)

	#Fill the array's with the same dimensions
	month_days_all	= ma.masked_all((len(month_days), len(data[0]), len(data[0, 0])))

	for month_i in range(len(month_days)):
		month_days_all[month_i]		= month_days[month_i]

	#Determine the time mean over the months of choice
	data_months	= np.sum(data[np.asarray(month_list) - 1] * month_days_all, axis = 0)

	return data_months

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------


stream_present	= ma.masked_all((5, 12, 30, 514))
stream_future	= ma.masked_all((5, 12, 30, 514))

#-----------------------------------------------------------------------------------------

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		fh 		= netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/Stream_function.nc', 'r')
		pres	= fh.variables['lev'][:]
		lat		= fh.variables['lat'][:]				
		stream	= fh.variables['SF'][:] / 10**10.0	#Stream function (10^10 kg / s)	

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			stream_present[ensemble_i]	= stream

		else:
			#Future ensemble
			stream_future[ensemble_i]	= stream

#Take the ensemble mean
stream_present		= np.mean(stream_present, axis = 0)
stream_future		= np.mean(stream_future, axis = 0)

#Take the summer and winter mean
stream_present_summer	= YearlyConverter(stream_present, [6, 7, 8, 9, 10, 11])
stream_present_winter	= YearlyConverter(stream_present, [12, 1, 2, 3, 4, 5])
stream_future_summer	= YearlyConverter(stream_future, [6, 7, 8, 9, 10, 11])
stream_future_winter	= YearlyConverter(stream_future, [12, 1, 2, 3, 4, 5])

#Get the summer means for the SH and NH
stream_summer_plot				= ma.masked_all(shape(stream_present_summer))
stream_summer_plot[:, :257]		= stream_future_winter[:, :257] - stream_present_winter[:, :257]
stream_summer_plot[:, 257:]		= stream_future_summer[:, 257:] - stream_present_summer[:, 257:]
stream_summer_PD_plot			= ma.masked_all(shape(stream_present_summer))
stream_summer_PD_plot[:, :257]	= stream_present_winter[:, :257]
stream_summer_PD_plot[:, 257:]	= stream_present_summer[:, 257:]

#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

x, y	= np.meshgrid(lat, pres)
CS	= contourf(x, y, stream_summer_plot, levels = np.arange(-3, 3.1, 0.25), extend = 'both', cmap = 'PuOr_r')
cbar	= colorbar(CS, ticks = np.arange(-3, 3.1, 1))
cbar.set_label('Mass streamfunction difference ($10^{10}$ kg s$^{-1}$)')

#ax.set_xlabel('Latitude')
ax.set_ylabel('Pressure (hPa)')
ax.set_xlim(-60, 60)
ax.set_ylim(950, 100)
ax.set_yscale('log')

ax.set_xticks(np.arange(-60, 60.1, 20))
ax.set_xticklabels(['60$^{\circ}$S', '40$^{\circ}$S', '20$^{\circ}$S', 'Eq', '20$^{\circ}$N', '40$^{\circ}$N', '60$^{\circ}$N'])
ax.set_yticks([100, 200, 300, 500, 850])
ax.set_yticklabels([100, 200, 300, 500, 850])

CS3	= ax.contour(x, y, stream_summer_PD_plot - 2, levels = [-1], colors = 'r', linewidths = 2)
CS3	= ax.contour(x, y, stream_summer_PD_plot, levels = [2], colors = 'r', linewidths = 2)
CS3	= ax.contour(x, y, stream_summer_PD_plot, levels = [-1], colors = 'b', linewidths = 2)
CS3	= ax.contour(x, y, stream_summer_PD_plot + 4, levels = [2], colors = 'b', linewidths = 2)

ax.axvline(x = 0, linewidth = 2.0, color = 'k', linestyle = '-')
ax.text(55, 120, 'NH summer', verticalalignment='bottom', horizontalalignment='right', fontsize=14)
ax.text(55, 130, 'Jun - Nov', verticalalignment='bottom', horizontalalignment='right', fontsize=12)
ax.text(-55, 120, 'SH summer', verticalalignment='bottom', horizontalalignment='left', fontsize=14)
ax.text(-55, 130, 'Dec - May', verticalalignment='bottom', horizontalalignment='left', fontsize=12)

ax.set_title('d) Meridional mass streamfunction, $\Delta$UH-CESM')

show()
