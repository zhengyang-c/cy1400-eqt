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

# https://stackoverflow.com/questions/13670333/multiple-variables-in-scipys-optimize-minimize
import scipy.optimize as optimize

from util_gridsearch import arbitrary_search


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
	N_DX = 20,
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

	# set initial seed as the bounding boxes of the region
	# i.e.
	# LON 94 - 97
	# LAT 3 -6 

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


	# if not args["N_DX"]: # default for N_DX is 0

	# 	DX = args["DX"] # degrees
	# 	# length of travel time arrays, used for interpolation
	# 	# just pad some extra area
	# 	# just make it a square that captures everything 
	# 	# each grid coordinates represents a centre point 
	# 	# left bottom corner (x ,y) == (lon, lat)
	# 	# 
	# 	lb_corner = (min(_lons) - extra_radius * DX, min(_lats) - extra_radius * DX) # lon, lat 
	# 	grid_length = int(round(np.ceil(_max_length/DX) + 2 * extra_radius))

	# else:

	# 	# how to decide extra padding? just take the max dist and add like 10% on each side

	# 	padding_range = (args["extra_range"] - 1)/2

	# 	lb_corner = (min(_lons) - _max_length*padding_range, min(_lats) - _max_length*padding_range)
	# 	max_grid_length = _max_length * args["extra_range"]

	# 	DX = max_grid_length / args["N_DX"]

	# 	grid_length = int(round(math.ceil(max_grid_length/DX)))
	# 	args["DX"] = DX 


	#args["lb_corner"] = lb_corner
	#args["grid_length"] = grid_length

	N_Z = int(round(Z_RANGE/DZ))

	args["N_Z"] = N_Z

	print("dry_run:",args["dry_run"])

	# metadata is for json saving

	output_folder = os.path.join(args["output_folder"], pid)

	base_filename = "{}_DZ{:.3g}".format(pid, DZ)

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

	
	# with open(json_filename, 'w') as f:
	# 	f.write(json.dumps(metadata, indent = 4))
	# 	if args["print_metadata"]:
	# 		return 0

		
	seed_lb_corner = (94.5, 3.5)
	seed_grid_length = 2
	if args["force"] or (not already_created):
		#grid = simple_search(args, phase_info, station_info, tt)
		
		grid_output = arbitrary_search(args, seed_lb_corner, seed_grid_length, phase_info, station_info, tt)

		target_lb = (grid_output["min_x"] - 0.1, grid_output["min_y"] - 0.1)
		target_grid_length = 0.2

		ref_lambda = arbitrary_search(args, target_lb, target_grid_length, phase_info, station_info, tt, compute_lambda = True)

		ref_tau = ref_lambda - ref_lambda[args["N_DX"]//2, args["N_DX"] // 2]

		mc_args = {"sigma_ml": grid_output["sigma_ml"], "ref_tau" : ref_tau, "min_z": grid_output["min_z"] }

		arbitrary_search(args, target_lb, target_grid_length, phase_info, station_info, tt, compute_lambda = True, mc_args = mc_args, N_monte_carlo = 20, do_mc = True)




	
	# numpy saving of the whole array
	# also include cell numbers to construct the array
	# lower left corner can be constructed from the ID tbh
	# 
	
	#print(grid)


	# if args["load_only"]:
	# 	with open(npy_filename, 'rb') as f:
	# 		grid = np.load(f)

	# else:
	# 	if (args["force"] or not os.path.exists(npy_filename)):
	# 		print("Saving .npy to: ", npy_filename)
	# 		with open(npy_filename, 'wb') as f:
	# 			np.save(f, grid)

	# if args["write_xyz"]:
	# 	xyz_writer(grid, lb_corner, DX, DZ, 0, output_folder = output_folder, filename = base_filename)
		

	# if args["convert_grd"]:
	# 	# gmt xyz2grd test.xyz -Gtest.grd -I0.05 $LIMS

	# 	# just generate the script and run it lol
	# 	# but gmt isn't installed / conda has to be active
	# 	# should i just activate conda

	# 	output_str = "gmt xyz2grd {} -G{} -I{:.3g} -R{:.5g}/{:.5g}/{:.5g}/{:.5g}".format(
	# 		xyz_filename,
	# 		grd_filename,
	# 		DX,
	# 		lb_corner[0],
	# 		lb_corner[0] + grid_length * DX,
	# 		lb_corner[1],			
	# 		lb_corner[1] + grid_length * DX,
	# 		)
	# 	p = subprocess.Popen(output_str, shell = True)

	# if args["plot_mpl"]:
	# 	plotter(pid, station_list, station_info, args)

	
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




# find the euclidean distance, taken to approximate the great circle distance for small distances



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

	parser.add_argument("-n_dx", type = int, default = 20)

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

