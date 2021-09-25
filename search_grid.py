from re import T
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import argparse
import datetime
import os


import kml_make

#gpsdist: two distance between two geographic points
# locations2degrees: no. of degrees between two points on a spherical earth
# degrees to kilometers (i think this is like multiplying with factor of)


from plot_gridsearch import plotter, gmt_plotter, preplot
import subprocess
import math

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

class NumpyEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.ndarray):
			return obj.tolist()
		if isinstance(obj, np.int64):
			return float(obj)
		return json.JSONEncoder.default(self, obj)

def load_travel_time(input_file):

	with open(input_file, "rb"):
		tt = np.load(input_file)

	return tt

def parse_input(station_file_name, 
	phase_json_name, 
	travel_time_file, 
	output_folder = "",
	event_csv = "",
	event_id = 0, 
	N_DX = 20,
	DZ = 5,
	ZRANGE = 41,
	TT_DX = 0.01,
	TT_DZ = 1,
	load_only = False,
	plot_mpl = False,
	show_mpl = False,
	force = False,
	map_type = "",
	run_rotate = False,
	event_folder = "",
	exclude = "",
	append_text = "",
	p_only = False,
	s_only = False,
	time_remapping = "",
	gmt_home = "",
	no_plot = False
	):

	if any([x == None for x in [DZ, TT_DX, TT_DZ, ZRANGE]]): 
		raise ValueError("Please specify DX, DZ, TT_DX, TT_DZ, and ZRANGE")

	args = {}

	args["station_file"] = station_file_name
	args["phase_json"] = phase_json_name
	# args["event_coord_file"] = event_coord_file
	# args["event_coord_format"] = event_coord_format
	args["travel_time_file"] = travel_time_file
	args["event_csv"] = event_csv
	args["event_id"] = event_id

	args["output_folder"] = output_folder

	args["map_type"] = map_type

	args["load_only"] = load_only
	args["plot_mpl"] = plot_mpl
	args["show_mpl"] = show_mpl	

	args["gmt_home"] = gmt_home

	args["event_folder"] = event_folder
	args["run_rotate"] = run_rotate

	args["no_plot"] = no_plot

	if show_mpl:
		args["plot_mpl"] = True
		#args["save_numpy"] = True

	args["force"] = force

	args["DZ"] = DZ
	args["ZRANGE"] = ZRANGE


	args["N_DX"] = N_DX

	args["TT_DX"] = TT_DX
	args["TT_DZ"] = TT_DZ
	args["exclude"] = exclude

	args["append_text"] = append_text

	args["p_only"] = p_only
	args["s_only"] = s_only

	args["time_remapping"] = time_remapping
	# apply time remapping when loading the phase info


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

	
def load_eqt_csv(eqt_csv):

	df = pd.read_csv(eqt_csv)
	df["p_arrival_time"] = pd.to_datetime(df["p_arrival_time"])
	df["s_arrival_time"] = pd.to_datetime(df["s_arrival_time"])

	return df


def search(pid, args):

	# move file loading to children

	station_info = parse_station_info(args["station_file"])

	#event_info = parse_event_coord(args["event_coord_file"], args["event_coord_format"])
	tt = load_travel_time(args["travel_time_file"])
	args["TT_NX"] = tt.shape[0]
	args["TT_NZ"] = tt.shape[1]

	args["pid"] = pid

	with open(args["phase_json"], 'r') as f:
		phase_info = json.load(f)

	#_station_dict = phase_info[pid]['data']


	_ts = phase_info[pid]['timestamp']

	#df = load_eqt_csv(args["eqt_csv"])

	phase_info = phase_info[pid]["data"]

	if args["time_remapping"]:
		rdf = pd.read_csv(args["time_remapping"])#remap dataframe
		rdf["p_arrival_time"] = pd.to_datetime(rdf["p_arrival_time"])
		rdf["s_arrival_time"] = pd.to_datetime(rdf["s_arrival_time"])
		for index, row in rdf.iterrows():
			_p = row.p_arrival_time
			_s = row.s_arrival_time

			_sta = row.datetime_str.split(".")[0]

			if _sta in phase_info:

				if 'P' in phase_info[_sta]:
					if _p == phase_info[_sta]['station_P']:
						phase_info[_sta]['station_P'] += datetime.timedelta(seconds = row.A_delta)

				if 'S' in phase_info[_sta]:
					if _s == phase_info[_sta]['station_S']:
						phase_info[_sta]['station_S'] += datetime.timedelta(seconds = row.T0_delta)


	# exclude after time remapping so phases won't get deleted + throw error (?) whatever

	#print(phase_info)

	if args["exclude"]:
		exclude_df = pd.read_csv(args["exclude"])
		_edf = exclude_df[exclude_df["ID"] == int(pid)]

		for index, row in _edf.iterrows():
			if row.station in phase_info:
				if row.phase in phase_info[row.station]:
					print("Excluding station {} phase {}".format(row.station, row.phase))
					phase_info[row.station].pop("station_" + row.phase)
					phase_info[row.station].pop(row.phase)


	if args["p_only"] or args["s_only"]:
		for _station in phase_info:
			if ("station_P" in phase_info[_station]) and args["p_only"]:
				phase_info[_station].pop("station_S")
			if ("station_S" in phase_info[_station]) and args["s_only"]:
				phase_info[_station].pop("station_P")

	station_list = phase_info.keys()

	_lats = [station_info[x]["lat"] for x in station_list]
	_lons = [station_info[x]["lon"] for x in station_list]

	# _lats.append(event_info[pid]["lat"])
	# _lons.append(event_info[pid]["lon"])

	_max_length = max([max(_lats) - min(_lats), max(_lons) - min(_lons)])

	#_event_coords = (event_info[pid]["lon"], event_info[pid]["lat"])

	# cell parameters
	DZ = args["DZ"] # km
	Z_RANGE = args["ZRANGE"]

	TT_DX = args["TT_DX"]
	TT_DZ = args["TT_DZ"] # km

	TT_NX = args["TT_NZ"]
	TT_NZ = args["TT_DZ"]
	#args["event_coords"] = _event_coords
	N_Z = int(round(Z_RANGE/DZ))

	args["N_Z"] = N_Z	

	# metadata is for json saving
	if args["run_rotate"]:
		_output_folder = os.path.join(args["output_folder"], pid + "_c")
	else:
		_output_folder = os.path.join(args["output_folder"], pid)


	if args["append_text"]:
		base_filename = "{}_{}".format(pid, args["append_text"])
	else:
		base_filename = "{}".format(pid)

	map_str = ""

	if args["map_type"] == "londep" or args["map_type"] == "latdep":
		map_str = "_" + args["map_type"]

	npy_filename = os.path.join(_output_folder, base_filename + ".npy")
	xyz_filename = os.path.join(_output_folder, base_filename + map_str + ".xyz")
	grd_filename = os.path.join(_output_folder, base_filename + map_str + ".grd")
	ps_filename = os.path.join(_output_folder, base_filename + map_str + ".ps")

	rot_filename = os.path.join(_output_folder, base_filename + "rot.npy") 

	com_filename = os.path.join(_output_folder, base_filename + "com.npy") 

	ps_zoomout_filename = os.path.join(_output_folder, base_filename + map_str + "_zoom.ps")
	sh_filename = os.path.join(_output_folder, "plot.sh")
	station_filename = os.path.join(_output_folder, "station.txt")
	json_filename = os.path.join(_output_folder, base_filename + ".json")

	kml_filename = os.path.join(_output_folder, base_filename + ".kml")

	misfit_filename = os.path.join(_output_folder, "misfit.txt")
	misfitplot_filename = os.path.join(_output_folder, "misfit.pdf")

	#args["output_folder"] = output_folder
	args["base_filename"] = base_filename
	args["npy_filename"] = npy_filename
	

	#args["xyz_filename"] = xyz_filename

	if not os.path.exists(_output_folder):
		os.makedirs(_output_folder)

	already_created = os.path.exists(npy_filename) or os.path.exists(json_filename)
	print("already created: ", already_created)
		
	seed_lb_corner = (94, 3.5, 0)
	seed_grid_length = 3

	target_grid_length = 0.25

	if args["force"] or (not already_created):		
		# do initial search get best estimate,
		try:
			grid_output = arbitrary_search(args, seed_lb_corner, seed_grid_length, phase_info, station_info, tt, )
		except:
			raise ValueError("Faulty ID: {}".format(pid))
		# then draw a box around it to get the colour map
		# second gridsearch without the iterations

		if grid_output["best_z"] - 11 * args["DZ"]< 0:
			new_Z_start = 0
		elif grid_output["best_z"] + 11 * args["DZ"] > tt.shape[1]:
			new_Z_start = grid_output["best_z"] - 21 * args["DZ"]
		else:
			new_Z_start = grid_output["best_z"] - 10 * args["DZ"]
		
		if args["run_rotate"]:
			target_lb = (grid_output["best_x_c"] - target_grid_length/2, grid_output["best_y_c"] - target_grid_length/2, new_Z_start)		
		else:
			target_lb = (grid_output["best_x"] - target_grid_length/2, grid_output["best_y"] - target_grid_length/2, new_Z_start)		

		args["N_DX"] = 50
		args["N_Z"] = int(round(21/args["DZ"])) # 20km


		print(grid_output)

		print("Doing second gridsearch:")

		try:
			plot_grid = arbitrary_search(args, target_lb, target_grid_length, phase_info, station_info, tt, get_grid = True)
		except:
			raise ValueError("Second gridsearch, faulty ID: {}".format(pid))
		metadata_output = plot_grid[7]

		metadata_output["station_misfit"] = plot_grid[1]

		# save the results in a dictionary (dump to json later)
		#grid_output["station_misfit"] = plot_grid[1] # this is a dictionary
		metadata_output["lb_corner_x"] = (plot_grid[2][0])
		metadata_output["lb_corner_y"] = (plot_grid[2][1])
		metadata_output["lb_corner_z"] = (plot_grid[2][2])
		metadata_output["cell_size"] = (plot_grid[3])
		metadata_output["cell_n"] = (args["N_DX"] + 1)
		metadata_output["ID"] = pid
		metadata_output["cell_height"] = (args["DZ"])
		metadata_output["misfit_type"] = "Absolute difference between synthetic and observed travel times."


		if args["run_rotate"]:
			rotate_grid = plot_grid[5] # should probably just use a dictionary
			combined = plot_grid[6]

			with open(com_filename, "wb") as f:
				np.save(f, combined)
			
			with open(rot_filename, "wb") as f:
				np.save(f, rotate_grid)

		_grid = plot_grid[0]

		print(metadata_output)

		with open(npy_filename, "wb") as f:
			np.save(f, plot_grid[0])

		with open(json_filename, "w") as f:
			json.dump(metadata_output, f, indent = 4, cls=NumpyEncoder)
			# https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable

	
	else:
		with open(npy_filename,"rb") as f:
			_grid = np.load(f)

		with open(json_filename, "r") as f:
			metadata_output = json.load(f)

		if args["run_rotate"]:
			with open(rot_filename, "rb") as f:
				rotate_grid = np.load(f)
			
			with open(com_filename, "rb") as f:
				combined = np.load(f)


		target_lb = (metadata_output["lb_corner_x"], metadata_output["lb_corner_y"], metadata_output["lb_corner_z"])

	if args["no_plot"]:
		return 0

	L2 = _grid[:,:,:,0]
	indices = np.where(L2 == L2.min())

	print("Best grid indices: ", indices)
	_lons.append(metadata_output["best_x"])
	_lats.append(metadata_output["best_y"])


	# the plot limits will depend on the map type (map view, horizontal view)
	if args["map_type"] == "map":
		_lims = (target_lb[0], target_lb[0] + target_grid_length, target_lb[1], target_lb[1] + target_grid_length)
		_y_cell_size = metadata_output["cell_size"]
		_all_station_lims = (min(_lons) - target_grid_length/2, max(_lons) + target_grid_length/2, min(_lats) - target_grid_length/2, max(_lats) + target_grid_length/2)
		_output = L2[:,:,indices[2][0]]

	elif args["map_type"] == "londep":
		_lims = (target_lb[0], target_lb[0] + target_grid_length, target_lb[2], target_lb[2] + N_Z)
		_y_cell_size = 1
		_all_station_lims = (min(_lons) - target_grid_length/2, max(_lons) + target_grid_length/2, target_lb[2], target_lb[2] + N_Z)
		_output = L2[:, indices[1][0], :]

	elif args["map_type"] == "latdep":
		_lims = (target_lb[1], target_lb[1] + target_grid_length, target_lb[2], target_lb[2] + N_Z)
		_y_cell_size = 1
		_all_station_lims = (min(_lats) - target_grid_length/2, max(_lats) + target_grid_length/2, target_lb[2], target_lb[2] + N_Z)
		_output = L2[indices[0][0], :, :]


	preplot(_output, target_lb, metadata_output, _y_cell_size, _lims, _output_folder, base_filename, pers = args["map_type"], _type = map_str)

	gmt_plotter(grd_filename, ps_filename, sh_filename, station_list, station_info, _lims, station_filename, metadata_output, pid, _output_folder, map_type = args["map_type"], misfit_file = misfit_filename, misfitplot_file = misfitplot_filename, gmt_home = args["gmt_home"], )

	gmt_plotter(grd_filename, ps_zoomout_filename, sh_filename, station_list, station_info, _all_station_lims, station_filename, metadata_output, pid, _output_folder, map_type = args["map_type"], ticscale = "0.1", gmt_home = args["gmt_home"])

	_event_info = {pid+"gs":{
	"lat":metadata_output["best_y"], 
	"lon":metadata_output["best_x"], 
	"dep":metadata_output["best_z"],}
	}

	# write kml file, can just drag and drop into google earth
	kml_make.events(_event_info, kml_filename, "grid search", file_type = "direct")

	# run all the plotting, printing that is needed for rotated data:

	if args["run_rotate"]:

		grd_file, ps_file, sh_file = preplot(rotate_grid, target_lb, metadata_output, _y_cell_size, _lims, _output_folder, base_filename, _type = "_r", pers = "map")

		gmt_plotter(grd_file, ps_file, sh_file, station_list, station_info, _lims, station_filename, metadata_output, pid, _output_folder, map_type = "map", gmt_home = args["gmt_home"], rotate = True)

		grd_file, ps_file, sh_file = preplot(combined, target_lb, metadata_output, _y_cell_size, _lims, _output_folder, base_filename, _type = "_c", pers = "map")

		gmt_plotter(grd_file, ps_file, sh_file, station_list, station_info, _lims, station_filename, metadata_output, pid, _output_folder, map_type = "map", gmt_home = args["gmt_home"], rotate = True)


		
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

	#parser.add_argument("-eqt_csv")
	# parser.add_argument("-coord_file")
	# parser.add_argument("-coord_format", choices = ["real_hypophase", "hypoDD_loc"])
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
	parser.add_argument("-m", "--map_type", type = str, default = "map")

	parser.add_argument("-load_only", action = "store_true")
	parser.add_argument("-plot_mpl", action = "store_true")
	parser.add_argument("-show_mpl", action = "store_true")

	parser.add_argument("-r", "--run_rotate", action = "store_true")
	parser.add_argument("-ef", "--event_folder", type = str, default = "imported_figures/event_archive")

	parser.add_argument("-excl", "--exclude")

	parser.add_argument("-ap", "--append_text", type = str, help = "appends an underscore followed by the text in the flag, modifying the base name of the file", default = "")

	parser.add_argument('-gmt', "--gmt_home", type = str, default = "/home/zy/gmt")

	parser.add_argument('-np', "--no_plot", action = "store_true")



	#parser.add_argument("-layer_index", type = int, default = 0, choices = [0,1,2,3], help = "Refer to wiki. 0: L2 norm, 1: L2 stdev, 2: L1 norm, 3: L1 stdev")

	parser.add_argument('-dry', action = "store_true")

	parser.add_argument("-p", "--p_only", action = "store_true", help = "only consider P phases")
	parser.add_argument("-s", "--s_only", action = "store_true", help = "only consider S phases")

	parser.add_argument("-dt", "--time_remapping", type = str, help = "path to csv dataframe with remapped P and S arrivals (A and T0)")

	args = parser.parse_args()


	#parse_input(args.event_csv, arg)

	if args.tt_path:

		parse_input(
			args.station_info, 
			args.phase_json,	
			args.tt_path, 
			args.output_folder, 
			event_csv = args.event_csv, 
			event_id = args.event_id, 
			TT_DX = args.tt_dx,
			TT_DZ = args.tt_dz,
			DZ = args.dz,
			N_DX = args.n_dx,
			ZRANGE = args.zrange,
			load_only = args.load_only,
			plot_mpl = args.plot_mpl,
			show_mpl = args.show_mpl,
			force = args.force,
			map_type = args.map_type,
			event_folder = args.event_folder,
			run_rotate = args.run_rotate,
			exclude = args.exclude,
			append_text = args.append_text,
			p_only = args.p_only,
			s_only = args.s_only,
			time_remapping = args.time_remapping,
			gmt_home = args.gmt_home,
			no_plot = args.no_plot
			)


	elif args.convert_tt:
		convert_tt_file(args.convert_tt, args.output_tt)



	#parse_input(55, "station_info.dat", "real_postprocessing/5jul_assoc/5jul_aceh_phase.json", "/home/zy/cy1400-eqt/real_postprocessing/5jul_assoc/aceh_phase.dat", "real_hypophase", "gridsearch/tt_t.npy", dry_run = True)

	
	#convert_tt_file("gridsearch/zy_ttdb.txt")

