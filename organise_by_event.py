import pandas as pd
import shutil
import os
import argparse
import json
import datetime
from glob import glob
from pathlib import Path
import time
import subprocess

# load all events

# dry run

# then move

# for each id in the relocated 

# if i move i still have the original files on hard drive / my onedrive

def main(sac_csv, input_json, reloc_csv, output_folder):

	# sac_csv = "real_postprocessing/7jul_compiled_customfilter.csv"
	# input_json = 'real_postprocessing/aceh_phase.json'
	# reloc_csv = "real_postprocessing/5jul_reloc.csv"
	# output_folder = "event_archive"


	event_df = pd.read_csv(reloc_csv)

	#print(event_df["ID"])

	df = pd.read_csv(sac_csv)
	df["p_arrival_time"] = pd.to_datetime(df["p_arrival_time"])
	df["s_arrival_time"] = pd.to_datetime(df["s_arrival_time"])


	with open(input_json, 'r') as f:
		phase_dict = json.load(f)

	for i in ["YR", "MO", "DY", "HR", "MI"]:
		event_df[i].astype(int)

	#for index, row in event_df.iterrows():

			

	#print(event_df["timestamp"])
	#event_df["timestamp"] = pd.to_datetime(event_df["timestamp"])

	for index, row in event_df.iterrows():
	 	searcher(output_folder, int(row.ID), df, event_df, phase_dict)
	#searcher(5, df, event_df, phase_dict, dryrun = True)
	#header_writer(5, df, event_df, phase_dict)

	# i think the P and S times in the phase_dict are not reliable so just use the new origin
	# time from the relocated file
	#

def header_writer(pid, df, event_df, phase_dict):

	pass

	#print(file_list)

	# for each sac file, get the corresponding entry in the sac_csv, to get the P and S times



	#origin_time = event_df

	# glob the sac files in each folder, for each file, look up in a pandas dataframe using the ID and station name
	# since the ID will give a unique time
	# and for each file, load the P/S differential time from the aceh_phase.json file
	# also get the event location from pandas dataframe
	# 
	# 


	# write event location (lat lon depth) and apparently sac will calculate the 
	# reference date (if needed e.g. over 000000, reference time, B and E
	# 
	# retrieve lat, lon, depth from the reloc file

	# i could generate a bash file heheheheh to write the headers

	# there's probably a more elegant way to do this i.e. package this inside searcher so i don't have to run 


def csv_cutter():
	pass
	# for each folder in event_archive, put in a csv file with the metadat from relocated table 
	# for convenience 
	# 
	# 

def df_searcher_one_off(eqt_csv, phase_json):

	# please have the metadata as very succint bc it will take up storage space

	df = pd.read_csv(eqt_csv)

	df["p_arrival_time"] = pd.to_datetime(df["p_arrival_time"])
	df["s_arrival_time"] = pd.to_datetime(df["s_arrival_time"])

	o_df = pd.DataFrame(columns = ["datetime_str", "p_arrival_time", "s_arrival_time", "ID", "metadata"])

	o_c = 0

	with open(phase_json, 'r') as f:
		phase_dict = json.load(f)

	for event in phase_dict:

		print(event)

		_ts = phase_dict[event]["timestamp"]
		try:
			_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d %H:%M:%S.%f")
		except:
			_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d %H:%M:%S")


		for sta in phase_dict[event]["data"]:

			print(sta)

			_df = df[(df["station"] == sta)].copy()

			_p_arrival_time, _s_arrival_time = "", ""

			if 'P' in phase_dict[event]["data"][sta]:
				_p_arrival_time = _ts + datetime.timedelta(seconds = float(phase_dict[event]["data"][sta]['P']))

			if 'S' in phase_dict[event]["data"][sta]:
				_s_arrival_time = _ts + datetime.timedelta(seconds = float(phase_dict[event]["data"][sta]['S']))


			for index, row in _df.iterrows():
				if _p_arrival_time:
					_df.at[index, '_p_delta'] = (row.p_arrival_time - _p_arrival_time).total_seconds()

				if _s_arrival_time:
					_df.at[index, '_s_delta'] = (row.s_arrival_time - _s_arrival_time).total_seconds()		


			search_file_path = ""

			if _p_arrival_time:
				_p_df = _df[(_df['_p_delta'] < 1) & (_df['_p_delta'] > -1)].copy()

				try:
					assert _p_df.shape[0] == 1

				except:
					print(_p_df)
					assert False

				# check that there's only 1 match
				# 
				

				for index, row in _p_df.iterrows():
					phase_dict[event]["data"][sta]['station_P'] = row.p_arrival_time.to_pydatetime()

					if 'S' in phase_dict[event]["data"][sta]:
						phase_dict[event]["data"][sta]['station_S'] = row.s_arrival_time.to_pydatetime()

					o_df.at[o_c, "datetime_str"] = row.datetime_str
					o_df.at[o_c, "p_arrival_time"] = row.p_arrival_time
					o_df.at[o_c, "s_arrival_time"] = row.s_arrival_time
					o_df.at[o_c, "ID"] = event

					o_c += 1

			elif _s_arrival_time:
				_s_df = _df[(_df['_s_delta'] < 1) & (_df['_s_delta'] > -1)].copy()

				try:
					assert _s_df.shape[0] == 1

				except:
					print(_s_df)
					assert False

				for index, row in _s_df.iterrows():
					
					phase_dict[event]["data"][sta]['station_S'] = row.s_arrival_time.to_pydatetime()

					if 'P' in phase_dict[event]["data"][sta]:
						phase_dict[event]["data"][sta]['station_P'] = row.p_arrival_time.to_pydatetime()

					o_df.at[o_c, "datetime_str"] = row.datetime_str
					o_df.at[o_c, "p_arrival_time"] = row.p_arrival_time
					o_df.at[o_c, "s_arrival_time"] = row.s_arrival_time
					o_df.at[o_c, "ID"] = event

					o_c += 1

	with open("test.json", "w") as f:
		json.dump(phase_dict, f, indent = 4)

	o_df.to_csv("test.csv", index = False)





def df_searcher(df, _station_dict, _ts,):

	files_to_copy = []
	try:
		_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d %H:%M:%S.%f")
	except:
		_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d %H:%M:%S")
	for sta in _station_dict:
		#print(sta, uid)
		_p_arrival_time, _s_arrival_time = "", ""


		# the phase file (association by REAL) might have both P and S picks, or only one of them
		# either way, we only need either one of those picks to identify which event it was
		# this is because we are just trying to find the correct detection file along with the 'actual' arrival times

		if 'P' in _station_dict[sta]:
			_p_arrival_time = _ts + datetime.timedelta(seconds = float(_station_dict[sta]['P']))

		if 'S' in _station_dict[sta]:
			_s_arrival_time = _ts + datetime.timedelta(seconds = float(_station_dict[sta]['S']))

		_df = df[(df["station"] == sta)].copy()

			# search for event time
			
		for index, row in _df.iterrows():

			# manually compute the time difference zzz

			# this is quite inefficient because i could just match the year month minute hour etc
			# but like what if there are edge cases right..

			if _p_arrival_time:
				_df.at[index, '_p_delta'] = (row.p_arrival_time - _p_arrival_time).total_seconds()

			if _s_arrival_time:
				_df.at[index, '_s_delta'] = (row.s_arrival_time - _s_arrival_time).total_seconds()						

		#print(_ts, sta)

		# these should give an exact match, and only 1

		search_file_path = ""

		if _p_arrival_time:
			_p_df = _df[(_df['_p_delta'] < 1) & (_df['_p_delta'] > -1)].copy()
			#print(_p_df)

			try:
				assert _p_df.shape[0] == 1

			except:
				print(_p_df)
				assert False

			# check that there's only 1 match
			# 
			

			for index, row in _p_df.iterrows():
				search_file_path = os.path.join(row.local_file_root, 'sac_picks', row.datetime_str+"*C") 

				_station_dict[sta]['station_P'] = row.p_arrival_time.to_pydatetime()
				_station_dict[sta]['station_S'] = row.s_arrival_time.to_pydatetime()

				_station_dict[sta]['stla'] = row.station_lat
				_station_dict[sta]['stlo'] = row.station_lon
				#print(_station_dict[sta]['P'])

				# REMINDER: this will fail if e.g. not using multi to merge / want to search inside multi_X folder
				# i can't remember why it'll fail
				# probably because the arrival time may not be what it thinks it is
				# i.e. the merged arrival time is a median of all the collated picks


			# save search_file_path by just using iterrows again lol

		elif _s_arrival_time:
			_s_df = _df[(_df['_s_delta'] < 1) & (_df['_s_delta'] > -1)].copy()

			try:

				assert _s_df.shape[0] == 1

			except:
				print(_s_df)
				assert False

			for index, row in _s_df.iterrows():
				search_file_path = os.path.join(row.local_file_root, 'sac_picks', row.datetime_str+"*C") 

				_station_dict[sta]['station_P'] = row.p_arrival_time.to_pydatetime()
				_station_dict[sta]['station_S'] = row.s_arrival_time.to_pydatetime()
				_station_dict[sta]['stla'] = row.station_lat
				_station_dict[sta]['stlo'] = row.station_lon
		#print(search_file_path)
		_files_to_copy = [str(p) for p in glob(search_file_path)] # 3 channel files

		files_to_copy.extend(_files_to_copy)

	return {"files_to_copy": files_to_copy, "_station_dict": _station_dict}

def searcher(output_folder, uid, df, event_df, phase_dict, dryrun = False):

	# this will only look for and then copy files if they aren't already copied
	# 

	i = uid

	padded_id = (str(i).zfill(6))
	row_index = event_df[event_df["ID"] == uid].index[0]

	print("current row:", row_index, uid)
	print("{}-{}-{}-{}-{}-{}".format(
			int(event_df.at[row_index, 'YR']), 
			int(event_df.at[row_index, 'MO']), 
			int(event_df.at[row_index, 'DY']), 
			int(event_df.at[row_index, 'HR']), 
			int(event_df.at[row_index, 'MI']), 
			event_df.at[row_index, 'SC']))

	try:
		origin_time = datetime.datetime.strptime("{}-{}-{}-{}-{}-{:.6f}".format(
			int(event_df.at[row_index, 'YR']), 
			int(event_df.at[row_index, 'MO']), 
			int(event_df.at[row_index, 'DY']), 
			int(event_df.at[row_index, 'HR']), 
			int(event_df.at[row_index, 'MI']), 
			event_df.at[row_index, 'SC']), 
			"%Y-%m-%d-%H-%M-%S.%f")

	except:
		if event_df.at[row_index, 'SC'] == 60.0:
			origin_time = datetime.datetime.strptime("{}-{}-{}-{}-{}-{}".format(int(event_df.at[row_index, 'YR']), int(event_df.at[row_index, 'MO']), int(event_df.at[row_index, 'DY']), int(event_df.at[row_index, 'HR']), int(event_df.at[row_index, 'MI']), "0.0"), "%Y-%m-%d-%H-%M-%S.%f")
			origin_time += datetime.timedelta(minutes = 1)

		else:
			raise ValueError

	#origin_time = .values[0]
	print("origin time", origin_time)

	#print(event_df.loc[event_df["ID"] == uid, "timestamp"])



	dest_folder = os.path.join(output_folder, padded_id)




	_station_dict = phase_dict[padded_id]['data']

	_ts = (phase_dict[padded_id]['timestamp'])


	bash_str = "#!/bin/bash\n"
	output_file = "cat_header_writer.sh"

	# function call: search here

	search_output = df_searcher(df, _station_dict, _ts)


	files_to_copy = search_output["files_to_copy"]
	_station_dict = search_output["_station_dict"]


	if not os.path.exists(dest_folder) and not dryrun:
		os.makedirs(dest_folder)

	for file in files_to_copy:

		basename = file.split("/")[-1]
		dest_path = os.path.join(dest_folder, basename)

		if os.path.exists(dest_path):
			print("File already exists, not copying : {}".format(dest_path))

		else:
			if dryrun:
				
				print("source file: {}".format(file))
				print("dest folder: {}".format(dest_folder))
			else:
				shutil.copy(file, dest_folder)


		# write headers here

		output_date_str = datetime.datetime.strftime(origin_time, "%Y %j %H %M %S %f")[:-3] # drop the last 3 zeros

		print(output_date_str)

		"""
			Setting of kzdate, kztime and iztype is eqivalent to the following SAC commands:
			SAC> ch o gmt 1994 160 00 33 16 230
			SAC> ch iztype IO
			SAC> ch allt (-1.0 * &1,o)
		"""

		# get event location

		_sta = basename.split(".")[0]

		station_lat, station_lon = _station_dict[_sta]['stla'], _station_dict[_sta]['stlo']

		event_lat, event_lon, event_depth = event_df.loc[event_df["ID"] == uid, "LAT"].values[0], event_df.loc[event_df["ID"] == uid, "LON"].values[0], event_df.loc[event_df["ID"] == uid, "DEPTH"].values[0]

		bash_str += "printf 'r {}\\nch o gmt {}\\nch iztype IO\\nch allt (-1.0 * &1,o)\\nch evla {} evlo {} evdp {} stla {} stlo {}\\nwh\\nq\\n' | sac\n".format(dest_path, output_date_str, event_lat, event_lon, event_depth, station_lat, station_lon)

		bash_str += "printf 'r {}\\nwh\\nq\\n' | sac\n".format(dest_path) # this is for calculating DIST etc


	with open(output_file, 'w') as f:
		f.write(bash_str)
	time.sleep(1)
	os.chmod(output_file, 0o775)
	time.sleep(1)

	subprocess.call(["./{}".format(output_file)])

	

	# start moving stuff to folder

	# check if stuff is already in destination folder
	# if not, attempt to move


if __name__ == "__main__":

	# parser = argparse.ArgumentParser()

	# parser.add_argument("eqt_csv")
	# parser.add_argument("phase_json")
	# parser.add_argument("reloc_csv")
	# parser.add_argument("output_folder")

	# args = parser.parse_args()

	# main(args.eqt_csv, args.phase_json, args.reloc_csv, args.output_folder)

	#df_searcher_one_off("gridsearch/remap7jul_compiled_customfilter.csv", "gridsearch/remap_phase.json")

	df_searcher_one_off("real_postprocessing/for_gs/7jul_compiled_customfilter.csv","real_postprocessing/for_gs/remap_phase.json")