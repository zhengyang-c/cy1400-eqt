import matplotlib
#matplotlib.use('TkAgg')
from EQTransformer.core.predictor import predictor
from EQTransformer.utils.hdf5_maker import preprocessor
import obspy
from obspy import read
import numpy as np
import os
import math
#import matplotlib
#import matplotlib.pyplot as plt
from datetime import datetime
from helpme import *
import sys
import re
import json
import datetime
import pandas as pd
import glob
import copy

coordinates_doc = "station_info.dat"
station_json_output = 'station_list.json'

start_day, end_day = 85, 109
stations_to_use = ["TA19"]
query_station_day = []

for i in stations_to_use:
	for day in range(start_day, end_day):
		query_station_day.append("{}_2020_{}".format(i, str(day).zfill(3))) # the year lol


#query_station_day = ["TA01_2020_{}".format(str(i).zfill(3)) for i in range(start_day, end_day)]
#query_station_day.extend(["TA02_2020_{}".format(str(i).zfill(3)) for i in range(start_day, end_day)])

#query_station_day = ["TA01_2020_085", "TA01_2020_086"] # some day autogenerate this lol
#print(query_station_day)
for run_i in range(25):
	run_string = "TA19_no_preproc"

	mseed_parent_folder_name = "mseed_" +  run_string
	#data_parent_folder_name = "EOS_SAC"
	data_parent_folder_name = "no_preproc"
	mseed_hdfs = mseed_parent_folder_name + "_processed_hdfs"
	eqt_model_path = 'EQTransformer/ModelsAndSampleData/EqT_model.h5'
	detection_folder_name = "detections_" + run_string + "_{}".format(run_i)

	if not os.path.exists(mseed_parent_folder_name):
		os.makedirs(mseed_parent_folder_name)

	# generate stations.json for a single station

	station_list = {}
	for thing in query_station_day:
		[_station, _year, _day] = thing.split("_")
		station_list[_station] = {"network": "AC", "channels":["EHZ", "EHE", "EHN"]}

	# generate station_list.json for multiple stations / handle a batch of files 

	with open(coordinates_doc, "r") as f:
		coordinates = f.read().split("\n")
		
		coordinates = [y.strip() for x in coordinates if len(x) > 0 for y in x.strip().split("\t") if len(y) > 0 ]

		# get all the stations and write the relevant details
		# all use 3 channels
		# elevations just put like 100? lmao

	for station in station_list:
		#print(station)
		i = coordinates.index(station)

		station_list[station]["coords"] = [100, float(coordinates[i + 1]), float(coordinates[i+2])]

	with open(station_json_output, 'w') as f:
		json.dump(station_list, f)

	# convert sac files to mseed for use in EQT



	# EOS_MSEED
	#	TA01
	# 		sac file

	folders = [x[0] for x in os.walk(data_parent_folder_name)]

	# if the last few letters follow a specific regex pattern, then use that folder

	folders = list(filter(lambda x: re.match(r"\D{2,3}\d{2,3}", x.split("/")[-1]), folders))

	# presumably everything will be first converted from MSEED to SAC format (preprocessed)
	# then back to MSEED for use in EqT
	# and then plotting using the SAC file 

	# for each folder, build a tuple of (EHE, EHZ, EHN) for every single day

	all_files = []

	for folder in folders:
		files = {}

		for _file in os.listdir(folder):
			net = _file.split(".")[0]
			sta = _file.split(".")[1]
			_ = _file.split(".")[2] #idk dude
			cha = _file.split(".")[3]
			_ = _file.split(".")[4]
			year_day = _file.split(".")[5] + "_" + _file.split(".")[6]
			
			if year_day not in files:
				files[year_day] = [_file]
			elif year_day in files:
				files[year_day].append(_file)

		all_files.append((sta, files))
			

	#print(all_files)
	# convert them to MSEED format using OBSPY
	#for _station, _all_days in all_files:



	for _station, _all_days in all_files:

		valid_days = []
		for day in _all_days:
			if not "{}_{}".format(_station, day) in query_station_day:
				continue
			valid_days.append(day)


		valid_days.sort(key = lambda x: (x.split("_")[0], x.split("_")[1]))

		# for every listed file in the year list, merge all matching files in the SAC folder 

		print(valid_days)

		for _channel in ["EHE", "EHN", "EHZ"]:
			output_file_name = "{}__{}__{}__{}__{}.mseed".format("AC", valid_days[0].split("_")[0], valid_days[0].split("_")[1], _station, _channel)
			if not os.path.exists(os.path.join(mseed_parent_folder_name, _station, output_file_name)):
				for c, valid_day in enumerate(valid_days):
					_file_name = "AC.{}.00.{}.D.{}.{}.*".format(_station, _channel, valid_day.split("_")[0], valid_day.split("_")[1] )
					if c == 0:
						_st = read(os.path.join(data_parent_folder_name, _station, _file_name))
					else:
						_st += read(os.path.join(data_parent_folder_name, _station, _file_name))
						#print("yes but ", _file_name)

				_st.merge(method = 1) 
				# documented at https://docs.obspy.org/packages/autogen/obspy.core.trace.Trace.__add__.html#handling-overlaps
				# this will prioritise the newer trace in the case of an overlap

				# just take the year and month of the first day because i'm not bothered enough right now

				if not os.path.exists(os.path.join(mseed_parent_folder_name, _station)):
					os.makedirs(os.path.join(mseed_parent_folder_name, _station))
				

				_st.write(os.path.join(mseed_parent_folder_name, _station, output_file_name))

				_st.clear()


	"""for _station, _all_days in all_files:
		for year_day in _all_days:
			for _file in _all_days[year_day]:

				# read in all SAC files of the same channel, put them in the same stream, then 
				# then merge them lol
				# https://docs.obspy.org/packages/autogen/obspy.core.stream.Stream.merge.html#obspy.core.stream.Stream.merge
				# https://docs.obspy.org/packages/autogen/obspy.core.trace.Trace.__add__.html#handling-overlaps

				# month
				_month = datetime.datetime.strptime(_file.split(".")[6], "%j").strftime("%m")

				_mseed_file_name = "AC__{}__{}__{}__{}.mseed".format(_file.split(".")[5], _month, _station, _file.split(".")[3]) # 3: channel
				# AC__2020__03__TA01__EHZ__085 i think??
				# if mseed file is written already, don't bother 
				# TODO: add a flag to force writing (?) no point tbh
				if os.path.isfile(os.path.join(mseed_parent_folder_name, _station, _mseed_file_name)):
					continue

				# check if output file exists
				_st = read(os.path.join(data_parent_folder_name, _station, _file))
				
				# make output folder if it's not there 
				if not os.path.exists(os.path.join(mseed_parent_folder_name, _station)):
					os.makedirs(os.path.join(mseed_parent_folder_name, _station))

				#_st.write(os.path.join(mseed_parent_folder_name, _station, _mseed_file_name), format = 'MSEED')
	"""

	#if not os.path.exists(mseed_hdfs):
	#preprocessor(mseed_dir=mseed_parent_folder_name, stations_json= station_json_output, overlap=0.3, n_processor=4)

	# this is quite sketchy hmm
	#if not os.path.exists(detection_folder_name):
	predictor(input_dir = mseed_hdfs, input_model = eqt_model_path, output_dir=detection_folder_name, detection_threshold=0.3, P_threshold=0.1, S_threshold=0.1, number_of_plots=100, plot_mode='time')

	# read CSV to cut SAC files into smaller folders and stuff

	# i'm unsure what will happen with batch processing

	for csv_file in glob.glob("{}/*/*.csv".format(detection_folder_name)):
		df = pd.read_csv(csv_file)

		sta = csv_file.split("/")[1].split("_")[0]

		csv_dir = "/".join(csv_file.split("/")[:-1])

		save_dir = "sac_picks"

		if not os.path.exists(os.path.join(csv_dir, save_dir)):
			os.makedirs(os.path.join(csv_dir, save_dir))
			
		pick_date_times = []

		for p_arrival in df['event_start_time']:
			pick_date_times.append(datetime.datetime.strptime(p_arrival.split(".")[0], "%Y-%m-%d %H:%M:%S"))

		#for p_arrival in pick_date_times:

		for _sta, _sta_details in all_files:
			if _sta == sta:
				sta_details = copy.deepcopy(_sta_details)
				break

		assert sta_details

		for c, p_arrival in enumerate(pick_date_times):
			# get year and julian day
			prev_year_day = ""
			_year = p_arrival.strftime("%Y")
			_day = p_arrival.strftime("%j")
			pick_year_day =  _year + "_" + _day

			print(sta_details[pick_year_day])

			if c == 0:
				st = read(os.path.join(data_parent_folder_name, sta,"*{}.{}.*".format(_year, _day))) 

			elif not prev_year_day == pick_year_day: # different year_day, so reload new
				st.clear()
				st = read(os.path.join(data_parent_folder_name, sta,"*{}.{}.*".format(_year, _day))) 

			# else, it's already loaded, can start trimming
			_st = st.copy()

			start_UTC_time = _st[0].stats.starttime
			delta_t = obspy.UTCDateTime(p_arrival) - start_UTC_time
			_st.trim(start_UTC_time + delta_t - 30, start_UTC_time + delta_t + 120)


			# write SAC file 
			for tr in _st:
				if not os.path.exists(os.path.join(csv_dir, save_dir, "{}.{}.{}.{}.{}.SAC".format(sta, _year, _day, p_arrival.strftime("%H%M%S"), tr.stats.channel))):
					tr.stats.stla, tr.stats.stlo = station_list[sta]["coords"][1], station_list[sta]["coords"][2], 
					#print(tr.stats.stla)
					#print(tr.stats.stlo)
					tr.write(os.path.join(csv_dir, save_dir, "{}.{}.{}.{}.{}.SAC".format(sta, _year, _day, tr.stats.channel, p_arrival.strftime("%H%M%S"))), format = "SAC")


			# plot 

			# trim a bit more then plot ?
			_st.trim(start_UTC_time + delta_t - 5, start_UTC_time + delta_t + 10)
			png_file = "{}.{}.{}.{}.png".format(sta, _year, _day, p_arrival.strftime("%H%M%S"))
			if not os.path.exists(os.path.join(csv_dir, save_dir, png_file)):
				_st.plot(outfile = os.path.join(csv_dir, save_dir, png_file), size = (800, 600))


			prev_year_day = pick_year_day

	# find the corresponding SAC file

	# load all three components

	# for each component, trim to:
	# 30 s before P and wave and 2 minutes after P wave

	# write the SAC file into a new folder

	# and presumably also plot in mpl or something 

