#Program plots the (zonal) vertical wind shear

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf
import matplotlib.colors as colors
from scipy import stats
import matplotlib.tri as tri
from mpl_toolkits.basemap import Basemap

#Making pathway to folder with all data
directory 				= '../../../Data/CMIP6/'
directory_ERA5			= '../../../Data/ERA5/'

def ReadinData(filename):
	"""Reads-in the data"""

	TEMP_data 	= netcdf.Dataset(filename, 'r')

	#Writing data to correct variable	
	lon		= TEMP_data.variables['lon'][:]  
	lat		= TEMP_data.variables['lat'][:]     	   	
	u_vel	= TEMP_data.variables['UVEL'][:] 	

	TEMP_data.close()
	
	return lon, lat, u_vel

def MaskedFilled(lon, lat, field):
	"""Interpolate the masked elements for interpolation for Antarctica"""

	try:
		#Get the indices for all masked elements
		mask_index = np.where(field.mask == True)
	except:
		return field

	for mask_i in range(len(mask_index[0])):
		#Get the lon/lat index for masked element
		lat_index, lon_index	= mask_index[0][mask_i], mask_index[1][mask_i]

		lat_min_index	= lat_index - 1
		lat_max_index	= lat_index + 2
		lon_min_index	= lon_index - 1
		lon_max_index	= lon_index + 2

		if lat_min_index < 0:
			lat_min_index = 0
		if lon_min_index < 0:
			lon_min_index = 0

		#Get all the points around masked element
		field_mask	= field[lat_min_index:lat_max_index, lon_min_index:lon_max_index]

		field[lat_index, lon_index]	= np.mean(field_mask)

	return field

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

month_start		= 5 	#1 = January, 2 = February, 3 = March, ..., 13 = January (+ 1), ...
month_end		= 11	#12 = December, 13 = January (+ 1), 14 = February (+ 1), ...

year_start_ERA	= 1993
year_end_ERA	= 2017
#-----------------------------------------------------------------------------------------
	
#Get the model names and path
models = glob.glob(directory+'*')
models.sort()

for model_i in range(len(models)):
	#Only retain the model names
	models[model_i]	= models[model_i][len(directory):]

print len(models)

#-----------------------------------------------------------------------------------------

fh = netcdf.Dataset(directory_ERA5+'Atmosphere/Vertical_wind_shear_WP_month_'+str(month_start)+'-'+str(month_end)+'_'+str(year_start_ERA)+'-'+str(year_end_ERA)+'.nc', 'r')

lon_ERA	= fh.variables['lon'][:]
lat_ERA	= fh.variables['lat'][:]
vel_ERA	= fh.variables['UVEL'][:]			

fh.close()

vel_present_all	= ma.masked_all((len(models), len(lat_ERA), len(lon_ERA)))
vel_future_all	= ma.masked_all((len(models), len(lat_ERA), len(lon_ERA)))

#-----------------------------------------------------------------------------------------

for period in ['PRESENT', 'FUTURE']:

	if period == 'PRESENT':
		year_start		= 4	#Start at 2003 (model year 4) and 2093 (model year 2094)
		year_end		= 8	#Add number of year from start

	if period == 'FUTURE':
		year_start		= 94	#Start at 2003 (model year 4) and 2093 (model year 2094)
		year_end		= 98	#Add number of year from start
	
	for model_i in range(len(models)):
		#For each model get the all the files
		print models[model_i]
		filename_UVEL		= directory+models[model_i]+'/Atmosphere/Vertical_wind_shear_WP_month_'+str(month_start)+'-'+str(month_end)+'_year_'+str(year_start).zfill(3)+'-'+str(year_end).zfill(3)+'.nc'

		#Get data and fill field for interpolation
		lon, lat, u_vel		= ReadinData(filename_UVEL)
		u_vel				= MaskedFilled(lon, lat, u_vel)

		#Unravel the field
		lon, lat	= np.meshgrid(lon, lat)
		lon			= lon.ravel()
		lat			= lat.ravel()
		u_vel		= u_vel.ravel()

		#Interpolate data to rectangular grid of the ERA5 grid
		triang 		= tri.Triangulation(lon, lat)
		x, y 		= np.meshgrid(lon_ERA, lat_ERA)

		#Interpolate each field to ERA5 grid and mask the land
		vel_interpolate 	= tri.LinearTriInterpolator(triang, u_vel)
		vel_interpolate 	= vel_interpolate(x, y)
		vel_interpolate		= ma.masked_array(vel_interpolate, mask = vel_ERA.mask)
		
		if period == 'PRESENT':
			vel_present_all[model_i]	= vel_interpolate

		if period == 'FUTURE':
			vel_future_all[model_i]	= vel_interpolate
			
#-----------------------------------------------------------------------------------------

fh = netcdf.Dataset(directory_ERA5+'Atmosphere/Vertical_wind_shear_WP_month_'+str(month_start)+'-'+str(month_end)+'_'+str(year_start_ERA)+'-'+str(year_end_ERA)+'.nc', 'r')

lon = fh.variables['lon'][:]
lat	= fh.variables['lat'][:]
	
fh.close()

#Take the ensemble mean
vel_present_plot	= np.mean(vel_present_all, axis = 0)
vel_future_plot		= np.mean(vel_future_all, axis = 0)
vel_plot			= vel_future_plot - vel_present_plot

#Difference per model
vel_diff		= vel_future_all - vel_present_all
sign_model		= ma.masked_all((len(lat), len(lon)))

for lat_i in range(len(lat)):
	for lon_i in range(len(lon)):

		if vel_present_all[0, lat_i, lon_i] is ma.masked:
			continue

		num_models 				= np.where(np.sign(vel_diff[:, lat_i, lon_i]) == np.sign(vel_plot[lat_i, lon_i]))[0]
		sign_model[lat_i, lon_i]= np.float(len(num_models)) / len(vel_present_all) * 100.0

#-----------------------------------------------------------------------------------------


fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])


#Set mask
x_field	= [89, 200]
y_field	= [-5, 65]
x_field, y_field	= m(x_field, y_field)
ax.fill_between(x_field, y_field[0], y_field[-1], facecolor='#cc9966')


x, y	= np.meshgrid(lon, lat)
x, y	= m(x, y)
CS	= contourf(x, y, vel_future_plot - vel_present_plot, levels = np.arange(-5, 5.1, 0.1), extend = 'both', cmap = 'RdBu_r')
cbar	= m.colorbar(CS, ticks = np.arange(-5, 5.1, 1))
cbar.set_label('Zonal vertical wind shear difference (m s$^{-1}$)')
CS_2	= m.contour(x, y, vel_present_plot, levels = [12.5], colors = 'gray', linewidths = 2.5, label = '10')
CS_3	= m.contour(x, y, vel_future_plot, levels = [12.5], colors = 'k', linewidths = 2.5, label = '10')

ax.set_title('d) Zonal vertical wind shear, $\Delta$CMIP6, May - November')

CS1	= m.plot([-1, -1], [-1, -1], linestyle = '-', color = 'gray', linewidth = 2.5, label = '12.5 m s$^{-1}$ (4-8)')
CS2	= m.plot([-1, -1], [-1, -1], '-k', linewidth = 2.5, label = '12.5 m s$^{-1}$ (94-98)')

graphs	= CS1 + CS2

legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper left', ncol=1, numpoints = 1)

for lat_i in range(0, len(lat), 8):
	for lon_i in range(0, len(lon), 8):

		if sign_model[lat_i, lon_i] >= 75.0:

			x, y = m(lon[lon_i], lat[lat_i])
			m.scatter(x, y, marker = 'o', edgecolor = 'k' , s = 10, facecolors='none')

show()



