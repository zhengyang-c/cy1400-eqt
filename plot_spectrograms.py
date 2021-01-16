import obspy
from obspy import read
import numpy as np
import os
import math
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from datetime import datetime
from helpme import *
import sys
import re
import json
import datetime
import pandas as pd
import glob
import copy
from scipy import signal

coordinates_doc = "station_info.dat"
station_json_output = 'station_list.json'
query_station_day = ["TA01_2020_085"] # some day autogenerate this lol
mseed_parent_folder_name = "EOS_MSEED"
data_parent_folder_name = "EOS_SAC" # what folder structure am i uh using 
detection_folder_name = "detections 20210113 1413"

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
		

for csv_file in glob.glob("{}/*/*.csv".format(detection_folder_name)):
	df = pd.read_csv(csv_file)

	sta = csv_file.split("/")[1].split("_")[0]

	csv_dir = "/".join(csv_file.split("/")[:-1])

	save_dir = "spec_plots"

	if not os.path.exists(os.path.join(csv_dir, save_dir)):
		os.makedirs(os.path.join(csv_dir, save_dir))
		
	pick_date_times = []

	for p_arrival in df['p_arrival_time']:
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
			st = read(os.path.join(data_parent_folder_name, sta,"*{}.{}.*".format(_year, _day))) # reads all 3 channels

		elif not prev_year_day == pick_year_day: # different year_day, so reload new
			st.clear()
			st = read(os.path.join(data_parent_folder_name, sta,"*{}.{}.*".format(_year, _day))) 

		# else, it's already loaded, can start trimming
		_st = st.copy()

		start_UTC_time = _st[0].stats.starttime
		delta_t = obspy.UTCDateTime(p_arrival) - start_UTC_time
		_st.trim(start_UTC_time + delta_t - 30, start_UTC_time + delta_t + 120)

		fig, axs = plt.subplots(2,3, figsize=(9,4))
		fig.suptitle("{} {} {} {}".format(sta, _year, _day, p_arrival.strftime("%H%M%S")))

		_time = (np.arange(0, len(_st[0].data)) * 0.008) - delta_t # 125 HZ sampling dum dum

		for n in range(3): # plot
			axs[0, n].plot(_time, _st[n].data, color = 'black', linewidth = 0.1)
			_f, _t, _Sxx = signal.spectrogram(_st[n].data, fs = _st[0].stats.sampling_rate)
			#print()
			axs[0, n].set_title(_st[n].stats.channel)

			axs[1, n].pcolormesh(_t, _f, _Sxx, shading = 'gouraud', cmap = 'viridis')
			axs[1, n].set_xlabel("Time relative to P-wave arrival")
			axs[1, n].set_ylim(1, 45)

		# plot 

		# trim a bit more then plot ?
		_st.trim(start_UTC_time + delta_t - 5, start_UTC_time + delta_t + 10)
		png_file = "{}.{}.{}.{}.png".format(sta, _year, _day, p_arrival.strftime("%H%M%S"))
		#if not os.path.exists(os.path.join(csv_dir, save_dir, png_file)):
		plt.savefig(os.path.join(csv_dir, save_dir, png_file), dpi = 300)
			#_st.plot(outfile = os.path.join(csv_dir, save_dir, png_file), size = (800, 600))


		prev_year_day = pick_year_day

# find the corresponding SAC file

# load all three components

# for each component, trim to:
# 30 s before P and wave and 2 minutes after P wave

# write the SAC file into a new folder

# and presumably also plot in mpl or something 

