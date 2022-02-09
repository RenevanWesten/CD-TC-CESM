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
directory 		= '../../../Data/UH-CESM'
directory_ERA5	= '../../../Data/ERA5/'

month_days		= np.asarray([31., 28., 31., 30., 31., 30., 31., 31., 30., 31., 30., 31.])

def Climatology(data):
	"""Determines the climatology"""

	time_month	= np.arange(14) - 0.5
	data_month	= np.zeros(14)
	data_month_5	= np.zeros(14)
	data_month_25	= np.zeros(14)
	data_month_75	= np.zeros(14)
	data_month_95	= np.zeros(14)

	for month_i in range(12):
		#Loop over each month
		index				= np.arange(month_i, len(data), 12)
		data_month[month_i+1]		= np.mean(data[index])

		data_month_5[month_i+1]		= np.percentile(data[index], 5)
		data_month_25[month_i+1]	= np.percentile(data[index], 25)
		data_month_75[month_i+1]	= np.percentile(data[index], 75)
		data_month_95[month_i+1]	= np.percentile(data[index], 95)

	#Add january climatology to end (for plotting)
	data_month[0]		= data_month[12]
	data_month_5[0]		= data_month_5[12]
	data_month_25[0]	= data_month_25[12]
	data_month_75[0]	= data_month_75[12]
	data_month_95[0]	= data_month_95[12]
	data_month[13]		= data_month[1]
	data_month_5[13]	= data_month_5[1]
	data_month_25[13]	= data_month_25[1]
	data_month_75[13]	= data_month_75[1]
	data_month_95[13]	= data_month_95[1]

	return time_month, data_month, data_month_5, data_month_25, data_month_75, data_month_95

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------
vel_present	= ma.masked_all((5 * 60))
vel_future	= ma.masked_all((5 * 60))

#-----------------------------------------------------------------------------------------

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]

	if period == 'FUTURE':
		ensemble_number	= [6, 7, 8, 9, 10]

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		fh = netcdf.Dataset(directory+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Atmosphere/Vertical_wind_shear_MDR_NA.nc', 'r')

		vel	= fh.variables['UVEL'][:]

		fh.close()

		if ensemble_number[ensemble_i] <= 5:
			#Present-day ensemble
			vel_present[60 * ensemble_i:60 * (ensemble_i + 1)]	= vel

		else:
			#Future ensemble
			vel_future[60 * ensemble_i:60 * (ensemble_i + 1)]	= vel

#-----------------------------------------------------------------------------------------
month, present_mean, present_5, present_25, present_75, present_95 = Climatology(vel_present)
month, future_mean, future_5, future_25, future_75, future_95 = Climatology(vel_future)

#-----------------------------------------------------------------------------------------
fh = netcdf.Dataset(directory_ERA5+'/Atmosphere/Vertical_wind_shear_MDR_NA_1993-2017.nc', 'r')

vel_ERA5	= fh.variables['UVEL'][:]

fh.close()

month, ERA5_mean, ERA5_5, ERA5_25, ERA5_75, ERA5_95 = Climatology(vel_ERA5)

#-----------------------------------------------------------------------------------------

#Determine RMS over given months
month_start		= 6
month_end		= 11

#Take the relevant months (note that we add 2 months at the start and end of array
present_diff	= present_mean[month_start:month_end+1] - ERA5_mean[month_start:month_end+1]
future_diff		= future_mean[month_start:month_end+1] - ERA5_mean[month_start:month_end+1]

days			= month_days[month_start-1:month_end]
days			= days / np.sum(days)
RMS_present_1	= np.sqrt(np.sum(days * present_diff**2.0))
RMS_future_1	= np.sqrt(np.sum(days * future_diff**2.0))


#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

ax.fill_between(month, ERA5_5, ERA5_95, color = 'k', alpha = 0.20)
ax.fill_between(month, ERA5_25, ERA5_75, color = 'k', alpha = 0.20)
ax.fill_between(month, present_5, present_95, color = 'b', alpha = 0.20)
ax.fill_between(month, present_25, present_75, color = 'b', alpha = 0.20)
ax.fill_between(month, future_5, future_95, color = 'r', alpha = 0.20)
ax.fill_between(month, future_25, future_75, color = 'r', alpha = 0.20)

graph_mean_ERA5	= ax.plot(month, ERA5_mean, '-k', linewidth = 2.0, label = 'ERA5 (1993 - 2017)')
graph_mean_PD	= ax.plot(month, present_mean, '-b', linewidth = 2.0, label = 'UH-CESM$^{\mathrm{PD}}$')
graph_mean_F	= ax.plot(month, future_mean, '-r', linewidth = 2.0, label = 'UH-CESM$^{\mathrm{F}}$')

ax.grid()

ax.set_xlabel('Month')
ax.set_ylabel('Zonal vertical wind shear (m s$^{-1}$)')
ax.set_ylim(-0.3, 50)

graphs	      = graph_mean_ERA5 + graph_mean_PD + graph_mean_F #+ graph_mean_PD_2 + graph_mean_F_2
legend_labels = [l.get_label() for l in graphs]
legend        = ax.legend(graphs, legend_labels, loc = 'lower left', ncol=1, fancybox=True, numpoints = 1)

ax2 = fig.add_axes([0.55, 0.6, 0.2, 0.2])

ax2.set_ylim(-0.1, 1.1)
ax2.set_xlim(0, 2.6)
ax2.axis('off')

x_legend	= np.arange(1, 2.51, 0.1)
ax2.fill_between(x_legend, 0, 1, color ='k', alpha = 0.2)
ax2.fill_between(x_legend, 0.25, 0.75, color = 'k', alpha = 0.2)
ax2.plot(x_legend, 0.5 + np.zeros(len(x_legend)), linestyle = '-', color = 'k', linewidth = 3.0)

ax2.text(0.2, 0,'5$\%$', color ='k',fontsize=15,ha='right',va='center')
ax2.plot([0.22, 1], [0, 0], '--k', linewidth = 0.5)

ax2.text(0.4, 0.25, '25$\%$', color ='k',fontsize=15,ha='right',va='center')
ax2.plot([0.42, 1], [0.25, 0.25], '--k', linewidth = 0.5)

ax2.text(0.6, 0.5,'Mean', color ='k',fontsize=15,ha='right',va='center')
ax2.plot([0.62, 1], [0.5, 0.5], '--k', linewidth = 0.5)

ax2.text(0.4, 0.75, '75$\%$', color ='k',fontsize=15,ha='right',va='center')
ax2.plot([0.42, 1], [0.75, 0.75], '--k', linewidth = 0.5)

ax2.text(0.2, 1,'95$\%$', color ='k',fontsize=15,ha='right',va='center')
ax2.plot([0.22, 1], [1, 1], '--k', linewidth = 0.5)



ax.set_xticks(np.arange(0, 13))
ax.set_xlim(0, 12)

labels = [item.get_text() for item in ax.get_xticklabels()]
labels[0] = 'Jan'
labels[1] = 'Feb'
labels[2] = 'Mar'
labels[3] = 'Apr'
labels[4] = 'May'
labels[5] = 'Jun'
labels[6] = 'Jul'
labels[7] = 'Aug'
labels[8] = 'Sep'
labels[9] = 'Oct'
labels[10] = 'Nov'
labels[11] = 'Dec'
labels[12] = 'Jan'
ax.set_xticklabels(labels)

ax.set_title('e) Zonal vertical wind shear climatology')

#-----------------------------------------------------------------------------------------
fig, ax	= subplots()

graph_mean_PD	= ax.plot(month, present_mean - ERA5_mean, '-b', linewidth = 2.0, label = 'UH-CESM$^{\mathrm{PD}}$')
graph_mean_F	= ax.plot(month, future_mean - ERA5_mean, '-r', linewidth = 2.0, label = 'UH-CESM$^{\mathrm{F}}$')

ax.grid()

ax.set_xlabel('Month')
ax.set_ylabel('Zonal vertical wind shear difference (m s$^{-1}$)')
ax.set_ylim(-10, 10)

graphs	      = graph_mean_PD + graph_mean_F	
legend_labels = [l.get_label() for l in graphs]
legend        = ax.legend(graphs, legend_labels, loc = 'lower left', ncol=1, fancybox=True, numpoints = 1)


plot([5.5, 10.5], [-4.5, -4.5], '-k', linewidth = 2.0)
plot([5.5, 5.5], [-5, -4], '-k', linewidth = 2.0)
plot([10.5, 10.5], [-5, -4], '-k', linewidth = 2.0)
ax.text(5.4, -4.5, 'June', verticalalignment='center', horizontalalignment='right', fontsize=10)
ax.text(10.6, -4.5, 'November', verticalalignment='center', horizontalalignment='left', fontsize=10)
ax.text(6, -6, 'UH-CESM$^{\mathrm{PD}}$ = '+str(round(RMS_present_1, 2)), verticalalignment='bottom', horizontalalignment='left', fontsize=14)
ax.text(6, -7, 'UH-CESM$^{\mathrm{F}}$   = '+str(round(RMS_future_1, 2)), verticalalignment='bottom', horizontalalignment='left', fontsize=14)

ax.set_xticks(np.arange(0, 13))
ax.set_xlim(0, 12)

labels = [item.get_text() for item in ax.get_xticklabels()]
labels[0] = 'Jan'
labels[1] = 'Feb'
labels[2] = 'Mar'
labels[3] = 'Apr'
labels[4] = 'May'
labels[5] = 'Jun'
labels[6] = 'Jul'
labels[7] = 'Aug'
labels[8] = 'Sep'
labels[9] = 'Oct'
labels[10] = 'Nov'
labels[11] = 'Dec'
labels[12] = 'Jan'
ax.set_xticklabels(labels)

ax.set_title('g) Zonal vertical wind shear climatology difference')

show()

