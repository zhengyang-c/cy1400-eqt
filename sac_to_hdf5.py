#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 21:21:31 2019

@author: mostafamousavi

last update: 06-21-2020 

- downsampling using the interpolation function can cause false segmentaiton error. 
	This depend on your data and its sampling rate. If you kept getting this error when 
	using multiprocessors, try using only a single cpu. 
	
"""
import argparse
import h5py
from pathlib import Path
from obspy import read
import obspy
from obspy import UTCDateTime
import datetime
import os
import math
import h5py
import numpy as np

import shutil
import json
import pandas as pd
from multiprocessing.pool import ThreadPool
import multiprocessing

import faulthandler; faulthandler.enable()


"""
adapted from Mousavi hdf5_maker.py
multiprocessing is added for multiple station processing

"""

# should remove n_days 


def preproc(csv_paths, station, output_folder, stations_json, overlap = 0.3, n_processor = None, partial_day_file = "" ):


	# sac_folder should contain folders named with station data. inside will be .SAC files and presumably no other junk 

	#if not n_processor:
		#n_processor = multiprocessing.cpu_count() # taken from mousavi stead

	# a hdf5 and csv file pair with the station name is created for each station

	with open(stations_json, "r") as f:
		stations_ = json.load(f)

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	
	#save_dir = os.path.join(os.getcwd(), str(mseed_dir)+'_processed_hdfs')


	sac_df = pd.read_csv(csv_paths)

	sac_df.dt = pd.to_datetime(sac_df.dt)

	sac_df = sac_df[sac_df.station == station]

	indiv_days = [v for k, v in sac_df.groupby('dt')] # further split into days, not sure if necessary

	if (len(indiv_days)) == 0:
		print("===========================================\n")
		print("sac to hdf5: no SAC files found for station: {}".format(station))
		print("\n===========================================")

		return 0
	# split into a list of smaller dataframes, which can be passed into the threadpool


	sac_df.reset_index(inplace = True)

	station_info = sac_df
	sta = station

	#print(station_info)


	# _output_folder = os.path.join(output_folder, sta)
	# if not os.path.exists(_output_folder):
	# 	os.makedirs(_output_folder)

	csv_output_path = os.path.join(output_folder, "{}.csv".format(sta))
	hdf5_output_path = os.path.join(output_folder, "{}.hdf5".format(sta))


	# create hdf5 file and csv object with all the required headers

	# csv output: trace_name, start_time


	_outhf = h5py.File(hdf5_output_path, "w")

	_outgrp = _outhf.create_group("data")


	# if partial_day_file is given, load from partial_day_file (the list of datetimes for that station to exclude)
	# which has station name as the header bc i am big lazy
	# then if this is so,
	# then when generating timestamps, use a different routine:

	csv_output = {"trace_name": [], "start_time": [], "source_file": [], "sac_start_time": []}

	# get time stamps first using the overlap since the time stamps are just a delta

	if partial_day_file != "":
		p_df = pd.read_csv(partial_day_file)
		exclude_list = [int(x) for x in p_df[station].tolist() if x == x] # NaN is != NaN 

	for dday_df in indiv_days:


		dday_df.reset_index(inplace = True)

		# get unique value of the filenames

		for _, day_df in dday_df.groupby(by = "_uid"):


			year_day = datetime.datetime.strftime(day_df["dt"].tolist()[0], "%Y.%j")
			
			"""
			just change it s.t. it will consider more than one entry inside the day_df (?) that's probably the easiest solution

			since i now know that the input mseed file is cut into sac files, there won't be any major overlaps to worry about
			"""

			filepath_root = Path(day_df.at[0,'filepath']).parent

			file_name_str = os.path.join(filepath_root, "*{}.{:06d}.SAC".format(year_day, day_df.at[0, "start_time"]))

			st = read(file_name_str)

			st.resample(100.0)
			st.filter('bandpass', freqmin = 1.0, freqmax = 45, corners = 2, zerophase = True)
			st.detrend('demean')


			# if using partial day file. could just submit a blank file in the future but still need a file anyway hmmm
			if partial_day_file != "":
				start_time = st[0].stats.starttime # UTCDateTime object
				end_time = st[0].stats.endtime

				# get jday of 
				# tbh this should be extended to year-jday but that can... wait??
				# 
				
				n_cuts = ((end_time - start_time) - (overlap * 60))/((1 - overlap)*60)

				n_cuts = math.floor(n_cuts)

				timestamps = []
				dt = [] 

				for i in range(n_cuts):

					_start_time = (start_time + i * (1 - overlap) * 60).datetime

					_dt = (1 - overlap) * 60 * i

					if int(datetime.datetime.strftime(_start_time, "%j")) in exclude_list:
						continue

					timestamps.append(_start_time)
					dt.append(_dt)

				
				# get the B E and KZTIME from the SAC header.
				# generate timestamps as per usual, but for every time stamp check against the partial day file list
				# if the dt is inside, skip (this can't be that expensive computationally)
				
			# default full day 
			else:
				start_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.min)

				end_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.max)


				n_cuts = ((end_of_day - start_of_day).total_seconds() - (overlap * 60))/((1 - overlap)*60)

				n_cuts = math.floor(n_cuts)

				timestamps = [start_of_day + datetime.timedelta(seconds = (1 - overlap) * 60) * j for j in range(n_cuts)]

				timestamps.append(start_of_day + datetime.timedelta(seconds = 86340))
				dt = [(1 - overlap) * 60 * j for j in range(n_cuts)]
				dt.append(86340) 			


			for c, timestamp in enumerate(timestamps):
				#print(timestamp)

				datum = np.zeros((6000, 3))

				start_index = int(dt[c] * 100)
				try:
					for j in range(3):
						datum[:,j] = st[j].data[start_index : start_index + 6000]
				except:
					continue
				_tracename = "{}_AC_EH_{}".format(sta, str(UTCDateTime(timestamp)))
				_start_time = datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

				#print(_tracename, _start_time)

				_g = _outgrp.create_dataset(_tracename, (6000, 3), data = datum)
				
				_g.attrs['trace_name'] = _tracename
				_g.attrs['receiver_code'] = sta
				_g.attrs['receiver_type'] = "EH"
				_g.attrs['network_code'] = "AC"
				_g.attrs["receiver_longitude"] = stations_[sta]['coords'][1]
				_g.attrs["receiver_latitude"] = stations_[sta]['coords'][2]				
				_g.attrs["receiver_elevation_m"] = stations_[sta]['coords'][0]
				_g.attrs["trace_start_time"] = _start_time

				csv_output["trace_name"].append(_tracename)
				csv_output["start_time"].append(_start_time)
				csv_output["source_file"].append(file_name_str)
				csv_output["sac_start_time"].append(str(st[0].stats.starttime))

	_outhf.close()
	d_csv = pd.DataFrame.from_dict(csv_output)
	d_csv.to_csv(csv_output_path, index = False)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()


	parser.add_argument('csv_path', help = "csv file with the required station metadata")
	parser.add_argument('station', help = "")
	parser.add_argument('output_folder', help = "folder to write the HDF5 and csv file in. station name is the filename.")
	parser.add_argument('station_json', help = "path to station_list.json that is already used by EQT, which gives station coordinates")
	parser.add_argument('-partial_day_file', help = "path to uptime (used for fixing", default = "")
	parser.add_argument('-t', '--time', type = str, help = "log timing to this filepath")
	parser.add_argument('-p', '--process', type = int, help = "number of processors (one per station)")



	args = parser.parse_args()

	start_time = datetime.datetime.now()


	preproc(args.csv_path, args.station, args.output_folder, args.station_json, n_processor = args.process, partial_day_file = args.partial_day_file)


	end_time = datetime.datetime.now()

	time_taken = (end_time - start_time).total_seconds()

	if args.time:
		with open(args.time, "a+") as f:
			f.write("sac_to_hdf5,{},{}\n".format(datetime.datetime.strftime(start_time, "%Y%m%d %H%M%S"),time_taken))

