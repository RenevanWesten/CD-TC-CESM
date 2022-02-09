#Plots the TCs genesis month

from pylab import *
import numpy
import datetime
import time
import glob, os
import math
import netCDF4 as netcdf
import matplotlib.colors as colors
from scipy import stats
from mpl_toolkits.basemap import Basemap

#Making pathway to folder with all data
directory 		= '../../../Data/UH-CESM'

def BasinCount(track_all):
	"""Returns the genesis of the tracks per basin"""

	#First retain the amount of years for all the tracks 
	year_track_start	= datetime.date.fromordinal(int(track_all[0, 0, 0])).year
	year_track_end		= datetime.date.fromordinal(int(track_all[-1, 0, 0])).year
	number_years		= year_track_end - year_track_start + 1

	#Empty array for each year and month for all tracks
	WP_gen			= []

	#-----------------------------------------------------------------------------------------

	WP_lon      = [100., 100., 180., 180., 100.]
	WP_lat      = [0, 60., 60., 0., 0.]

	#Re-arrange the coordinates of the corners of domain into single lists
	points_WP	= Points(WP_lon, WP_lat)

	#-----------------------------------------------------------------------------------------

	for track_i in range(len(track_all)):
		#Loop over each track
		track		= track_all[track_i]
		lon_genesis	= track[0, 1]
		lat_genesis	= track[0, 2]

		if Inside_polygon(lon_genesis, lat_genesis, points_WP) == True:
			#North Atlantic region
			WP_gen.append([lon_genesis, lat_genesis])
			continue
		
	return WP_gen

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

#-----------------------------------------------------------------------------------------
#--------------------------------MAIN SCRIPT STARTS HERE----------------------------------
#-----------------------------------------------------------------------------------------

grid_size	= 5.0
lon_start	= 80
lon_end		= 180.0
lat_start	= -5.0
lat_end		= 40


#Generate the lon/lat points for the tracks
lon				= np.arange(lon_start - grid_size / 2.0, lon_end + grid_size / 2.0 + 0.01, grid_size)
lat				= np.arange(lat_start - grid_size / 2.0, lat_end + grid_size / 2.0 + 0.01, grid_size)
field_present	= np.zeros((len(lat), len(lon)))
field_future	= np.zeros((len(lat), len(lon)))

#-----------------------------------------------------------------------------------------

for ensemble_i in range(1, 11):
	#Add genesis latitidue for the North Atlantic
	fh = netcdf.Dataset(directory+'_'+str(ensemble_i).zfill(3)+'/Atmosphere/TC_tracker.nc', 'r')

	#Writing data to correct variable	
	track_all	= fh.variables['TC_tracks'][:]

	fh.close()

	NA_gen	= BasinCount(track_all)

	for TC_i in range(len(NA_gen)):
		#Add to general array

		lon_TC, lat_TC	= NA_gen[TC_i][0], NA_gen[TC_i][1]
		lon_index	= (np.fabs(lon - lon_TC)).argmin()
		lat_index	= (np.fabs(lat - lat_TC)).argmin()

		if ensemble_i <= 5:
			field_present[lat_index, lon_index] += 1.0

		if ensemble_i >= 6:
			field_future[lat_index, lon_index] += 1.0

#Normalise
field_present	= field_present / np.sum(field_present)
field_future	= field_future / np.sum(field_future)

#-----------------------------------------------------------------------------------------

cNorm  		= colors.Normalize(vmin=0, vmax= 0.15) 			#Probablility
scalarMap 	= cm.ScalarMappable(norm=cNorm, cmap='Spectral_r') 	#Using colormap

#-----------------------------------------------------------------------------------------

fig, ax	= subplots()	
x, y 	= np.meshgrid(lon, lat)
levels 	= np.arange(0, 0.16, 0.01)
cs 	= contourf(x,y, field_present, levels, extend = 'max', cmap='Spectral_r', norm=cNorm)

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

deviation 	= grid_size / 2.0 - 0.2

for lat_i in range(len(lat)):
	for lon_i in range(len(lon)):
		if field_present[lat_i, lon_i] == 0:
			continue

		x1,y1 = m(lon[lon_i] - deviation, lat[lat_i] - deviation) #Bottom left
		x2,y2 = m(lon[lon_i] - deviation, lat[lat_i] + deviation) #Top left
		x3,y3 = m(lon[lon_i] + deviation, lat[lat_i] + deviation) #Top right
		x4,y4 = m(lon[lon_i] + deviation, lat[lat_i] - deviation) #Bottom right
		color_count =  scalarMap.to_rgba(field_present[lat_i, lon_i])
		p = Polygon([(x1,y1),(x2,y2),(x3,y3),(x4,y4)],facecolor=color_count, linewidth=0) 
		plt.gca().add_patch(p) 
		
		
cbar = m.colorbar(cs,location='right',pad="4%", cmap = scalarMap, norm = cNorm, ticks = np.arange(0, 0.16, 0.05))
cbar.set_label('TC genesis PDF')
ax.set_title('b) Western Pacific, UH-CESM$^{\mathrm{PD}}$')

#-----------------------------------------------------------------------------------------

fig, ax	= subplots(figsize = (8, 6))

m = Basemap(projection = 'merc', llcrnrlat=-3, urcrnrlat=61, llcrnrlon=90, urcrnrlon=200.0001, resolution='i') 
m.drawcoastlines()

par = m.drawparallels(np.arange(-80,80,10),labels=[1,0,0,0])
mer = m.drawmeridians(np.arange(0,360.1,20),labels=[0,0,0,1])

deviation 	= grid_size / 2.0 - 0.2

for lat_i in range(len(lat)):
	for lon_i in range(len(lon)):
		if field_future[lat_i, lon_i] == 0:
			continue

		x1,y1 = m(lon[lon_i] - deviation, lat[lat_i] - deviation) #Bottom left
		x2,y2 = m(lon[lon_i] - deviation, lat[lat_i] + deviation) #Top left
		x3,y3 = m(lon[lon_i] + deviation, lat[lat_i] + deviation) #Top right
		x4,y4 = m(lon[lon_i] + deviation, lat[lat_i] - deviation) #Bottom right
		color_count =  scalarMap.to_rgba(field_future[lat_i, lon_i])
		p = Polygon([(x1,y1),(x2,y2),(x3,y3),(x4,y4)],facecolor=color_count, linewidth=0) 
		plt.gca().add_patch(p) 
		
		
cbar = m.colorbar(cs,location='right',pad="4%", cmap = scalarMap, norm = cNorm, ticks = np.arange(0, 0.16, 0.05))
cbar.set_label('TC genesis PDF')
ax.set_title('d) Western Pacific, UH-CESM$^{\mathrm{F}}$')

show()

