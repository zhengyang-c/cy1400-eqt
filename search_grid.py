import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import argparse
import datetime
import os
import netCDF4
from plot_gridsearch import plotter
import subprocess

# first generate travel time table
# devise a scheme for easy lookup: dictionaries are expensive...
# is it faster? it's like a 0.3MB textfile....

# i'm not sure which would be faster / i could test it?


# scheme:
# store everything in a 2D numpy array?
# 
# one table for P arrival, one table for S arrival?


# interpolation? estimate local derivative? or just round
# try both why not like just call a function


def parse_station_info(input_file):
	# 'reusing functions is bad practice' yes haha

	station_info = {}

	with open(input_file, 'r') as f:
		for line in f:
			#print(line)
			try:
				sta, lon, lat = [x for x in line.strip().split("\t") if x != ""]
			except:
				sta, lon, lat = [x for x in line.strip().split(" ") if x != ""] 
			station_info[sta] = {"lon": float(lon), "lat": float(lat)}	
	return station_info

def parse_event_coord(file_name, _format):

	event_info = {}

	# uid : {"lon", "lat", "depth"}

	if _format == "real_hypophase":
	
		with open(file_name, 'r') as f:
			for line in f:
				line = [x for x in line.strip().split(" ") if x != ""]

				if line[0] == "#":
					#print(line)

					_lon = float(line[8])
					_lat = float(line[7])
					_depth = float(line[9])
					_id = (line[-1])

					event_info[_id] = {
					"lat": _lat,
					"lon": _lon,
					"dep": _depth
					}

	elif _format == "hypoDD_loc": # any .loc or .reloc file
		with open(file_name, 'r') as f:
			for line in f:
				line = [x for x in line.strip().split(" ") if x != ""]

				_id = str(line[0]).zfill(6)

				event_info[_id] = {
				"lat":float(line[1]),
				"lon":float(line[2]),
				"dep":float(line[3])
				}

	else:
		raise ValueError("Format {} not supported, please consult the wiki".format(_format))

	return event_info

def load_travel_time(input_file):

	with open(input_file, "rb"):
		tt = np.load(input_file)

	return tt

"""

	parse_input(
		args.station_info, 
		args.phase_json,	
		args.coord_file, 
		args.coord_format, 
		args.tt_path, 
		args.output_folder, 
		event_csv = args.event_csv, 
		event_id = args.event_id, 
		dry_run = args.dry,
		save_numpy = args.save_numpy,
		write_xyz = args.write_xyz,
		convert_grd = args.convert_grd)


"""

def parse_input(station_file_name, 
	phase_json_name, 
	event_coord_file, 
	event_coord_format, 
	travel_time_file, 
	output_folder = "",
	event_csv = "",
	event_id = 0, 
	dry_run = False, 
	save_numpy = False,
	write_xyz = False,
	convert_grd = False,
	DX = 0.01,
	DZ = 5,
	ZRANGE = 41,
	TT_DX = 0.01,
	TT_DZ = 1,
	load_only = False,
	plot_mpl = False,
	show_mpl = False,
	layer_index = 0):

	if any([x == None for x in [DX, DZ, TT_DX, TT_DZ, ZRANGE]]):
		raise ValueError("Please specify DX, DZ, TT_DX, TT_DZ, and ZRANGE")

	args = {}

	args["station_file"] = station_file_name
	args["phase_json"] = phase_json_name
	args["event_coord_file"] = event_coord_file
	args["event_coord_format"] = event_coord_format
	args["travel_time_file"] = travel_time_file
	args["event_csv"] = event_csv
	args["event_id"] = event_id
	args["dry_run"] = dry_run
	args["save_numpy"] = save_numpy
	args["write_xyz"] = write_xyz
	

	args["load_only"] = load_only
	args["plot_mpl"] = plot_mpl
	args["show_mpl"] = show_mpl

	args["layer_index"] = layer_index

	args["convert_grd"] = convert_grd
	args["DX"] = DX
	args["DZ"] = DZ
	args["ZRANGE"] = ZRANGE

	args["TT_DX"] = TT_DX
	args["TT_DZ"] = TT_DZ


	station_info = parse_station_info(args["station_file"])
	event_info = parse_event_coord(args["event_coord_file"], args["event_coord_format"])
	tt = load_travel_time(args["travel_time_file"])

	args["TT_NX"] = tt.shape[0]
	args["TT_NZ"] = tt.shape[1]

	print(args)


	with open(args["phase_json"], 'r') as f:
		phase_info = json.load(f)

	file_info = {"station_info": station_info,
	"event_info": event_info,
	"tt": tt,
	"phase_info": phase_info}


	if args["event_id"]:
		padded_id = (str(args["event_id"]).zfill(6))

		search(padded_id, file_info, args) # doesn't need to return anything

	elif args["event_csv"]:

		df = pd.read_csv(args["event_csv"])

		for index, row in df.iterrows():
			try:
				_id = int(row.id)
			except:
				_id = int(row.ID)


			padded_id = str(_id).zfill(6)
			#args["output_folder"] = output_folder
			search(padded_id, file_info, args)






	# in principle this should be ok with taking in REAL and before/after hypoDD
	# info needed:
	# 	- name of stations (and station files) --> coordinates
	# 	- relative P and S arrival of each station (i.e. phase info)
	# 	- BUT: the relative P and S arrivals depend on the location of the event: if the event is relocated, then the times will be differrent
	# 	- just assume correct origin time first
	# 	
	# 	
	# 	
	# event_coord_formats:
	# real_hypophase, read lines starting with # 
	# hypoDD.loc / .reloc use every line
	
		

	#print(station_info)

	#print(phase_info)

	#print(event_info)

	


def test_grid():

	file_name = "gridsearch/000055_20210815-220241_DX0.05_DZ5.npy"

	with open(file_name, "rb") as f:
		grid = np.load(f)

	print(grid.shape)

	L2 = grid[:, :, :, 0]

	indices = np.where(L2 == L2.min())
	print(indices)

	depths = L2[indices[0][0], indices[1][0], :, ]

	plt.plot(np.arange(len(depths)), depths)
	plt.show()



	# ax = plt.imshow(L2[:, :, indices[2]], cmap = 'rainbow')
	# plt.colorbar(ax, cmap = "rainbow")

	# plt.show()




def search(pid, file_info, args):

	# input: preliminary located event, coordinates of stations, 
	# 
	# want to use grid to represent the centre coordinate of each square so it's more consistent (?)
	# 
	# size of grid: 
	# (1) draw a bounding box across all the stations
	# (2) use a set bounding box centred on the event
	# 
	# no. of grids:
	# 
	# 
	# want to use static size grid for cross comparison
	# (1) could be static e.g. divide dynamic area into N no. of grids
	# (2) or static size per grid e.g. 1km (0.01 degrees) 
	# 
	# 
	# 
	# grid unit: in decimal degrees 
	# 
	# output: a 2d map / image
	# colorscale: could i use GMT? or just use matplotlib
	# might be easier to use GMT 
	# 
	# use the netcdf 4 library to write a .nc file (and rename to .grd because geologists ree)
	# 
	
	
	# construct station list:
	phase_info = file_info["phase_info"]
	station_info = file_info["station_info"]
	tt = file_info["tt"]
	event_info = file_info["event_info"]

	station_list = phase_info[pid]["data"].keys()

	# construct grid, centered around event lat lon 

	## get bounding box



	_lats = [station_info[x]["lat"] for x in station_list]
	_lons = [station_info[x]["lon"] for x in station_list]

	_lats.append(event_info[pid]["lat"])
	_lons.append(event_info[pid]["lon"])

	_event_coords = (event_info[pid]["lon"], event_info[pid]["lat"])

	# cell parameters
	DX = args["DX"] # degrees
	DZ = args["DZ"] # km
	Z_RANGE = args["ZRANGE"]

	TT_DX = args["TT_DX"]
	TT_DZ = args["TT_DZ"] # km

	# length of travel time arrays, used for interpolation
	TT_NX = args["TT_NZ"]
	TT_NZ = args["TT_DZ"]

	# just pad some extra area
	extra_radius = 2

	# just make it a square that captures everything 
	# each grid coordinates represents a centre point 

	# left bottom corner (x ,y) == (lon, lat)
	lb_corner = (min(_lons) - extra_radius * DX, min(_lats) - extra_radius * DX) # lon, lat 

	args["event_coords"] = _event_coords
	args["lb_corner"] = lb_corner

	grid_length = int(np.ceil(max([max(_lats) - min(_lats), max(_lons) - min(_lons)])/DX) + 2 * extra_radius)

	N_Z = int(Z_RANGE/DZ)

	grid = np.zeros([grid_length, grid_length, N_Z, 4])

	print("dry_run:",args["dry_run"])

	if args["dry_run"]:

		#xyz_writer(lb_corner, DX, DZ)
		#plotter(grid, lb_corner, DX, DZ, station_list, station_info, _event_coords, pid)
		#netcdf_writer(lb_corner, DX, DZ)
		print(lb_corner, DX, DZ)
		#return (lb_corner, DX, DZ)
		#
		
		return 0
	else:
		pass

	if not args["load_only"]:
		for i in range(grid_length): # lon
			for j in range(grid_length): # lat
				for k in range(N_Z): # depth

					cell_coords = [i * DX + lb_corner[0], j * DX + lb_corner[1], k * DZ]

					delta_r = [] # distance and depth pairs
					phase_list = []
					obs_tt = []

					for station in phase_info[pid]["data"]:
						for phase in phase_info[pid]["data"][station]:

							_dep = k * DZ # stations assumed to be at 0 km elevation

							_dist = dx([station_info[station]["lon"], station_info[station]["lat"]], cell_coords[:2])

							_row = [_dist, _dep]

							phase_list.append(phase)
							delta_r.append(_row)
							obs_tt.append(float(phase_info[pid]["data"][station][phase]))

							#print(_row)

					delta_r = np.array(delta_r)
					obs_tt = np.array(obs_tt)

					# bin the distance and depth 
					# bin distance only (?) i won't be touching depth
					
					tt_dist_indices = np.array([int(x) for x in delta_r[:, 0]/TT_DX])

					tt_dist_deltas = delta_r[:,0] - tt_dist_indices * TT_DX

					tt_dep_index = int((k * DZ)/TT_DZ)
					#print(tt_dep_index)

					#print(max(delta_r[:,0]))

					#print(tt_dist_indices)
					#print(tt_dist_deltas)
					#
					
					tt_cell = []
					
					tt_dist_gradients = []


					# do an interpolation operation by taking the nearby indices
					# and estimating gradient

					for _c, _i in enumerate(tt_dist_indices): #_i are for travel time table indices

						if _i + 1 > TT_NX:
							_indices = np.array([_i - 1, _i])
						if _i - 1 < 0:
							_indices = np.array([_i, _i + 1])
						_indices = np.array([_i - 1, _i, _i + 1]) 

						if phase_list[_c] == "P":
							_Y = [tt[_x][tt_dep_index][0] for _x in _indices]
							tt_cell.append(tt[_i][tt_dep_index][0])

						elif phase_list[_c] == "S":
							_Y = [tt[_x][tt_dep_index][1] for _x in _indices]

							tt_cell.append(tt[_i][tt_dep_index][1])

						tt_dist_gradients.append(ip((_indices) * TT_DX, _Y))

					tt_dist_gradients = np.array(tt_dist_gradients)
					tt_cell = np.array(tt_cell)

					# add the correction from the table terms using interpolation method

					tt_cell += tt_dist_gradients * tt_dist_deltas

					# calculate L2 and L1 errors

					sq_residuals = (tt_cell - obs_tt)**2
					abs_residuals = np.sqrt(sq_residuals)

					# keep standard dev in array because idk that could be useful? 

					volume = (grid_length * DX)**2 * (Z_RANGE)

					sq_residuals /= volume
					abs_residuals /= volume

					L2 = np.sum(sq_residuals)
					L2_std = np.std(sq_residuals)
					L1 = np.sum(abs_residuals)
					L1_std = np.std(abs_residuals)

					grid[i][j][k][0] = L2
					grid[i][j][k][1] = L2_std
					grid[i][j][k][2] = L1
					grid[i][j][k][3] = L1_std



	
	# numpy saving of the whole array
	# also include cell numbers to construct the array
	# lower left corner can be constructed from the ID tbh
	# 
	
	#print(grid)

	output_folder = os.path.join(args["output_folder"], pid)

	base_filename = "{}_DX{}_DZ{}".format(pid, DX, DZ)
	npy_filename = os.path.join(output_folder, base_filename + ".npy")
	xyz_filename = os.path.join(output_folder, base_filename + ".xyz")
	grd_filename = os.path.join(output_folder, base_filename + ".grd")

	#args["output_folder"] = output_folder
	args["base_filename"] = base_filename
	args["npy_filename"] = npy_filename
	#args["xyz_filename"] = xyz_filename



	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	if args["load_only"]:
		with open(npy_filename, 'rb') as f:
			grid = np.load(f)

	else:
		if args["save_numpy"]:
			print("Saving .npy to: ", npy_filename)
			with open(npy_filename, 'wb') as f:
				np.save(f, grid)

	if args["write_xyz"]:
		xyz_writer(grid, lb_corner, DX, DZ, 0, output_folder = output_folder, filename = base_filename)
		

	if args["convert_grd"]:
		# gmt xyz2grd test.xyz -Gtest.grd -I0.05 $LIMS

		# just generate the script and run it lol
		# but gmt isn't installed / conda has to be active
		# should i just activate conda

		output_str = "gmt xyz2grd {} -G{} -I{:.3g} -R{:.5g}/{:.5g}/{:.5g}/{:.5g}".format(
			xyz_filename,
			grd_filename,
			DX,
			lb_corner[0],
			lb_corner[0] + grid_length * DX,
			lb_corner[1],			
			lb_corner[1] + grid_length * DX,
			)
		p = subprocess.Popen(output_str, shell = True)

	if args["plot_mpl"]:
		plotter(pid, station_list, station_info, args)

	
		#gmt xyz2grd test.xyz -Gtest.grd -I0.05 $LIMS




	# for each grid cell, compute the misfit between the observed and 'theoretical' travel time
	# use both L1 and L2 norm because... reasons? first entry for L1, second for L2
	# 
	# construct a vector target locations (station locations), calculate for each of them the distance
	# (do a plane approx) and the depth difference, 
	# use the table to do a interpolation to get the estimated travel time (not that i think it'll help)
	# compute the squared difference and save it somewhere (inside the grid?)

def xyz_writer(grid, lb_corner, DX, DZ, index = 0, output_folder = "", filename = ""):

	L2 = grid[:,:,:,index]

	indices = np.where(L2 == L2.min())

	N_X, N_Y, N_Z = grid.shape[:3]
	

	output = L2[:,:,indices[2][0]]

	output_file = os.path.join(output_folder, filename + ".xyz")

	with open(output_file, "w") as f:
		for i in range(N_X):
			for j in range(N_Y):
				x = lb_corner[0] + i * DX
				y = lb_corner[1] + j * DX

				z = output[i,j]

				f.write("{:.7f} {:.7f} {:.3f}\n".format(x,y,z))


	

def netcdf_writer(lb_corner, DX, DZ ):

	# https://unidata.github.io/python-training/workshop/Bonus/netcdf-writing/
	grp = netCDF4.Dataset("gmt/gridsearch/test.nc", "w")

	with open("gridsearch/55_test_grid.npy", 'rb') as f:
		grid = np.load(f)

	# need array dimensions

	N_X, N_Y, N_Z = grid.shape[:3]

	print("loaded shape", grid.shape)

	# need starting positions + stepsize
	lon_dim = grp.createDimension('x', N_X)
	lat_dim = grp.createDimension('y', N_Y)


	# write a model title for completion with date 
	grp.title = "Test"
	grp.setncattr_string("")
	x = grp.createVariable('x', np.float64, ('x',))
	x.units = 'degrees_east'
	x.long_name = 'x'
	y = grp.createVariable('y', np.float64, ('y',))
	y.units = 'degrees_north'
	y.long_name = 'y'

	print(N_X, N_Y)
	print(lb_corner)


	x[:] = lb_corner[0] + np.arange(N_X) * DX
	y[:] = lb_corner[1] + np.arange(N_Y) * DX

	#print(lon[:])
	#print(lat[:])

	#print(grid[0][0][0][0].shape)

	rms_l2 = grp.createVariable("z", np.float64, ('x', 'y', ))

	rms_l2.units = 'km'
	rms_l2.long_name = "z"


	best_depth = 9

	rms_l2[:,:] = grid[:,:,best_depth,0]

	print(rms_l2)


	grp.close()




def ip(X, Y):
	if len(X) == 3:

		# arithmetic average of in between gradients to approximate gradient at midpoint

		return 0.5 * ((Y[2] - Y[1])/(X[2] - X[1]) + (Y[1] - Y[0])/(X[1] - X[0]))

	if len(X) == 2:

		return (Y[1] - Y[0])/(X[1] - X[0])

def dx(X1, X2):
	return np.sqrt((X1[0] - X2[0])**2 + (X1[1] - X2[1])**2)


# interpolation function


def convert_tt_file(input_file, output_file):

	# use the REAL format

	# dist, dep, p_time,s_time, p_ray_param, s_ray_param, p_hslowness, s_hslowness, pname, sname

	# or just make it a 3d array

	tt_table = np.zeros([301, 41, 2]) # hard coded and depends on size of array

	with open(input_file, 'r') as f:
		for line in f:
			_data = line.strip().split(" ")
			_dist = float(_data[0])
			_depth = float(_data[1])

			_x_1 = int(_dist/0.01) # there will be one empty row (the very first one) which is inconsequential

			_x_2 = int(_depth)

			_P = float(_data[2])
			_S = float(_data[3])

			tt_table[_x_1][_x_2][0] = _P
			tt_table[_x_1][_x_2][1] = _S

	# save numpy file
	#print(tt_table)

	with open(output_file, "wb") as f:
		np.save(f, tt_table)

# plotting: i think plot 2D, in the top down plane, height at the depth of the maxima? idk
# https://www.python-course.eu/matplotlib_contour_plot.php

if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument("-convert_tt")
	parser.add_argument("-output_tt")


	parser.add_argument("-station_info")
	parser.add_argument("-phase_json")
	parser.add_argument("-coord_file")
	parser.add_argument("-coord_format", choices = ["real_hypophase", "hypoDD_loc"])
	parser.add_argument("-tt_path")
	parser.add_argument("-output_folder")

	parser.add_argument("-event_csv")
	parser.add_argument("-event_id", type = int)

	parser.add_argument("-zrange", type = float)

	parser.add_argument("-tt_dx", type = float)
	parser.add_argument("-tt_dz", type = float)


	parser.add_argument("-dx", type = float)
	parser.add_argument("-dz", type = float)

	parser.add_argument("-save_numpy", action = "store_true")
	parser.add_argument("-write_xyz", action = "store_true")
	parser.add_argument("-convert_grd", action = "store_true")

	parser.add_argument("-load_only", action = "store_true")
	parser.add_argument("-plot_mpl", action = "store_true")
	parser.add_argument("-show_mpl", action = "store_true")

	parser.add_argument("-layer_index", type = int, default = 0, choices = [0,1,2,3], help = "Refer to wiki. 0: L2 norm, 1: L2 stdev, 2: L1 norm, 3: L1 stdev")

	parser.add_argument('-dry', action = "store_true")


	args = parser.parse_args()


	#parse_input(args.event_csv, arg)

	if args.tt_path:

		parse_input(
			args.station_info, 
			args.phase_json,	
			args.coord_file, 
			args.coord_format, 
			args.tt_path, 
			args.output_folder, 
			event_csv = args.event_csv, 
			event_id = args.event_id, 
			dry_run = args.dry,
			save_numpy = args.save_numpy,
			write_xyz = args.write_xyz,
			convert_grd = args.convert_grd,
			TT_DX = args.tt_dx,
			TT_DZ = args.tt_dz,
			DX = args.dx,
			DZ = args.dz,
			ZRANGE = args.zrange,
			load_only = args.load_only,
			plot_mpl = args.plot_mpl,
			show_mpl = args.show_mpl,
			layer_index = args.layer_index,
			)


	elif args.convert_tt:
		convert_tt_file(args.convert_tt, args.output_tt)



	#parse_input(55, "station_info.dat", "real_postprocessing/5jul_assoc/5jul_aceh_phase.json", "/home/zy/cy1400-eqt/real_postprocessing/5jul_assoc/aceh_phase.dat", "real_hypophase", "gridsearch/tt_t.npy", dry_run = True)

	
	#convert_tt_file("gridsearch/zy_ttdb.txt")

