"""
- run multi_station on the root folder to get a master SAC file
- run cut_sac to link the rereal catalogue to the eqt picks
- then link to sac
- also write the filter csv option to be included with the -w write flag


in parallel:
do mpl visualisations for the other large events along the creeping section
add alpha so you can see if events are being hidden under others

compare w locked section

and then start looking at the seiscloud papers etc




this script aims to match existing timestamps of detections (EQT) with the original SAC files, hence linking the two

creates a column "source_file" so we know where to look. this has the wildcard character so you can load all 3C files

also sets the local file root to the "output folder" so you can later run replot_eqt.py and then organise_by_event.py

"""


from subprocess import check_output
import datetime
import pandas as pd
import argparse
import json
import time
import sys
import os
from utils import parse_station_info

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


def choose_event_wf(real_csv, real_json, input_csv, output_csv, output_json, sac_csv, output_folder, station_file, eqt_to_event = False, eqt_to_sac = False, write = False, filter_csv = ""):
	if eqt_to_event:
		eqt_df = pd.read_csv(input_csv)
	else:
		eqt_df = pd.read_csv(output_csv)

	if station_file:
		station_info = parse_station_info(station_file)

	eqt_df["event_start_time"] = pd.to_datetime(eqt_df["event_start_time"])
	eqt_df["p_arrival_time"] = pd.to_datetime(eqt_df["p_arrival_time"])
	eqt_df["s_arrival_time"] = pd.to_datetime(eqt_df["s_arrival_time"])


	real_df = pd.read_csv(real_csv)
	real_df["timestamp"] = pd.to_datetime(real_df["timestamp"])


	if eqt_to_event:
		with open(real_json, "r") as f:
			phase_dict = json.load(f)

		for index, row in real_df.iterrows():
			padded_id = str(int(row.ID)).zfill(6)

			_station_dict = phase_dict[padded_id]['data']
			_ts = (phase_dict[padded_id]['timestamp'])

			target_indices, updated_station_dict = df_searcher(eqt_df, _station_dict, _ts)

			for i in target_indices:
				eqt_df.at[i, "ID"] = row.ID
			phase_dict[padded_id]['data'] = updated_station_dict
		
		eqt_df.to_csv(output_csv, index = False)

		with open(output_json, "w") as f:
			json.dump(phase_dict, f, indent = 4, default = str)

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	eqt_df = eqt_df.dropna(subset = ['ID'])
	cut_str = "#!/bin/bash\n"
	header_str = "#!/bin/bash\n"

	cut_file = os.path.join(output_folder, "cut.sh")
	header_file = os.path.join(output_folder, "header.sh")

	if eqt_to_sac:
		s_df = pd.read_csv(sac_csv)

		# if ("kzdate" in s_df.columns) and ("kztime" in s_df.columns):
		# 	s_df = s_df.dropna(subset=["kzdate", "kztime"])

		eqt_df.drop(['sac_start_time'], axis = 1)
		eqt_df["source_file"] = eqt_df["source_file"].astype("object")

		s_df['sac_start_dt'] = pd.to_datetime(s_df['sac_start_dt'])
		s_df['sac_end_dt'] = pd.to_datetime(s_df['sac_end_dt'])


		for index, row in eqt_df.iterrows():
			print(row.station)
			# get station
			jday = int(datetime.datetime.strftime(row.event_start_time, "%j"))

			_df = s_df[(s_df["station"] == row.station)]
			# station dataframe
			if len(_df) == 0:
				station_remap = {"A02": "A54", "A10": "TG03", "GE01": "GN01", "GE16": "GN16", "GE10": "GN10", "GE07":"GN07", "AS09":"AN09", "GE13":"GN13", "TA02":"TN02", "MA01": "MN01", "GE15":"GN16", "GM05":"GM55"}
				rev_map = {v:k for k,v in station_remap.items()}

				try:
					_station = rev_map[row.station]
					_df = s_df[(s_df["station"] == _station)]
					print("attempting fix new station", _station)
					assert len(_df) != 0

				except:
					print("unable to fix via mapping, skipping")
					print(row.station, row.timestamp)
					continue

			_fdf = _df[(_df["sac_start_dt"] < row.event_start_time) & (_df["sac_end_dt"] > row.event_start_time )]

			if len(_fdf) == 0 :
				print(_df)
				print(row.station, "error for")
				print(index, row.station, row.event_start_time)
				continue

			search_term = _fdf["filepath"].iloc[0]

			print("found source_file:", search_term)

			eqt_df.at[index, "source_file"] = search_term

		eqt_df.dropna(subset = ["source_file"]) # this should fix the faulty merge

		eqt_df = eqt_df.merge(s_df, how = "left", left_on = "source_file", right_on = "filepath", suffixes = ("", "_sac")) 

		for index, row in eqt_df.iterrows():
			for x in [".EHE.", ".EHN.", ".EHZ."]:
				if x in str(row.source_file):
					search_term = row.source_file.replace(x, ".EH*.")
					break
			eqt_df.at[index, "source_file"] = search_term

		eqt_df.rename({"sac_start_dt_sac": "sac_start_time"})
		# eqt_df.drop(['filepath', 'station_sac'], axis = 1)
		
		eqt_df.to_csv(output_csv, index = False)


	if write:

		eqt_df["sac_start_dt"] = pd.to_datetime(eqt_df["sac_start_dt"])
		eqt_df["event_start_time"] = pd.to_datetime(eqt_df["event_start_time"])

		if filter_csv:
			fdf = pd.read_csv(filter_csv)

			# check that the int types are the same?

			fdf["ID"] = fdf["ID"].astype('int64')
			real_df["ID"] = real_df["ID"].astype('int64')

			real_df = real_df[real_df["ID"].isin(fdf["ID"].tolist())]
		

		for index, row in real_df.iterrows():

			_eqt_df = eqt_df[eqt_df["ID"] == row.ID]
			pid = str(int(row.ID)).zfill(6)
			event_folder = os.path.join(output_folder, pid)

			event_date_string = datetime.datetime.strftime(row["timestamp"], "%Y %j %H %M %S %f")[:-3] # drop the last 3 zeros
			event_lat, event_lon, event_depth = row["LAT"],row["LON"],row["DEPTH"]

			if not os.path.exists(event_folder):
				os.makedirs(event_folder)

			for _index, _row in _eqt_df.iterrows():
				sta = _row.station
				event_dt = _row.event_start_time

				year = (datetime.datetime.strftime(event_dt, "%Y"))
				jday = (datetime.datetime.strftime(event_dt, "%j"))
				year_day = year + "."+ jday # need string representation

				# load routine
				#

				sac_source = _row["source_file"]

				timestamp = (datetime.datetime.strftime(event_dt, "%H%M%S"))

				event_id = "{}.{}.{}".format(sta, year_day, timestamp)

				f1 = os.path.join(event_folder, event_id + ".EHE.SAC")
				f2 = os.path.join(event_folder, event_id + ".EHN.SAC")
				f3 = os.path.join(event_folder, event_id + ".EHZ.SAC")

				start_time = (event_dt - _row.sac_start_dt).total_seconds() - 30
				end_time = (event_dt - _row.sac_start_dt).total_seconds() + 120

				_cut_str = "printf \"cut {:.2f} {:.2f}\\nr {}\\nwrite SAC {} {} {}\\nq\\n\" | sac\n".format(start_time, end_time, sac_source, f1, f2, f3)

				if not "nan" in _cut_str:
					cut_str += _cut_str
				else:
					print("found nan, excluding")
					print(_row.station)
					print(_row["source_file"])
					print(_row.ID)
					print("event dt",event_dt)
					print("sac start time", _row.sac_start_dt)
					print("index", _index)
					print(_row.filepath)
					continue

				#
				# HEADER WRITING
				#

				start_of_file = _row.sac_start_dt

				timestamp = datetime.datetime.strftime(_row.event_start_time, '%H%M%S')

				if not _row.p_arrival_time: # NaN
					p_diff = "-12345"
				else:
					p_diff = (_row.p_arrival_time - start_of_file).total_seconds()
				if not _row.s_arrival_time:
					s_diff = "-12345"
				else:
					s_diff = (_row.s_arrival_time - start_of_file).total_seconds()


				header_str += ("printf \"r {}\\nch A {:.2f}\\nch T0 {:.2f}\\nwh\\nq\\n\" | sac\n".format(
					os.path.join(output_folder, pid, "{}*{}.{}*SAC").format(sta, year_day, timestamp),
					p_diff,
					s_diff,
					))#

				if station_file:
					header_str += "printf 'r {}\\nch o gmt {}\\nch iztype IO\\nch allt (-1.0 * &1,o)\\nch evla {:.5f} evlo {:.5f} evdp {:.5f} stla {:.5f} stlo {:.5f}\\nwh\\nq\\n' | sac\n".format(
					os.path.join(output_folder, pid, "{}*{}.{}*SAC").format(sta, year_day, timestamp),
					event_date_string, 
					event_lat, 
					event_lon, 
					event_depth, 
					station_info[sta]["lat"],
					station_info[sta]["lon"])
				else:
					header_str += "printf 'r {}\\nch o gmt {}\\nch iztype IO\\nch allt (-1.0 * &1,o)\\nch evla {:.5f} evlo {:.5f} evdp {:.5f}\\nwh\\nq\\n' | sac\n".format(
					os.path.join(output_folder, pid, "{}*{}.{}*SAC").format(sta, year_day, timestamp),
					event_date_string, 
					event_lat, 
					event_lon, 
					event_depth, )


				header_str += "printf 'r {}\\nwh\\nq\\n' | sac\n".format(os.path.join(output_folder, pid, "{}*{}.{}*SAC").format(sta, year_day, timestamp)) # this is for calculating DIST etc

		with open(header_file, 'w') as f:
			f.write(header_str)
		with open(cut_file, 'w') as f:
			f.write(cut_str)

		# call subprocess
		time.sleep(1)
		os.chmod(header_file, 0o775)
		time.sleep(1)
		os.chmod(cut_file, 0o775)

def df_searcher(df, _station_dict, _ts, ):

	files_to_copy = []
	try:
		_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d %H:%M:%S.%f")
	except:
		try:
			_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d %H:%M:%S")
		except:
			_ts = datetime.datetime.strptime(_ts, "%Y-%m-%d-%H-%M-%S.%f")

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

		# these should give an exact match, and only 1

		if _p_arrival_time:
			_p_df = _df[(_df['p_arrival_time'] < _p_arrival_time + datetime.timedelta(seconds=1)) & (_df['p_arrival_time'] > _p_arrival_time - datetime.timedelta(seconds=1))].copy()
			# print(_p_df)

			try:
				assert _p_df.shape[0] == 1

			except:
				pass
				# print("Duplicates found for above p_df")

			for index, row in _p_df.iterrows():

				# print(index)
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
			_s_df = _df[(_df['s_arrival_time'] < _s_arrival_time + datetime.timedelta(seconds=1)) & (_df['s_arrival_time'] > _s_arrival_time - datetime.timedelta(seconds=1))].copy()

			try:
				assert _s_df.shape[0] == 1

			except:
				pass
				# print("Duplicates found for above p_df")

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

	return target_indices, _station_dict

	#return {"files_to_copy": files_to_copy, "_station_dict": _station_dict}


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("real_csv", help = "Collated from collect_latlon. Only has event information. Used to iterate over IDs.")
	ap.add_argument("output_folder", help = "Folder to create new event archive inside.")
	ap.add_argument("-eqt_csv", help = "EQT outputs (filtered the way you want it)")
	ap.add_argument("-rj", "--real_json", help = "Collated from collect_latlon, has phase and event information.")
	ap.add_argument("-oc", "--output_csv", help = "Patched EQT output csv with source file paths and event ID")
	ap.add_argument("-oj", "--output_json", help = "Patched json with timestamps for arrival times")
	ap.add_argument("-sc", "--sac_csv", help = "Generated by -msc flag from multi_station, with start and end times for each original SAC file.")
	ap.add_argument("-sf", "--station_file", help = "Include this argument to write STLO and STLA headers")
	ap.add_argument("-ee", "--eqt_to_event", action = 'store_true')
	ap.add_argument("-es", "--eqt_to_sac", action = 'store_true')
	ap.add_argument("-w", "--write", action = 'store_true')
	ap.add_argument('-f', "--filter_csv", help = "column of IDs to write events for")

	args = ap.parse_args()


	choose_event_wf(args.real_csv, args.real_json, args.eqt_csv, args.output_csv, args.output_json,  args.sac_csv,args.output_folder, args.station_file,
	eqt_to_event = args.eqt_to_event, 
	eqt_to_sac = args.eqt_to_sac, 
	write = args.write, 
	filter_csv = args.filter_csv,	
	)
