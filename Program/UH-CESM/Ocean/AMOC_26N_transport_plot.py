#Program plots the AMOC strength (26N), including spin-up and HR-CESM

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf
import matplotlib.colors as colors

#Making pathway to folder with all data
directory_UH_CESM 		= '../../../Data/UH-CESM'
directory_HR_CESM 		= '../../../Data/HR-CESM/'

def ReadinData(filename):

	fh = netcdf.Dataset(filename, 'r')

	time		= fh.variables['time'][:]	
	transport	= fh.variables['AMOC'][:]
		
	fh.close()

	return time, transport

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

transport_present	= ma.masked_all((5, 96))
transport_future	= ma.masked_all((5, 96))

#-----------------------------------------------------------------------------------------

#Read in the time series of the HR-CESM
time_HR, transport_HR	= ReadinData(directory_HR_CESM+'Ocean/AMOC_26N_transport_maximum.nc')

for period in ['PRESENT', 'FUTURE']:
	#Loop over both periods
	if period == 'PRESENT':
		ensemble_number	= [1, 2, 3, 4, 5]
		
		#Only get the relevant years for the HR-CESM
		time_start 		= (fabs(time_HR - datetime.datetime(2000, 1, 15).toordinal())).argmin()
		time_end 		= (fabs(time_HR - datetime.datetime(2001, 12, 15).toordinal())).argmin() + 1
		time_HR_1		= time_HR[time_start:time_end]
		transport_HR_1		= transport_HR[time_start:time_end]

		#Get the spin up for the UH-CESM
		time_UH_spin, transport_UH_spin	= ReadinData(directory_UH_CESM+'/Ocean/AMOC_26N_transport_maximum_spin_up_year_2002.nc')

	if period == 'FUTURE':
		ensemble_number			= [6, 7, 8, 9, 10]

		#Only get the relevant years for the HR-CESM
		time_start 		= (fabs(time_HR - datetime.datetime(2090, 1, 15).toordinal())).argmin()
		time_end 		= (fabs(time_HR - datetime.datetime(2091, 12, 15).toordinal())).argmin() + 1
		time_HR_1		= time_HR[time_start:time_end]
		transport_HR_1		= transport_HR[time_start:time_end]

		#Get the spin up for the UH-CESM
		time_UH_spin, transport_UH_spin	= ReadinData(directory_UH_CESM+'/Ocean/AMOC_26N_transport_maximum_spin_up_year_2092.nc')

	for ensemble_i in range(len(ensemble_number)):
		#Loop over each ensemble
		time, transport	= ReadinData(directory_UH_CESM+'_'+str(ensemble_number[ensemble_i]).zfill(3)+'/Ocean/AMOC_26N_transport_maximum.nc')

		time_all	= np.zeros(len(time_HR_1) + len(time_UH_spin) +  len(time))
		transport_all	= np.zeros(len(time_all))

		#Save the corresponding HR-CESM as the first part of the ensemble (for plotting only)
		time_all[:len(time_HR_1)]	= time_HR_1
		transport_all[:len(time_HR_1)]	= transport_HR_1
		
		#Save the corresponding UH-CESM spin-up (for plotting only)
		time_all[len(time_HR_1):len(time_HR_1)+len(time_UH_spin)]	= time_UH_spin
		transport_all[len(time_HR_1):len(time_HR_1)+len(time_UH_spin)]	= transport_UH_spin

		#Save the corresponding ensemble run
		time_all[len(time_HR_1)+len(time_UH_spin):]	= time
		transport_all[len(time_HR_1)+len(time_UH_spin):]	= transport

		#Save the data to general array
		if period == 'PRESENT':
			time_present					= np.copy(time_all)
			transport_present[ensemble_i]	= transport_all

		if period == 'FUTURE':
			time_future						= np.copy(time_all)
			transport_future[ensemble_i]	= transport_all
#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

graph_HR_CESM		=  ax.plot_date(time_HR[:121], transport_HR[:121], color = 'gray', linestyle = '-', marker = None, linewidth = 2.0, label = 'HR-CESM')
graph_UH_CESM_spin	=  ax.plot_date(time_present[23:35], transport_present[0, 23:35], color = 'k', linestyle = '-', marker = None, linewidth = 2.0, label = 'UH-CESM$^{\mathrm{SP}}$')
graph_UH_CESM		=  ax.plot_date(time_present[34:], np.mean(transport_present[:, 34:], axis = 0), color = 'r', linestyle = '-', marker = None, linewidth = 2.0, label = 'UH-CESM$^{\mathrm{PD}}$')


ax.set_xlabel('Model year')
ax.set_ylabel('Atlantic Meridional Overturning Circulation (Sv)')
ax.set_ylim(-2	, 32)
ax.grid()

ax.set_xticks([datetime.datetime(2000, 1, 1).toordinal(),
		datetime.datetime(2001, 1, 1).toordinal(),
		datetime.datetime(2002, 1, 1).toordinal(),
		datetime.datetime(2003, 1, 1).toordinal(), 
		datetime.datetime(2004, 1, 1).toordinal(),
		datetime.datetime(2005, 1, 1).toordinal(), 
		datetime.datetime(2006, 1, 1).toordinal(),
		datetime.datetime(2007, 1, 1).toordinal(),
		datetime.datetime(2008, 1, 1).toordinal(),
		datetime.datetime(2009, 1, 1).toordinal(),
		datetime.datetime(2010, 1, 1).toordinal()])

graphs	      = graph_HR_CESM + graph_UH_CESM_spin + graph_UH_CESM

legend_labels = [l.get_label() for l in graphs]
ax.legend(graphs, legend_labels, loc='lower left', ncol=1, fancybox=True, shadow=False, numpoints = 1)

ax2 = fig.add_axes([0.43, 0.15, 0.43, 0.25])

ax2.plot_date(time_present[23:35], transport_present[0, 23:35] - transport_HR[23:35], color = 'k', linestyle = '-', marker = None, linewidth = 2.0, label = 'UH-CESM$^{\mathrm{SP}}$')
ax2.plot_date(time_present[34:], transport_present[0, 34:] - transport_HR[34:96] , color = 'r', linestyle = '-', marker = None, linewidth = 1.0)
ax2.plot_date(time_present[34:], transport_present[1, 34:] - transport_HR[34:96] , color = 'b', linestyle = '-', marker = None, linewidth = 1.0)
ax2.plot_date(time_present[34:], transport_present[2, 34:] - transport_HR[34:96] , color = 'c', linestyle = '-', marker = None, linewidth = 1.0)
ax2.plot_date(time_present[34:], transport_present[3, 34:] - transport_HR[34:96] , color = 'm', linestyle = '-', marker = None, linewidth = 1.0)
ax2.plot_date(time_present[34:], transport_present[4, 34:] - transport_HR[34:96] , color = 'firebrick', linestyle = '-', marker = None, linewidth = 1.0)

ax2.set_xticks([datetime.datetime(2002, 1, 1).toordinal(),
		datetime.datetime(2004, 1, 1).toordinal(),
		datetime.datetime(2006, 1, 1).toordinal(),
		datetime.datetime(2008, 1, 1).toordinal()])
		
ax2.set_ylim(-10, 10)
ax2.grid()
		
ax.set_title('g) AMOC strength 26$^{\circ}$N, UH-CESM$^{\mathrm{PD}}$')

#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

graph_HR_CESM		=  plot_date(time_HR[1080:1201], transport_HR[1080:1201], color = 'gray', linestyle = '-', marker = None, linewidth = 2.0, label = 'HR-CESM')
graph_UH_CESM_spin	=  plot_date(time_future[23:35], transport_future[0, 23:35], color = 'k', linestyle = '-', marker = None, linewidth = 2.0, label = 'UH-CESM$^{\mathrm{SP}}$')
graph_UH_CESM		=  plot_date(time_future[34:], np.mean(transport_future[:, 34:], axis = 0), color = 'r', linestyle = '-', marker = None, linewidth = 2.0, label = 'UH-CESM$^{\mathrm{F}}$')


ax.set_xlabel('Model year')
ax.set_ylabel('Atlantic Meridional Overturning Circulation (Sv)')
ax.set_ylim(-2, 32)
ax.grid()

ax.set_xticks([datetime.datetime(2090, 1, 1).toordinal(),
		datetime.datetime(2091, 1, 1).toordinal(),
		datetime.datetime(2092, 1, 1).toordinal(),
		datetime.datetime(2093, 1, 1).toordinal(), 
		datetime.datetime(2094, 1, 1).toordinal(),
		datetime.datetime(2095, 1, 1).toordinal(), 
		datetime.datetime(2096, 1, 1).toordinal(),
		datetime.datetime(2097, 1, 1).toordinal(),
		datetime.datetime(2098, 1, 1).toordinal(),
		datetime.datetime(2099, 1, 1).toordinal(),
		datetime.datetime(2100, 1, 1).toordinal()])

graphs	      = graph_HR_CESM + graph_UH_CESM_spin + graph_UH_CESM

legend_labels = [l.get_label() for l in graphs]
ax.legend(graphs, legend_labels, loc='upper left', ncol=1, fancybox=True, shadow=False, numpoints = 1)

ax2 = fig.add_axes([0.43, 0.62, 0.43, 0.25])

ax2.plot_date(time_future[23:35], transport_future[0, 23:35] - transport_HR[1103:1115], color = 'k', linestyle = '-', marker = None, linewidth = 2.0, label = 'UH-CESM$^{\mathrm{SP}}$')
ax2.plot_date(time_future[34:], transport_future[0, 34:] - transport_HR[1114:1176] , color = 'r', linestyle = '-', marker = None, linewidth = 1.0)
ax2.plot_date(time_future[34:], transport_future[1, 34:] - transport_HR[1114:1176] , color = 'b', linestyle = '-', marker = None, linewidth = 1.0)
ax2.plot_date(time_future[34:], transport_future[2, 34:] - transport_HR[1114:1176] , color = 'c', linestyle = '-', marker = None, linewidth = 1.0)
ax2.plot_date(time_future[34:], transport_future[3, 34:] - transport_HR[1114:1176] , color = 'm', linestyle = '-', marker = None, linewidth = 1.0)
ax2.plot_date(time_future[34:], transport_future[4, 34:] - transport_HR[1114:1176] , color = 'firebrick', linestyle = '-', marker = None, linewidth = 1.0)

ax2.set_xticks([datetime.datetime(2092, 1, 1).toordinal(),
		datetime.datetime(2094, 1, 1).toordinal(),
		datetime.datetime(2096, 1, 1).toordinal(),
		datetime.datetime(2098, 1, 1).toordinal()])
		
ax2.set_ylim(-10, 10)
ax2.grid()

ax.set_title('h) AMOC strength 26$^{\circ}$N, UH-CESM$^{\mathrm{F}}$')

show()
