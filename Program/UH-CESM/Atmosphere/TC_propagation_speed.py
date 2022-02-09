#Plots the TC propagation speed

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

def BasinCount(track_all, basin):
	"""Returns the genesis of the tracks per basin"""

	#Empty array, 0 = Else, 1 = NA genesis basin
	TC_gen			= np.zeros(len(track_all))

	#-----------------------------------------------------------------------------------------

	if basin == 'NA':
		lon_domain	= [260, 360, 360, 290, 290, 275, 275, 270, 270, 260, 260]
		lat_domain	= [60, 60, 0, 0, 8, 8, 14, 14, 17.5, 17.5, 60]

	if basin == 'WP':
		lon_domain	= [100., 100., 180., 180., 100.]
		lat_domain	= [0, 60., 60., 0., 0.]

	#Re-arrange the coordinates of the corners of domain into single lists
	points		= Points(lon_domain, lat_domain)

	#-----------------------------------------------------------------------------------------

	for track_i in range(len(track_all)):
		#Loop over each track
		track		= track_all[track_i]
		lon_genesis	= track[0, 1]
		lat_genesis	= track[0, 2]

		if Inside_polygon(lon_genesis, lat_genesis, points) == True:
			#North Atlantic region
			TC_gen[track_i]	= 1.0

	return TC_gen


def Inside_polygon(x_point, y_point, corners):
    """Return True if a coordinate (x, y) is inside a polygon defined by
    a list of verticies corners = [(x1, y1), (x2, x2), ... , (xN, yN)]. Note that you do NOT have
    to insert the first vertices as the last element"""

    n = len(corners) #Number of points of polygon
    inside = False  #Assume that point is not in polygon
    p1x, p1y = corners[0] #Take the first points of polygon
    p1x, p1y = float(p1x), float(p1y) #Make floats, otherwise program does not work (if there are any integers as input)
    
    for ver_i in range(1, n + 1):     #Extra number, to make sure that the first one is also taken into account (closed loop)
        p2x, p2y = corners[ver_i % n] #Read out the next point, and in the end also the first point again
        if y_point > min(p1y, p2y):
            if y_point <= max(p1y, p2y):
                if x_point <= max(p1x, p2x):
                    if p1y != p2y:
                    	#The point should be left above a vertex, but in between the y values of the vertices
                    	#This can be checked while determining the intersection of two lines
                    	#1) A horizontal line through the point of interest, so y = y_point
                        #2) The line of a single vertex
                        x_intersection = (y_point - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x_point <= x_intersection:
                    	#This implies, if the point is indeed left (above) of the vertex, say that point is in polygon
                    	#However, it might be possible that the polygon has a particular shape,
                    	#So a second encounter in this line says that it is false again.
                        inside = not inside
        p1x, p1y = p2x, p2y #Save the old one as the first one, and continue
    return inside

def Points(lon_domain, lat_domain):
	"""Returns the coordinates of the domain, which are used to determine the mask of the different ocean basins"""

	points = []

	for point_i in range(len(lon_domain) - 1): #Do not include any double elements
		points.append((float(lon_domain[point_i]), float(lat_domain[point_i])))

	return points

def Distance(lon_1, lat_1, lon_2, lat_2):
	"""Returns distance (m) of two points located at the globe coordinates need input in degrees"""

	#Convert to radians
	lon_1, lat_1, lon_2, lat_2 = map(radians, [lon_1, lat_1, lon_2, lat_2]) 

	#Haversine formula 
	d_lon 	= lon_2 - lon_1 
	d_lat 	= lat_2 - lat_1 
	a 	= math.sin(d_lat/2.0)**2 + math.cos(lat_1) * math.cos(lat_2) * math.sin(d_lon/2.0)**2
	c 	= 2.0 * math.asin(sqrt(a)) 
	r 	= 6371000.0 # Radius of earth in meters
	
	return c * r #Distance between two points in meter

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------


TC_speed_present	= []
TC_speed_future		= []
TC_NA_speed_present	= []
TC_NA_speed_future	= []
TC_WP_speed_present	= []
TC_WP_speed_future	= []

for ensemble_i in range(1, 11):
	#Add genesis latitidue for the North Atlantic
	print ensemble_i
	fh = netcdf.Dataset(directory+'_'+str(ensemble_i).zfill(3)+'/Atmosphere/TC_tracker.nc', 'r')

	#Writing data to correct variable	
	track_all	= fh.variables['TC_tracks'][:]

	fh.close()

	NA_gen	= BasinCount(track_all, 'NA')
	WP_gen	= BasinCount(track_all, 'WP')

	for track_i in range(len(track_all)):
		#Add to general array

		lon_TC, lat_TC	= track_all[track_i, :, 1], track_all[track_i, :, 2]
		mask_index		= np.where(lon_TC.mask == True)[0][0]
		lon_TC, lat_TC	= lon_TC[:mask_index], lat_TC[:mask_index]

		for time_i in range(1, len(lat_TC)):
			#Determine the distance between two points (in km)
			TC_distance	=  Distance(lon_TC[time_i], lat_TC[time_i], lon_TC[time_i - 1], lat_TC[time_i - 1]) / 1000.0

			#Save the propagation speed (in km/h, 3 hours per time step, /3)
			if ensemble_i <= 5:
				TC_speed_present.append(TC_distance / 3.0)

				if NA_gen[track_i] == 1.0:
					TC_NA_speed_present.append(TC_distance / 3.0)

				if WP_gen[track_i] == 1.0:
					TC_WP_speed_present.append(TC_distance / 3.0)
					
			if ensemble_i >= 6:
				TC_speed_future.append(TC_distance / 3.0)

				if NA_gen[track_i] == 1.0:
					TC_NA_speed_future.append(TC_distance / 3.0)

				if WP_gen[track_i] == 1.0:
					TC_WP_speed_future.append(TC_distance / 3.0)
					
#-----------------------------------------------------------------------------------------
bins				= 10.0
speed_bins			= np.arange(0, 200.1, bins)
speeds				= np.arange(speed_bins[0] + bins / 2.0, speed_bins[-1], bins)
speed_present		= np.zeros((len(speed_bins)))
speed_future		= np.zeros((len(speed_bins)))
speed_NA_present	= np.zeros((len(speed_bins)))
speed_NA_future		= np.zeros((len(speed_bins)))
speed_WP_present	= np.zeros((len(speed_bins)))
speed_WP_future		= np.zeros((len(speed_bins)))

for speed_i in range(len(TC_speed_present)):
	#Get the speed boundaries
	index				= np.where(TC_speed_present[speed_i] >= speed_bins)[0][-1]
	speed_present[index] 		+= 1.0

for speed_i in range(len(TC_NA_speed_present)):
	#Get the speed boundaries
	index				= np.where(TC_NA_speed_present[speed_i] >= speed_bins)[0][-1]
	speed_NA_present[index] 	+= 1.0
	
for speed_i in range(len(TC_WP_speed_present)):
	#Get the speed boundaries
	index				= np.where(TC_WP_speed_present[speed_i] >= speed_bins)[0][-1]
	speed_WP_present[index] 	+= 1.0
	
for speed_i in range(len(TC_speed_future)):
	#Get the speed boundaries
	index				= np.where(TC_speed_future[speed_i] >= speed_bins)[0][-1]
	speed_future[index] 		+= 1.0

for speed_i in range(len(TC_NA_speed_future)):
	#Get the speed boundaries
	index				= np.where(TC_NA_speed_future[speed_i] >= speed_bins)[0][-1]
	speed_NA_future[index] 		+= 1.0

for speed_i in range(len(TC_WP_speed_future)):
	#Get the speed boundaries
	index				= np.where(TC_WP_speed_future[speed_i] >= speed_bins)[0][-1]
	speed_WP_future[index] 		+= 1.0
	
print np.mean(TC_speed_present), np.mean(TC_speed_future)
print np.mean(TC_NA_speed_present), np.mean(TC_NA_speed_future)
print np.mean(TC_WP_speed_present), np.mean(TC_WP_speed_future)

fig, ax	= subplots()

graph_global	= ax.plot(speeds, speed_present[:-1] / np.sum(speed_present), '-k', linewidth = 2.0, label = 'Global')
graph_NA	= ax.plot(speeds, speed_NA_present[:-1] / np.sum(speed_NA_present), '-r', linewidth = 2.0, label = 'North Atlantic')
graph_WP	= ax.plot(speeds, speed_WP_present[:-1] / np.sum(speed_WP_present), '-b', linewidth = 2.0, label = 'Western Pacific')

ax.axvline(x = np.mean(TC_speed_present), linestyle = '--', linewidth = 2.0, color = 'k')
ax.axvline(x = np.mean(TC_NA_speed_present), linestyle = '--', linewidth = 2.0, color = 'r')
ax.axvline(x = np.mean(TC_WP_speed_present), linestyle = '--', linewidth = 2.0, color = 'b')

ax.set_xlim(0, 100)
ax.grid()
ax.set_xlabel('Propagation speed (km h$^{-1}$)')
ax.set_ylabel('PDF')
ax.set_title('a) Propagation speed, UH-CESM$^{\mathrm{PD}}$')

ax.text(np.mean(TC_speed_present) - 1.5, 0.01, str(round(np.mean(TC_speed_present), 1)), verticalalignment='bottom', horizontalalignment='right', color = 'k', fontsize=14)
ax.text(np.mean(TC_NA_speed_present) + 1, 0.01, str(round(np.mean(TC_NA_speed_present), 1)), verticalalignment='bottom', horizontalalignment='left', color = 'r', fontsize=14)
ax.text(np.mean(TC_speed_present) - 1.5, 0.03, str(round(np.mean(TC_WP_speed_present), 1)), verticalalignment='bottom', horizontalalignment='right', color = 'b', fontsize=14)


graphs		= graph_global + graph_NA + graph_WP
legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper right', ncol=1, numpoints = 1)

#-----------------------------------------------------------------------------------------

fig, ax	= subplots()

graph_global	= ax.plot(speeds, speed_future[:-1] / np.sum(speed_future), '-k', linewidth = 2.0, label = 'Global')
graph_NA	= ax.plot(speeds, speed_NA_future[:-1] / np.sum(speed_NA_future), '-r', linewidth = 2.0, label = 'North Atlantic')
graph_WP	= ax.plot(speeds, speed_WP_future[:-1] / np.sum(speed_WP_future), '-b', linewidth = 2.0, label = 'Western Pacific')


ax.axvline(x = np.mean(TC_speed_future), linestyle = '--', linewidth = 2.0, color = 'k')
ax.axvline(x = np.mean(TC_NA_speed_future), linestyle = '--', linewidth = 2.0, color = 'r')
ax.axvline(x = np.mean(TC_WP_speed_future), linestyle = '--', linewidth = 2.0, color = 'b')

ax.set_xlim(0, 100)
ax.grid()
ax.set_xlabel('Propagation speed (km h$^{-1}$)')
ax.set_ylabel('PDF')
ax.set_title('b) Propagation speed, UH-CESM$^{\mathrm{F}}$')

ax.text(np.mean(TC_speed_future) - 1.5, 0.01, str(round(np.mean(TC_speed_future), 1)), verticalalignment='bottom', horizontalalignment='right', color = 'k', fontsize=14)
ax.text(np.mean(TC_NA_speed_future) + 1, 0.01, str(round(np.mean(TC_NA_speed_future), 1)), verticalalignment='bottom', horizontalalignment='left', color = 'r', fontsize=14)
ax.text(np.mean(TC_speed_future) - 1.5, 0.03, str(round(np.mean(TC_WP_speed_future), 1)), verticalalignment='bottom', horizontalalignment='right', color = 'b', fontsize=14)


graphs		= graph_global + graph_NA + graph_WP
legend_labels = [l.get_label() for l in graphs]
legend_1      = ax.legend(graphs, legend_labels, loc = 'upper right', ncol=1, numpoints = 1)

show()
