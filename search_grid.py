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
import math

from organise_by_event import df_searcher

from itertools import repeat

import multiprocessing as mp

from utils import parse_station_info, parse_event_coord

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


def load_travel_time(input_file):

	with open(input_file, "rb"):
		tt = np.load(input_file)

	return tt


def parse_input(station_file_name, 
	phase_json_name, 
	event_coord_file, 
	event_coord_format, 
	travel_time_file, 
	output_folder = "",
	event_csv = "",
	event_id = 0, 
	dry_run = False, 
	write_xyz = False,
	convert_grd = False,
	DX = 0.01,
	N_DX = 0,
	DZ = 5,
	ZRANGE = 41,
	TT_DX = 0.01,
	TT_DZ = 1,
	load_only = False,
	plot_mpl = False,
	show_mpl = False,
	force = False,
	eqt_csv = "",
	extra_radius = 2,
	extra_range = 1.2,
	append_text = "",
	print_metadata = False,):

	if any([x == None for x in [DZ, TT_DX, TT_DZ, ZRANGE]]) or (not N_DX and not DX):
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
	#args["save_numpy"] = save_numpy
	args["write_xyz"] = write_xyz
	args["output_folder"] = output_folder

	args["extra_radius"] = extra_radius
	args["extra_range"] = extra_range
	args["append_text"] = append_text

	args["load_only"] = load_only
	args["plot_mpl"] = plot_mpl
	args["show_mpl"] = show_mpl	

	args["print_metadata"] = print_metadata

	args["eqt_csv"] = eqt_csv

	if show_mpl:
		args["plot_mpl"] = True
		#args["save_numpy"] = True

	args["force"] = force

	args["convert_grd"] = convert_grd
	args["DX"] = DX
	args["DZ"] = DZ
	args["ZRANGE"] = ZRANGE


	args["N_DX"] = N_DX

	args["TT_DX"] = TT_DX
	args["TT_DZ"] = TT_DZ



	print(args)


	df = load_eqt_csv(eqt_csv)


	if args["event_id"]:
		padded_id = (str(args["event_id"]).zfill(6))


		search(padded_id, args) # doesn't need to return anything

	elif args["event_csv"]:
		df = pd.read_csv(args["event_csv"])

		try:
			all_id = df["id"].tolist()
		except:
			try:
				all_id = df["ID"].tolist()
			except:
				all_id = df["cat_index"].tolist()

		all_id = [str(int(_id)).zfill(6) for _id in all_id]

		pool = mp.Pool(mp.cpu_count())

		result = pool.starmap(search, zip(all_id, repeat(args)))



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

	
def load_eqt_csv(eqt_csv):

	df = pd.read_csv(eqt_csv)
	df["p_arrival_time"] = pd.to_datetime(df["p_arrival_time"])
	df["s_arrival_time"] = pd.to_datetime(df["s_arrival_time"])

	return df

def filter_eqt_phases():

	pass


def search(pid, args):

	# move file loading to children

	station_info = parse_station_info(args["station_file"])
	event_info = parse_event_coord(args["event_coord_file"], args["event_coord_format"])
	tt = load_travel_time(args["travel_time_file"])
	args["TT_NX"] = tt.shape[0]
	args["TT_NZ"] = tt.shape[1]
	with open(args["phase_json"], 'r') as f:
		phase_info = json.load(f)

	_station_dict = phase_info[pid]['data']

	_ts = phase_info[pid]['timestamp']

	df = load_eqt_csv(args["eqt_csv"])

	phase_info = df_searcher(df, _station_dict, _ts)["_station_dict"]


	# construct station list:
	station_list = phase_info.keys()

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
	


	"""
	options:
	1) rely on REAL association to choose phases
	2) manually choose phases myself

	obviously i am going to do (1) because REAL association is alright

	plotting the wadati diagram, there are a lot of outliers

	but if i only use the phases that REAL is using, there are almost no outliers
	so at least the association is reliable

	that said i think i'll have to plot the record section
	but the record section is plot using raw SAC data i.e. it's not bp filtered yet
	i could write a new file e.g. append like a _ or something at the back
	but that would take up double the space
	the folder is already 12.8GB
	i have 84GB available 
	the original archive is also on disk and on onedrive so i could just modify the traces later

	so:

	1. load EQT csv 
	2. for specific station phases, find the correct detection assuming REAL phase choice is correct 
	(which it has good reason to be, given the wadati diagram plot)

	i'm not doing EQ association myself

	3. maybe also save the csv file subset so you don't have to do the operation everytime 
	4. save the p arrival and s arrival time in their own vectors python list

	5. for each grid cell, obtain an array of 'candidate' origin times
	6. since np.std() cannot operate directly on datetime objects, normalise using the minimum value
	7. find the standard deviation and save in the cell

	this means that the grid doesn't need like size 4 array for every cell

	but i'm also lazy to like rework it you know

	8. the cell with the minimum standard deviation should give the origin time + location

	"""

	# construct grid, centered around event lat lon 

	# get bounding box first



	_lats = [station_info[x]["lat"] for x in station_list]
	_lons = [station_info[x]["lon"] for x in station_list]

	_lats.append(event_info[pid]["lat"])
	_lons.append(event_info[pid]["lon"])

	_max_length = max([max(_lats) - min(_lats), max(_lons) - min(_lons)])

	_event_coords = (event_info[pid]["lon"], event_info[pid]["lat"])

	# cell parameters
	DZ = args["DZ"] # km
	Z_RANGE = args["ZRANGE"]

	TT_DX = args["TT_DX"]
	TT_DZ = args["TT_DZ"] # km

	TT_NX = args["TT_NZ"]
	TT_NZ = args["TT_DZ"]
	extra_radius = args["extra_radius"]
	args["event_coords"] = _event_coords


	if not args["N_DX"]: # default for N_DX is 0

		DX = args["DX"] # degrees
		# length of travel time arrays, used for interpolation
		# just pad some extra area
		# just make it a square that captures everything 
		# each grid coordinates represents a centre point 
		# left bottom corner (x ,y) == (lon, lat)
		# 
		lb_corner = (min(_lons) - extra_radius * DX, min(_lats) - extra_radius * DX) # lon, lat 
		grid_length = int(round(np.ceil(_max_length/DX) + 2 * extra_radius))

	else:

		# how to decide extra padding? just take the max dist and add like 10% on each side

		padding_range = (args["extra_range"] - 1)/2

		lb_corner = (min(_lons) - _max_length*padding_range, min(_lats) - _max_length*padding_range)
		max_grid_length = _max_length * args["extra_range"]

		DX = max_grid_length / args["N_DX"]

		grid_length = int(round(math.ceil(max_grid_length/DX)))
		args["DX"] = DX 


	args["lb_corner"] = lb_corner

	N_Z = int(round(Z_RANGE/DZ))

	grid = np.zeros([grid_length, grid_length, N_Z, 4])

	print("dry_run:",args["dry_run"])
	metadata = {
		"corner_x": lb_corner[0],
		"corner_y": lb_corner[1],
		"DX": DX,
		"DZ": DZ,
		"ID:": pid,
	}
	# if args["print_metadata"]:



	# 	#xyz_writer(lb_corner, DX, DZ)
	# 	#plotter(grid, lb_corner, DX, DZ, station_list, station_info, _event_coords, pid)
	# 	#netcdf_writer(lb_corner, DX, DZ)
	# 	print(lb_corner, DX, DZ)
	# 	#return (lb_corner, DX, DZ)
	# 	#
		
	# 	return 0
	# else:
	# 	pass

	output_folder = os.path.join(args["output_folder"], pid)

	base_filename = "{}_DX{:.3g}_DZ{:.3g}".format(pid, DX, DZ)

	if args["append_text"]:
		base_filename += "_{}".format(args["append_text"])

	npy_filename = os.path.join(output_folder, base_filename + ".npy")
	xyz_filename = os.path.join(output_folder, base_filename + ".xyz")
	grd_filename = os.path.join(output_folder, base_filename + ".grd")

	json_filename = os.path.join(output_folder, base_filename + ".json")

	#args["output_folder"] = output_folder
	args["base_filename"] = base_filename
	args["npy_filename"] = npy_filename
	#args["xyz_filename"] = xyz_filename

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	already_created = os.path.exists(npy_filename) or os.path.exists(xyz_filename) or os.path.exists(grd_filename)
	print("already created: ", already_created)

	if args["print_metadata"]:
		with open(json_filename, 'w') as f:
			f.write(json.dumps(metadata, indent = 4))
		return 0

		
	elif args["force"] or (not already_created):
		
		for i in range(grid_length): # lon
			for j in range(grid_length): # lat
				for k in range(N_Z): # depth

					cell_coords = [i * DX + lb_corner[0], j * DX + lb_corner[1], k * DZ]

					delta_r = [] # distance and depth pairs
					phase_list = []
					#obs_tt = []

					arrivals = [] # origin times
					# this only uses phases chosen by REAL association
					for station in phase_info:

						for phase in ["P", "S"]:
							if phase not in phase_info[station]:
								continue

							_dep = k * DZ # stations assumed to be at 0 km elevation

							_dist = dx([station_info[station]["lon"], station_info[station]["lat"]], cell_coords[:2])

							_row = [_dist, _dep]

							phase_list.append(phase)
							delta_r.append(_row)
							#obs_tt.append(float(phase_info[station][phase]))
							if phase == "P":
								arrivals.append(phase_info[station]["station_P"])
							elif phase == "S":
								arrivals.append(phase_info[station]["station_S"])

							#print(_row)

					delta_r = np.array(delta_r)
					#obs_tt = np.array(obs_tt)

					# bin the distance and depth 
					# bin distance only (?) i won't be touching depth
					
					tt_dist_indices = np.array([int(round(x)) for x in delta_r[:, 0]/TT_DX])

					tt_dist_deltas = delta_r[:,0] - tt_dist_indices * TT_DX

					tt_dep_index = int(round((k * DZ)/TT_DZ))
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
						elif _i - 1 < 0:
							_indices = np.array([_i, _i + 1])
						else:
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

					# with the travel times, find the set of origin times

					assert len(phase_list) == len(arrivals) == len(tt_cell)

					guess_ot = []

					for _c in range(len(arrivals)):
						guess_ot.append(arrivals[_c] - datetime.timedelta(seconds = tt_cell[_c]))

					# normalise the origin times and find the std 

					min_origin_time = min(guess_ot)
					for _c in range(len(guess_ot)):
						guess_ot[_c] = (guess_ot[_c] - min_origin_time).total_seconds()

					mean_time = np.mean(guess_ot)
					std_time = np.std(guess_ot)
					#ref_str = datetime.datetime.strftime(min_origin_time, "%Y%m%d-%H%M%S.%f")

					grid[i][j][k][0] = std_time
					grid[i][j][k][1] = mean_time
					grid[i][j][k][2] = min_origin_time.timestamp()
					# save the mean and std origin time in the grid
					# saving the datetime object sounds like a bad idea
					# so just convert the reference time to a string?
					# so it'll be
					# 
					# std
					# mean delta
					# min_time reference as string
					# 
					# then i can look up the cell, and reobtain the mean time
					# 
					





					"""
					following code was done assuming the truth of REAL travel times, which
					may not always be the case
					they are left here for reference
					"""

					# # calculate L2 and L1 errors

					# sq_residuals = (tt_cell - obs_tt)**2
					# abs_residuals = np.sqrt(sq_residuals)

					# # keep standard dev in array because idk that could be useful? 

					# volume = (grid_length * DX)**2 * (Z_RANGE)

					# sq_residuals /= volume
					# abs_residuals /= volume

					# L2 = np.sum(sq_residuals)
					# L2_std = np.std(sq_residuals)
					# L1 = np.sum(abs_residuals)
					# L1_std = np.std(abs_residuals)

					# grid[i][j][k][0] = L2
					# grid[i][j][k][1] = L2_std
					# grid[i][j][k][2] = L1
					# grid[i][j][k][3] = L1_std



	
	# numpy saving of the whole array
	# also include cell numbers to construct the array
	# lower left corner can be constructed from the ID tbh
	# 
	
	#print(grid)


	if args["load_only"]:
		with open(npy_filename, 'rb') as f:
			grid = np.load(f)

	else:
		if (args["force"] or not os.path.exists(npy_filename)):
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





def ip(X, Y):
	if len(X) == 3:

		# arithmetic average of in between gradients to approximate gradient at midpoint

		return 0.5 * ((Y[2] - Y[1])/(X[2] - X[1]) + (Y[1] - Y[0])/(X[1] - X[0]))

	if len(X) == 2:

		return (Y[1] - Y[0])/(X[1] - X[0])

# find the euclidean distance, taken to approximate the great circle distance for small distances
def dx(X1, X2):
	return np.sqrt((X1[0] - X2[0])**2 + (X1[1] - X2[1])**2)


def convert_tt_file(input_file, output_file):

	# use the REAL format

	# dist, dep, p_time,s_time, p_ray_param, s_ray_param, p_hslowness, s_hslowness, pname, sname

	# or just make it a 3d array

	tt_table = np.zeros([301, 41, 2]) # hard coded and depends on size of array

	with open(input_file, 'r') as f:
		for c, line in enumerate(f):

			_data = line.strip().split(" ")
			_dist = float(_data[0])
			_depth = float(_data[1])

			_x_1 = int(round(_dist/0.01)) # there will be one empty row (the very first one) which is inconsequential

			_x_2 = round(_depth)

			

			_P = float(_data[2])
			_S = float(_data[3])

			#print("dist index",_x_1, "_dist:",_dist, len(_data[0]))

			tt_table[_x_1][_x_2][0] = _P
			tt_table[_x_1][_x_2][1] = _S

	# save numpy file
	#print(tt_table)

	with open(output_file, "wb") as f:
		np.save(f, tt_table)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument("-convert_tt")
	parser.add_argument("-output_tt")


	parser.add_argument("-station_info")
	parser.add_argument("-phase_json")

	parser.add_argument("-eqt_csv")
	parser.add_argument("-coord_file")
	parser.add_argument("-coord_format", choices = ["real_hypophase", "hypoDD_loc"])
	parser.add_argument("-tt_path")
	parser.add_argument("-output_folder")

	parser.add_argument("-f", "--force", help = "Force to run gridsearch", action = 'store_true')

	parser.add_argument("-event_csv")
	parser.add_argument("-event_id", type = int)

	parser.add_argument("-zrange", type = float)

	parser.add_argument("-tt_dx", type = float)
	parser.add_argument("-tt_dz", type = float)

	parser.add_argument("-n_dx", type = float)


	parser.add_argument("-dx", type = float)
	parser.add_argument("-dz", type = float)

	#parser.add_argument("-save_numpy", action = "store_true")

	parser.add_argument("-p", "--print_metadata", action = "store_true")
	parser.add_argument("-write_xyz", action = "store_true")
	parser.add_argument("-convert_grd", action = "store_true")

	parser.add_argument("-load_only", action = "store_true")
	parser.add_argument("-plot_mpl", action = "store_true")
	parser.add_argument("-show_mpl", action = "store_true")

	parser.add_argument("-extra_radius", type = int, default = 2)
	parser.add_argument("-extra_range", type = float, default = 1.2)
	parser.add_argument("-append_text", type = str, default = "")

	#parser.add_argument("-layer_index", type = int, default = 0, choices = [0,1,2,3], help = "Refer to wiki. 0: L2 norm, 1: L2 stdev, 2: L1 norm, 3: L1 stdev")

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
			write_xyz = args.write_xyz,
			convert_grd = args.convert_grd,
			TT_DX = args.tt_dx,
			TT_DZ = args.tt_dz,
			DX = args.dx,
			DZ = args.dz,
			N_DX = args.n_dx,
			ZRANGE = args.zrange,
			load_only = args.load_only,
			plot_mpl = args.plot_mpl,
			show_mpl = args.show_mpl,
			force = args.force,
			eqt_csv = args.eqt_csv,
			extra_radius = args.extra_radius,
			extra_range = args.extra_range,
			append_text = args.append_text,
			print_metadata = args.print_metadata,
			)


	elif args.convert_tt:
		convert_tt_file(args.convert_tt, args.output_tt)



	#parse_input(55, "station_info.dat", "real_postprocessing/5jul_assoc/5jul_aceh_phase.json", "/home/zy/cy1400-eqt/real_postprocessing/5jul_assoc/aceh_phase.dat", "real_hypophase", "gridsearch/tt_t.npy", dry_run = True)

	
	#convert_tt_file("gridsearch/zy_ttdb.txt")

