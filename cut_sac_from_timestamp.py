"""
this script aims to match existing timestamps of detections (EQT) with the original SAC files, hence linking the two

creates a column "source_file" so we know where to look. this has the wildcard character so you can load all 3C files

also sets the local file root to the "output folder" so you can later run replot_eqt.py and then organise_by_event.py

"""


from subprocess import check_output
import datetime
import pandas as pd
import argparse
import json
import glob
import os


"""
sac_file_checker

Matches detection time stamps to the original SAC file

Inputs:
- `input_csv': EQT outputs (filter the way you want it)

- `sac_csv': The sac file .csv that is generated the `make_sac_csv -msc' flag on multi_station.py
	This file has the associated start and end times, along with file paths for all the SAC files it has found

- `real_json': Collated from `collect_latlon.py', has phase information along with event information

- `real_csv': Collated from `collect_latlon.py' but only has event information. This was just used to iterate over IDs


Outputs:
- `output_csv': the input_csv but now with the matched file_name
- `output_folder': the folder to create to store all the event names

"""
def sac_file_checker(input_csv, output_csv, sac_csv, ):

	s_df = pd.read_csv(sac_csv)

	s_df = s_df.dropna(subset=["kzdate", "kztime"])


	df = pd.read_csv(input_csv)
	df["event_start_time"] = pd.to_datetime(df["event_start_time"])

	for index, row in s_df.iterrows():
		s_df.at[index, "start_dt"] = datetime.datetime.strptime("{} {}".format(row.kzdate, row.kztime), "%Y/%m/%d %H:%M:%S.%f")

	for index, row in df.iterrows():
		print(index)
		# get station
		jday = int(datetime.datetime.strftime(row.event_start_time, "%j"))

		_df = s_df[(s_df["station"] == row.station)]

		if len(_df) == 0:
			continue


		for s_index, s_row in _df.iterrows():
			_df.at[s_index, "is_within"] = (((row.event_start_time - s_row.start_dt).total_seconds()) < s_row.E) and (((row.event_start_time - s_row.start_dt).total_seconds()) > s_row.B) 


		try:
			_fdf = _df[(_df["is_within"] == True)]
		except:
			print(row.station, row.jday, "error")

		search_term = _fdf["filepath"].iloc[0]

		df.at[index, "source_file"] = search_term



	df = df.merge(s_df, how = "left", left_on = "source_file", right_on = "filepath", suffixes = ("", "_sac")) 

	for index, row in df.iterrows():
		for x in [".EHE.", ".EHN.", ".EHZ."]:
			if x in row.source_file:
				search_term = row.source_file.replace(x, ".EH*.")
				break
		df.at[index, "source_file"] = search_term


	df.to_csv(output_csv, index = False)



# this input_csv is the previous output i.e. EQT output but with the source file column
def choose_event_wf(real_csv, real_json, input_csv, output_csv, output_json):

	# real_csv: association output

	# make a dataframe in memory? and then write the text files with the script for cutting all the sac files 
	
	# first filter for waveforms that are associated with events using the json

	# next merge in the code from replot_eqt.py

	eqt_df = pd.read_csv(input_csv)

	eqt_df["event_start_time"] = pd.to_datetime(eqt_df["event_start_time"])
	eqt_df["p_arrival_time"] = pd.to_datetime(eqt_df["p_arrival_time"])
	eqt_df["s_arrival_time"] = pd.to_datetime(eqt_df["s_arrival_time"])

	with open(real_json, "r") as f:
		phase_dict = json.load(f)

	
	real_df = pd.read_csv(real_csv)

	for index, row in real_df.iterrows():
		padded_id = str(int(row.ID)).zfill(6)

		_station_dict = phase_dict[padded_id]['data']

		_ts = (phase_dict[padded_id]['timestamp'])

		bash_str = "#!/bin/bash\n"
		output_file = "cat_header_writer.sh"

		# function call: search here

		target_indices, updated_station_dict = df_searcher(eqt_df, _station_dict, _ts)

		for i in target_indices:
			eqt_df.at[i, "ID"] = row.ID


		phase_dict[padded_id]['data'] = updated_station_dict



		# use station dict information to update the dataframe, then save the dataframe first
		# this is so you don't have to relink the info every time for the waveforms 
	
	eqt_df.to_csv(output_csv, index = False)

	with open(output_json, "w") as f:
		json.dump(phase_dict, f, indent = 4)



	#files_to_copy = search_output["files_to_copy"]



def df_searcher(df, _station_dict, _ts,):

	files_to_copy = []
	try:
		_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d %H:%M:%S.%f")
	except:
		_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d %H:%M:%S")

	target_indices = []
	
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

			
		for index, row in _df.iterrows():

			if _p_arrival_time:
				_df.at[index, '_p_delta'] = (row.p_arrival_time - _p_arrival_time).total_seconds()

			if _s_arrival_time:
				_df.at[index, '_s_delta'] = (row.s_arrival_time - _s_arrival_time).total_seconds()						

		# these should give an exact match, and only 1

		if _p_arrival_time:
			_p_df = _df[(_df['_p_delta'] < 1) & (_df['_p_delta'] > -1)].copy()
			print(_p_df)

			try:
				assert _p_df.shape[0] == 1

			except:
				print("Duplicates found for above p_df")

			for index, row in _p_df.iterrows():
				#search_file_path = os.path.join(row.local_file_root, 'sac_picks', row.datetime_str+"*C") 

				_station_dict[sta]['station_P'] = row.p_arrival_time.to_pydatetime()
				_station_dict[sta]['station_S'] = row.s_arrival_time.to_pydatetime()

				_station_dict[sta]['stla'] = row.station_lat
				_station_dict[sta]['stlo'] = row.station_lon

				target_indices.append(index)

				break
				#print(_station_dict[sta]['P'])

				# REMINDER: this will fail if e.g. not using multi to merge / want to search inside multi_X folder
				# i.e. the merged arrival time is a median of all the collated picks


		elif _s_arrival_time:
			_s_df = _df[(_df['_s_delta'] < 1) & (_df['_s_delta'] > -1)].copy()

			try:
				assert _s_df.shape[0] == 1

			except:
				print("Duplicates found for above p_df")

			for index, row in _s_df.iterrows():
				#search_file_path = os.path.join(row.local_file_root, 'sac_picks', row.datetime_str+"*C") 

				_station_dict[sta]['station_P'] = row.p_arrival_time.to_pydatetime()
				_station_dict[sta]['station_S'] = row.s_arrival_time.to_pydatetime()
				_station_dict[sta]['stla'] = row.station_lat
				_station_dict[sta]['stlo'] = row.station_lon

				target_indices.append(index)

				break
		#print(search_file_path)
		#_files_to_copy = [str(p) for p in glob(search_file_path)] # 3 channel files

		#files_to_copy.extend(_files_to_copy)

	# should return a dataframe, then merge the dataframes in memory

	return {"target_indices": target_indices, "_station_dict": _station_dict}

	#return {"files_to_copy": files_to_copy, "_station_dict": _station_dict}


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("eqt_csv", help = "EQT outputs (filtered the way you want it)")
	ap.add_argument("real_csv", help = "Collated from collect_latlon. Only has event information. Used to iterate over IDs.")
	ap.add_argument("real_json", help = "Collated from collect_latlon, has phase and event information.")
	ap.add_argument("output_csv", help = "Patched EQT output csv with source file paths and event ID")
	ap.add_argument("output_json", help = "Patched json with timestamps for arrival times")
	#ap.add_argument("sac_csv", help = "Generated by -msc flag from multi_station, with start and end times for each original SAC file.")
	#ap.add_argument("output_folder", help = "Folder to create new event archive inside.")

	args = ap.parse_args()

	#sac_file_checker(args.input_csv, args.output_csv, args.sac_csv, )

	choose_event_wf(args.real_csv, args.real_json, args.eqt_csv, args.output_csv, args.output_json)

	#def choose_event_wf(real_csv, real_json, input_csv, output_csv, output_json):