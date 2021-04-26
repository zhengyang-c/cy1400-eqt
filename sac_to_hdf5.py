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

def preproc(sac_folder, output_folder, stations_json, n_days = None, overlap = 0.3, n_processor = None):

	# sac_folder should contain folders named with station data. inside will be .SAC files and presumably no other junk 

	if not n_processor:
		n_processor = multiprocessing.cpu_count()

	# a hdf5 and csv file pair with the station name is created for each station

	with open(stations_json, "r") as f:
		stations_ = json.load(f)
	
	#save_dir = os.path.join(os.getcwd(), str(mseed_dir)+'_processed_hdfs')

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	#repfile = open(os.path.join(preproc_dir,"X_preprocessor_report.txt"), 'w')

	station_list = [{"path":os.path.join(sac_folder, _sta), "sta": _sta} for _sta in os.listdir(sac_folder)]

	def process(station_info):
		print(station_info)

		sta = station_info["sta"]

		_output_folder = os.path.join(output_folder, sta)
		if not os.path.exists(_output_folder):
			os.makedirs(_output_folder)

		csv_output_path = os.path.join(output_folder, sta, "{}.csv".format(sta))
		hdf5_output_path = os.path.join(output_folder, sta, "{}.hdf5".format(sta))


		# create hdf5 file and csv object with all the required headers

		# csv output: trace_name, start_time

		_outhf = h5py.File(hdf5_output_path, "w")

		_outgrp = _outhf.create_group("data")

		sac_files = [str(path) for path in Path(station_info["path"]).glob('*.SAC')]
		sac_files.sort()

		# group sac_files into days in increasing order
		# create a dictionary, entry: year_day { EHE, EHZ, EHN file paths}
		# 
		
		files = {}
		
		for _file in sac_files:
			print(_file)
			net = _file.split(".")[0]
			sta = _file.split(".")[1]
			_ = _file.split(".")[2] #idk dude
			cha = _file.split(".")[3]
			_ = _file.split(".")[4]
			year_day = _file.split(".")[5] + "." + _file.split(".")[6]
			
			if year_day not in files:
				files[year_day] = [_file]
			elif year_day in files:
				files[year_day].append(_file)

		print(files)

		csv_output = {"trace_name": [], "start_time": []}

		# get time stamps first using the overlap since the time stamps are just a delta

		for c, year_day in enumerate(files):

			if not n_days == None:
				if c > n_days:
					break

			start_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.min)

			end_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.max)

			print(start_of_day, end_of_day)

			n_cuts = ((end_of_day - start_of_day).total_seconds() - (overlap * 60))/((1 - overlap)*60)

			n_cuts = math.floor(n_cuts)

			timestamps = [start_of_day + datetime.timedelta(seconds = (1 - overlap) * 60) * j for j in range(n_cuts)]
			timestamps.append(start_of_day + datetime.timedelta(seconds = 1430))
			dt = [(1 - overlap) * 60 * j for j in range(n_cuts)]
			dt.append(1430)

			#print(timestamps[:5])

			st = read(os.path.join(station_info["path"], "*{}*SAC".format(year_day)))
			print(st)
			st.resample(100.0)
			st.detrend('demean')

			for c, timestamp in enumerate(timestamps):
				print(timestamp)

				datum = np.zeros((6000, 3))

				start_index = int(dt[c] * 100)
				try:
					for j in range(3):
						datum[:,j] = st[j].data[start_index : start_index + 6000]
				except:
					continue
				_tracename = "{}_AC_EH_{}".format(sta, str(UTCDateTime(timestamp)))
				_start_time = datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

				print(_tracename, _start_time)

				_g = _outgrp.create_dataset(_tracename, (6000, 3), data = datum)
				
				_g.attrs['trace_name'] = _tracename
				_g.attrs['receiver_code'] = sta
				_g.attrs['receiver_type'] = "EH"
				_g.attrs['network_code'] = "AC"
				_g.attrs["receiver_longitude"] = stations_[sta]['coords'][0]
				_g.attrs["receiver_latitude"] = stations_[sta]['coords'][1]				
				_g.attrs["receiver_elevation_m"] = stations_[sta]['coords'][2]
				_g.attrs["trace_start_time"] = _start_time

				csv_output["trace_name"].append(_tracename)
				csv_output["start_time"].append(_start_time)

		_outhf.close()
		d_csv = pd.DataFrame.from_dict(csv_output)
		d_csv.to_csv(csv_output_path, index = False)



	with ThreadPool(n_processor) as p:
		p.map(process, station_list) 

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument('sac_folder')
	parser.add_argument('output_folder')
	parser.add_argument('station_json')
	parser.add_argument('-n', '--n_days', type = int)


	args = parser.parse_args()

	preproc(args.sac_folder, args.output_folder, args.station_json, args.n_days)


