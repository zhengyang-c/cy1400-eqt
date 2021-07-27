import pandas as pd
from pathlib import Path
import datetime
import json
import numpy as np
import os
from copy import copy
# select ID from csv --> get station and times from .json --> get path to .SAC files from the compiled event table --> plot SAC files

# future: query directly from EOS_DATA folder

def get_stations():
	input_csv = "7jul_compiled_customfilter.csv"
	input_json = 'aceh_phase.json'

	df = pd.read_csv(input_csv)

	output_bash = "test.sh"

	#output_str = "#!/bin/bash\nPSFILE=test.ps\n\nWIDTH=-W0.5\nY_HEIGHT=-M2\nPROJ=-JX10c/5c\nLIM=-R-10/50/-2/2\nFORMAT='-Baf -BweSn -Fr'\nTIME_SHIFT='-T+t-2'"

	df["p_arrival_time"] = pd.to_datetime(df["p_arrival_time"])
	df["s_arrival_time"] = pd.to_datetime(df["s_arrival_time"])

	with open(input_json, 'r') as f:
		phase_dict = json.load(f)


	id_list = [33, 52, 55]
	#id_list = [402, 443, 449]

	# deep: 33, 52, 55

	# shallow: 402,  443, 449

	for i in id_list:
		print("-------------------------------------------")
		padded_id = (str(i).zfill(6))

		_ts = (phase_dict[padded_id]['timestamp'])

		_station_dict = {}

		for x in phase_dict[padded_id]['data']:
			if x[0] not in _station_dict:
				_station_dict[x[0]] = {}
			_station_dict[x[0]][x[3]] = x[1] # natural support for only P or only S picks

		#print(_ts,_station_dict)
		_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d %H:%M:%S.%f")

		for sta in _station_dict:


			_p_arrival_time, _s_arrival_time = "", ""

			if 'P' in _station_dict[sta]:
				_p_arrival_time = _ts + datetime.timedelta(seconds = float(_station_dict[sta]['P']))

			if 'S' in _station_dict[sta]:
				_s_arrival_time = _ts + datetime.timedelta(seconds = float(_station_dict[sta]['S']))

			_df = df[(df["station"] == sta)].copy()

				# search for event time
				
			for index, row in _df.iterrows():

				# manually compute the time difference zzz

				# this is quite efficient because i could just match the year month minute hour etc
				# but like what if there are edge cases right..
				# 
				

				if _p_arrival_time:
					_df.at[index, '_p_delta'] = (row.p_arrival_time - _p_arrival_time).total_seconds()

				if _s_arrival_time:
					_df.at[index, '_s_delta'] = (row.p_arrival_time - _p_arrival_time).total_seconds()						

			#print(_ts, sta)

			# these should give an exact match, and only 1

			search_file_path = ""

			if _p_arrival_time:
				_p_df = _df[(_df['_p_delta'] < 1) & (_df['_p_delta'] >= 0)].copy()
				#print(_p_df)

				assert _p_df.shape[0] == 1

				# check that there's only 1 match
				# 
				

				for index, row in _p_df.iterrows():
					search_file_path = os.path.join(row.local_file_root, 'sac_picks', row.datetime_str+"*C") 
					print(_station_dict[sta]['P'])

					# REMINDER: this will fail if e.g. not using multi to merge / want to search inside multi_X folder


				# save search_file_path by just using iterrows again lol

			elif _s_arrival_time:
				_s_df = _df[(_df['_s_delta'] < 1) & (_df['_s_delta'] >= 0)].copy()

				assert _s_df.shape[0] == 1

				for index, row in _s_df.iterrows():
					search_file_path = os.path.join(row.local_file_root, 'sac_picks', row.datetime_str+"*C") 
					print(_station_dict[sta]['S'])

			print(search_file_path)


		# for each station, look in the df (filter by station, then filter by timestamp to within +/- 1s of the origin time + p_arrival)

		# report failures just in case




def convert_phase():

	input_file = "aceh_phase.dat"
	output_file = "aceh_phase.json"

	df = pd.DataFrame()

	def parse(x):
		contents = [y.strip() for y in x[1:].split(" ") if y != ""]

		return contents

	all_phases = {}

	with open(input_file, 'r') as f:

		_station_list = []
		row_counter = 0
		headers = ['year', 'month', 'day', 'hour', 'min', 'sec', 'lat_guess', 'lon_guess', 'dep_guess']

		for c, line in enumerate(f):

			if line[0] == "#":
				metadata = parse(line)

				_id = metadata[-1]

				all_phases[_id] = {}

				for i in range(9):
					all_phases[_id][headers[i]] = metadata[i]

				all_phases[_id]['timestamp'] = str(datetime.datetime.strptime('-'.join(metadata[0:6]), "%Y-%m-%d-%H-%M-%S.%f"))
				all_phases[_id]['data'] = []


			else:
				_data = [x.strip() for x in line.split(" ") if x != ""]

				all_phases[_id]['data'].append(_data) 

	for event_id in all_phases:
		_station_dict = {}

		for x in all_phases[event_id]['data']:
			if x[0] not in _station_dict:
				_station_dict[x[0]] = {}
			_station_dict[x[0]][x[3]] = x[1] # natural support for only P or only S picks

		all_phases[event_id]['data'] = _station_dict


	with open(output_file, 'w') as f:

		json.dump(all_phases, f, indent = 2)

	#df.to_csv(output_file, index = False)
	# build a table, with a column for stations,
	# separate each station by like some character




# for each ID, get the timestamp, get the list of stations + their original times and search for the waveforms
convert_phase()