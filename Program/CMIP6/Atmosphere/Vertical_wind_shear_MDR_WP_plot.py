#Program plots the vertical wind shear over the MDR

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
directory 				= '../../../Data/CMIP6/'
directory_ERA5			= '../../../Data/ERA5/'
directory_UH_CESM		= '../../../Data/UH-CESM'
directory_HR_CESM		= '../../../Data/HR-CESM/'

def ReadinDataMDR(filename, month_start, month_end):
	"""Reads-in the data"""

	TEMP_data 	= netcdf.Dataset(filename, 'r')

	#Writing data to correct variable	
	time		= TEMP_data.variables['time'][:]     	
	u_vel		= TEMP_data.variables['UVEL'][:] 	

	TEMP_data.close()
		
	#Take yearly averages
	time_year, u_vel	= YearlyConverter(time, u_vel, month_start, month_end)
	
	return time_year, u_vel

def YearlyConverter(time, data, month_start = 1, month_end = 12):
	"""Determines yearly averaged, over different months of choice,
	default is set to January - December"""

	#Take twice the amount of years for the month day
	month_days	= np.asarray([31., 28., 31., 30., 31., 30., 31., 31., 30., 31., 30., 31., 31., 28., 31., 30., 31., 30., 31., 31., 30., 31., 30., 31.])
	month_days	= month_days[month_start - 1:month_end]
	month_days	= month_days / np.sum(month_days)

	if month_end <= 12:
		#Normal average over a single year, for example, February 100 - December 100
		time_year		= np.zeros(len(time) / 12)

	else:
		#If you take the average, for example, over November 100 - May 101
		#Take year 101 as the average over this period
		#There is one year less compared to the period analysed
		time_year		= np.zeros(len(time) / 12 - 1)

	#-----------------------------------------------------------------------------------------
	data_year	= ma.masked_all(len(time_year))

	for year_i in range(len(time_year)):
		#Determine the SSH over the selected months

		#The year is defined as the current year
		year			= int(str(datetime.date.fromordinal(int(time[year_i * 12])))[0:4])

		if month_end	>= 13:
			#If average is taken over, for example, November 100 - May 101, the year is defined as 101
			year = year + 1

		time_year[year_i] 	= datetime.datetime(year, 1, 1).toordinal()

		#Determine the time mean over the months of choice
		data_year[year_i]		= np.sum(data[year_i * 12 + month_start - 1: year_i * 12 + month_end] * month_days, axis = 0)

	return time_year, data_year

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

month_start		= 5 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end		= 11	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...


model_year_start	= 3	#Start at 2003 (model year 4) and 2093 (model year 94)
model_year_len		= 5	#Add number of year from start
#-----------------------------------------------------------------------------------------
	
#Get the model names and path
models = glob.glob(directory+'*')
models.sort()

for model_i in range(len(models)):
	#Only retain the model names
	models[model_i]	= models[model_i][len(directory):]

#-----------------------------------------------------------------------------------------

for model_i in range(len(models)):
	#For each model get the all the files
	filename_UVEL		= directory+models[model_i]+'/Atmosphere/Vertical_wind_shear_MDR_WP.nc'

	time_year, u_vel	= ReadinDataMDR(filename_UVEL, month_start, month_end)

	if model_i == 0:
		#First file
		u_vel_all		= ma.masked_all((len(models), len(time_year)))

	#Save the data for each model
	u_vel_all[model_i]		= u_vel

#-----------------------------------------------------------------------------------------

u_vel_ref	= np.mean(u_vel_all[:, model_year_start:model_year_start+model_year_len], axis = 1)
u_vel_diff	= np.mean(u_vel_all[:, 90+model_year_start:90+model_year_start+model_year_len], axis = 1) - np.mean(u_vel_all[:,  model_year_start:model_year_start+model_year_len], axis = 1)

#-----------------------------------------------------------------------------------------

vel_present	= ma.masked_all((5 * 5))
vel_future	= ma.masked_all((5 * 5))

#-----------------------------------------------------------------------------------------

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		time_rcp, u_vel = ReadinDataMDR(directory_UH_CESM+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/Vertical_wind_shear_MDR_WP.nc', month_start, month_end)

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			vel_present[5 * ensemble_i:5 * (ensemble_i + 1)]	= u_vel

		else:
			#Future ensemble
			vel_future[5 * ensemble_i:5 * (ensemble_i + 1)]	= u_vel

vel_present_ref	= np.mean(vel_present)
vel_future_diff	= np.mean(vel_future) - np.mean(vel_present)

#-----------------------------------------------------------------------------------------

time_ERA5, u_vel_ERA5			= ReadinDataMDR(directory_ERA5+'/Atmosphere/Vertical_wind_shear_MDR_WP_1993-2017.nc', month_start, month_end)
time_rcp_high, u_vel_rcp_high	= ReadinDataMDR(directory_HR_CESM+'/Atmosphere/Vertical_wind_shear_MDR_WP.nc', month_start, month_end)
u_vel_rcp_high_ref				= np.mean(u_vel_rcp_high[model_year_start:model_year_start+model_year_len])
u_vel_rcp_high_diff				= np.mean(u_vel_rcp_high[90+model_year_start:90+model_year_start+model_year_len]) - np.mean(u_vel_rcp_high[model_year_start:model_year_start+model_year_len])


#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

for model_i in range(len(models)):
	#Plot numbers for each model
	if model_i >= 0 and model_i < 10:
		color_label = 'k'
	if model_i >= 10 and model_i < 20:
		color_label = 'r'
	if model_i >= 20 and model_i < 30:
		color_label = 'b'
	if model_i >= 30 and model_i < 40:
		color_label = 'c'
	if model_i >= 40 and model_i < 50:
		color_label = 'forestgreen'
	if model_i >= 50 and model_i < 60:
		color_label = 'orangered'

	ax.text(u_vel_ref[model_i], u_vel_diff[model_i], str(model_i+1), color = color_label, verticalalignment='center', horizontalalignment='center', fontsize=14)

ax.scatter(np.mean(u_vel_ref), np.mean(u_vel_diff), s = 70, color = 'k', label = 'CMIP6 mean')
ax.scatter(vel_present_ref, vel_future_diff, s = 70, color = 'r', label = 'UH-CESM')
ax.scatter(u_vel_rcp_high_ref, u_vel_rcp_high_diff, s = 70, color = 'b', label = 'HR-CESM')
ax.scatter(np.mean(u_vel_ERA5), 0, s = 70, color = 'c', label = 'ERA5')

ax.errorbar(vel_present_ref, vel_future_diff, yerr = np.std(vel_future - vel_present), xerr = np.std(vel_present), color = 'r') 
ax.errorbar(np.mean(u_vel_ref), np.mean(u_vel_diff), yerr = np.std(u_vel_diff), xerr = np.std(u_vel_ref), color = 'k') 
ax.errorbar(np.mean(u_vel_ERA5), 0, xerr = np.std(u_vel_ERA5), color = 'c') 
ax.axvline(x = np.min(u_vel_ERA5), linestyle = '--', color = 'k')
ax.axvline(x = np.max(u_vel_ERA5), linestyle = '--', color = 'k')

ax.set_xlim(6, 14)
ax.set_ylim(-3, 3)
ax.grid()

ax.set_xlabel('Zonal vertical wind shear (m s$^{-1}$)')
ax.set_ylabel('Zonal vertical wind shear difference (m s$^{-1}$)')

ax.legend(loc='upper left', fancybox=True, shadow=False, scatterpoints=1, ncol = 1, prop={'size': 12.5})
ax.set_title('f) MDR Western Pacific, May - November')

show()



