# fill this in with the common functions so i can clean up my shitty code 

import os
import json
import pandas as pd
import datetime
import math
from pathlib import Path
import numpy as np

def csv_naive_filter(csv_path, list_of_timestamps):
	df = pd.read_csv(csv_path)

	df["event_ts"] = pd.to_datetime(df["event_start_time"])

	for index, row in df.iterrows():
		df.at[index, "keep"] = "{}.{}".format(row["station"], datetime.datetime.strftime(row["event_ts"], "%Y.%j.%H%M%S")) in list_of_timestamps

	df = df[df.keep == True]

	return df

def csv_indexed_filter(csv_path, list_of_timestamps):
	df = pd.read_csv(csv_path)

	df["event_ts"] = pd.to_datetime(df["event_start_time"])

	for index, row in df.iterrows():
		test_str = "{}.{}".format(row["station"], datetime.datetime.strftime(row["event_ts"], "%Y.%j.%H%M%S"))
		df.at[index, "keep"] = test_str in list_of_timestamps

		try:
			_manualindex = int(list_of_timestamps.index(test_str))
			df.at[index, "input_index"] = _manualindex
		except:
			df.at[index, "input_index"] = None

	df = df[df.keep == True]

	return df


def centre_bin(bins):
	return (bins[1:] + bins[:-1])/2

def match_gradings(df, grade_tracename, grades):
	"""
	Given a txt file in manual (giving the grades for each trace as identified in its file name),
	and a data file, match each grade to the waveform in the pd df
	
	:param      df:               filtered pandas dataframe
	:type       df:               { type_description }
	:param      grade_tracename:  A list of grades and tracenames, taken from the manual folder
	:type       grade_tracename:  { type_description }
	:param      grades:           The grades
	:type       grades:           { type_description }
	"""

	for c, tn in enumerate(grade_tracename):
		tn = ".".join(tn.split(".")[1:])
		_dfindex = df[df.ts_str == tn].index.values[0]

		df.at[_dfindex, "grade"] = grades[c].upper()

	return df


def load_graded_from_file_structure(sac_folder, csv_file):
	# returns matched df (with the file structure) + puts their grade there

	grades = []
	filenames = []

	for p in Path(sac_folder).rglob("*png"):
		_p = str(p)

		_grade = _p.split("/")[-2]

		grades.append(_grade)

		filenames.append(".".join(_p.split("/")[-1].split(".")[:-1])) # get the filename without the extension

		# there is defn a better way to do this
	#print(filenames)
	df = csv_indexed_filter(csv_file, filenames)

	for index, row in df.iterrows():
		df.at[index, "grade"] = grades[int(row["input_index"])] 

	return df


def load_from_grades(known_picks):
	"""
	returns a tuple of (a list of tracenames (the timestamp), and the grade). 
	this should be depreciated in favour of reading directly from the sac_picks folder as a source of picks
	
	:param      known_picks:  The known picks
	:type       known_picks:  { type_description }
	"""

	graded_traces = []
	grades = []

	with open(known_picks, "r") as f:
		for line in f:
			_x = line.strip().split(",")
			graded_traces.append(_x[0])
			grades.append(_x[1])

	return (graded_traces, grades)

def load_with_path_and_grade(csv_file, source_folder):
	sac_pathname = [str(path) for path in Path(source_folder).rglob('*.png')]

	sac_tracename = [x.split("/")[-1].split(".png")[0] for x in sac_pathname]

	folder_df = pd.DataFrame(np.column_stack([sac_pathname, sac_tracename]), columns = ["pathname", "wf"])

	for index, row in folder_df.iterrows():
		folder_df.at[index, 'grade'] = row.pathname.split("/")[-2]

	# load the csv file, make a new column for file name, do pd.merge to match the two of the


	csv_df = pd.read_csv(csv_file)
	csv_df['event_dt'] = pd.to_datetime(csv_df.event_start_time)


	for index, row in csv_df.iterrows():
		csv_df.at[index, 'wf'] = "{}.{}".format(row.station, datetime.datetime.strftime(row.event_dt, "%Y.%j.%H%M%S"))

	#print(csv_df)

	new_df = csv_df.merge(folder_df, on = "wf")

	return new_df

def parse_xy_lines(input_file):

	all_lines = []

	b_c = 0 # bracket counter

	_line = []

	with open(input_file, 'r') as f:
		for line in f:
			if ">" in line.strip():
				b_c += 1

				if len(_line) > 0:
					all_lines.append(_line)

				_line = []	

				continue
			if b_c % 2:
				#print(line.strip().split(" "))
				try:
					_lon, _lat = line.strip().split(" ")
				except:
					_lon, _lat = line.strip().split("\t")
				_line.append((float(_lon), float(_lat)))

	return all_lines



def parse_station_info(input_file):
	# 'reusing functions is bad practice' yes haha

	station_info = {}

	with open(input_file, 'r') as f:
		for line in f:
			#print(line)
			try:
				data = [x for x in line.strip().split("\t") if x != ""]
			except:
				data = [x for x in line.strip().split(" ") if x != ""] 

			sta = data[0]
			lon = data[1]
			lat = data[2]


			station_info[sta] = {"lon": float(lon), "lat": float(lat)}	

			if len(data) == 4:
				elv = data[3]
				station_info[sta]["elv"] = float(elv)

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

	elif _format == "event_csv":
		df = pd.read_csv(file_name)

		for index, row in df.iterrows():
			for _i in ["ID", "id", "cat_index"]:
				if _i in df.columns:
					_id = str(int(row[_i])).zfill(6)
					event_info[_id] = {}
					break
			for _i in ["lat", "LAT", "event_lat", "ev_lat"]:
				if _i in df.columns:
					event_info[_id]["lat"] = row[_i]
					break

			for _i in ["lon", "LON", "event_lon", "ev_lon"]:
				if _i in df.columns:
					event_info[_id]["lon"] = row[_i]
					break

			for _i in ["DEPTH", "depth", "dep", "DEP", "event_depth", "event_dep"]:
				if _i in df.columns:
					event_info[_id]["dep"] = row[_i]
					break


	else:
		raise ValueError("Format {} not supported, please consult the wiki".format(_format))

	return event_info

def split_csv(input_csv, output_csv_root, N = 4):

	df = pd.read_csv(input_csv)

	remainder = len(df) % 4
	n_rows_per_file = len(df) // 4



def theoretical_misfit(tt, station_info, target_ID, df, station_metadata):
	"""
	station_info
	tt path 
	real_json (with travel time and phases)
	real_csv
	ID
	"""

	print(target_ID)

	TT_DX = 1
	TT_DZ = 1 
	TT_NX = tt.shape[0]
	TT_NZ = tt.shape[1]

	station_metadata = parse_station_info(station_metadata)

	# key ordering is immutable: throw into array and let numpy handle it

	dists = []
	depths = []

	_lon = df[df["ID"] == target_ID]["LON"].tolist()[0]
	_lat = df[df["ID"] == target_ID]["LAT"].tolist()[0]
	_dep = df[df["ID"] == target_ID]["DEPTH"].tolist()[0]

	# compute station distances for all stations
	for sta in station_info:
		_dist = dx((_lon, _lat), (station_metadata[sta]["lon"], station_metadata[sta]["lat"]))
		dists.append(_dist)
		depths.append(_dep)

	dists = np.array(dists)
	depths = np.array(depths)

	dist_indices = np.array([int(round(x)) for x in dists/TT_DX]) # for table interpolation
	depth_indices = np.array([int(round(x)) for x in depths/TT_DZ]) # for table interpolation

	dist_deltas = dists - dist_indices * TT_DX
	depth_deltas = depths - depth_indices * TT_DZ

	dist_grad_P = []
	dist_grad_S = []

	depth_grad_P = []
	depth_grad_S = []

	tt_P = []
	tt_S = []

	for _c, _i in enumerate(dist_indices):
		if _i + 1 > TT_NX:
			_indices = np.array([_i - 1, _i])
		elif _i - 1 < 0:
			_indices = np.array([_i, _i + 1])
		else:
			_indices = np.array([_i - 1, _i, _i + 1]) 
		

		_Y_P = [tt[_x][depth_indices[_c]][0] for _x in _indices]
		_Y_S = [tt[_x][depth_indices[_c]][1] for _x in _indices]

		tt_P.append(tt[_i][depth_indices[_c]][0])
		tt_S.append(tt[_i][depth_indices[_c]][1])

		dist_grad_P.append(ip((_indices) * TT_DX, _Y_P))
		dist_grad_S.append(ip((_indices) * TT_DX, _Y_S))

	for _c, _i in enumerate(depth_indices):
		if _i + 1 > TT_NZ:
			_indices = np.array([_i - 1, _i])
		elif _i - 1 < 0:
			_indices = np.array([_i, _i + 1])
		else:
			_indices = np.array([_i - 1, _i, _i + 1]) 

		_Y_P = [tt[dist_indices[_c]][_x][0] for _x in _indices]
		_Y_S = [tt[dist_indices[_c]][_x][1]for _x in _indices]

		depth_grad_P.append(ip((_indices) * TT_DZ, _Y_P))
		depth_grad_S.append(ip((_indices) * TT_DZ, _Y_S))

	dist_grad_P = np.array(dist_grad_P)
	dist_grad_S = np.array(dist_grad_S)
	depth_grad_P = np.array(depth_grad_P)
	depth_grad_S = np.array(depth_grad_S)

	tt_P = np.array(tt_P)
	tt_S = np.array(tt_S)

	tt_P += dist_grad_P * dist_deltas
	tt_S += dist_grad_S * dist_deltas
	tt_P += depth_grad_P * depth_deltas
	tt_S += depth_grad_S * depth_deltas
	
	output_times = {}

	for c, sta in enumerate(station_info):
		output_times[sta] = {
			"tt_P": tt_P[c],
			"tt_S": tt_S[c]
		} 

	return output_times

def dx(X1, X2):
	from obspy.geodetics import gps2dist_azimuth
	"""
	
	takes in two coordinate tuples (lon, lat), (lon, lat) returning their distance in kilometres
	gps2dist_azimuth also returns the azimuth but i guess i don't need that yet
	it also returns distances in metres so i just divide by 1000

	the order doesn't matter
	
	:param      X1:   The x 1
	:type       X1:   { type_description }
	:param      X2:   The x 2
	:type       X2:   { type_description }

	"""

	print(X1, X2)
	return gps2dist_azimuth(X1[1], X1[0], X2[1], X2[0])[0] / 1000


def ip(X, Y):
	if len(X) == 3:

		# arithmetic average of in between gradients to approximate gradient at midpoint

		return 0.5 * ((Y[2] - Y[1])/(X[2] - X[1]) + (Y[1] - Y[0])/(X[1] - X[0]))

	if len(X) == 2:
		return (Y[1] - Y[0])/(X[1] - X[0])

def pbs_writer(n_nodes, job_name, paths, n_cores = 1, walltime_hours = 80):
	output_pbs = os.path.join(paths["pbs_folder"], job_name +".pbs")

	project_code = 'eos_shjwei'

	with open(output_pbs, "w") as f:
		if n_nodes == 1:
			pass
		else:
			f.write("#PBS -J 0-{:d}\n".format(n_nodes - 1))

		f.write("#PBS -N {}\n#PBS -P {}\n#PBS -q q32\n#PBS -l select={}:ncpus={}:mpiprocs=32:mem=16gb -l walltime={}:00:00\n".format(job_name, project_code, n_nodes, n_cores, walltime_hours))
		f.write("#PBS -e log/pbs/{0}/error.log \n#PBS -o log/pbs/{0}/output.log\n".format(job_name))

		if n_nodes == 1:
			f.write("{1}/runtime_scripts/{0}/0/run.sh\n".format(job_name, paths["pbs_folder"]))
		else:
			f.write("{1}/runtime_scripts/{0}/${{PBS_ARRAY_INDEX}}/run.sh\n".format(job_name, paths["pbs_folder"]))


if __name__ == "__main__":
	pass