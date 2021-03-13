'''
has a proper datetime merger uknow

1) identify timestamps to use that are signals

use 65 - 5 seconds before the signal

take timestamps from csv file picks

2) and output to hdf5 file, write to csv file too	

after this,

3) start adding detections that were actually noise

this will keep the number of noise waveforms manageable

can feed the noise through the detection because that would be interesting to know the false positive rate


after that, start randomly sampling from the 
'''

import h5py as h5
import glob
import os
import argparse
import numpy as np
#import matplotlib
#matplotlib.use("TkAgg")
#import matplotlib.pyplot as plt
import random
import datetime
import obspy
from obspy import read
import pandas as pd
from obspy import UTCDateTime

from pathlib import Path
# recommended by https://stackoverflow.com/questions/2186525/how-to-use-glob-to-find-files-recursively
# glob is slower 
def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

def datetime_to_str(x, dx):
	return datetime.datetime.strftime(x  + datetime.timedelta(seconds = dx), "%Y-%m-%d %H:%M:%S")


# https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def collate_timestamps():
	csv_parent_folder = "/home/zchoong001/cy1400/cy1400-eqt/training_files/generate_noise_13mar"

	csv_files = [str(path) for path in Path(csv_parent_folder).rglob('*.csv')]


	# read 

	global_list = []

	for csv_file in csv_files:
		df = pd.read_csv(csv_file)
		_detections = df['event_start_time']

		global_list.extend(_detections)

	#print(global_list[:5])
	print(len(global_list))

	global_list = [str_to_datetime(x) for x in global_list]

	

	filtered_datestrings = [] # rounded to seconds

	for entry in global_list:
		time_deltas = [-2, -1, 0, 1, 2]

		# round the timestamp to the nearest second, then take +/- 2 seconds
		# if none of those are in filtered datestrings, then add to filtered datestrings
		# this is meant to filter out duplicate detections since sometimes the detection can be quite off / bad

		if (all(not(x in filtered_datestrings) for x in ([datetime_to_str(entry, dx) for dx in time_deltas]))):
			filtered_datestrings.append(datetime_to_str(entry, 0))

	print(len(filtered_datestrings))

	filtered_datestrings.sort()


	noise_periods = [] # a list of tuples, start and end datetime objects, 

	blacklist = []

	for i, event_time in enumerate(filtered_datestrings):
		_event_time = str_to_datetime(event_time)

		start_time = _event_time - datetime.timedelta(seconds = 65)
		end_time = _event_time - datetime.timedelta(seconds = 5)
		event_start = _event_time - datetime.timedelta(seconds = 5)
		event_end_time = _event_time + datetime.timedelta(seconds = 60)

		# using this in case there are like a lot of tremors or w/e 
		# even though i could use the event_end time from EQT

		if not (is_time_between(start_time, end_time, str_to_datetime(filtered_datestrings[i - 1]))):
			noise_periods.append((start_time, end_time))

		if i == len(filtered_datestrings) - 1:
			blacklist.append((event_start, event_end_time))
		else:
			next_event_start = str_to_datetime(filtered_datestrings[i + 1]) - datetime.timedelta(seconds = 5)
			next_event_end = str_to_datetime(filtered_datestrings[i + 1]) + datetime.timedelta(seconds = 60)		

			if not is_time_between(next_event_start, next_event_end, event_end_time):
				blacklist.append((event_start, event_end_time))

			#print(is_time_between(next_event_start, next_event_end,event_end_time))
	#print(blacklist[:5])
	#print(blacklist[-5:])

	unravelled_blacklist = []

	start_of_first_day = datetime.datetime.combine(blacklist[0][0].date(), datetime.time.min)
	end_of_last_day = datetime.datetime.combine(blacklist[-1][1].date(), datetime.time.max)
	unravelled_blacklist.append(start_of_first_day)

	for _i, _j in blacklist:
		unravelled_blacklist.append(_i)
		unravelled_blacklist.append(_j)

	unravelled_blacklist.append(end_of_last_day)
	#cut_sac_file(["TA19"], [noise_periods])
	cut_sac_file(["TA19"], [unravelled_blacklist], fill_gaps = True)

	# actually just get all noise waveforms in between events, block out 5 seconds before event starts and 60 s after event ends

''' timestamps: a list of tuples, for noise start and end periods''' 
def cut_sac_file(stations, timestamps, fill_gaps = False, overlap = 0.3):

	sac_parent_folder = "/home/zchoong001/cy1400/cy1400-eqt/no_preproc/TA19/"

	sac_files = [str(path) for path in Path(sac_parent_folder).rglob('*.SAC')]

	print(sac_files)

	output_root = "training_files/aceh_noise_13mar_wholeday"
	output_h5 = output_root + ".hdf5"
	output_csv = output_root + ".csv"

	csv_output_data = {
		"trace_category":[],
		"trace_name":[],
	}

	#_outhf = h5.File(output_h5, "w")

	#_outgrp = _outhf.create_group("data")

	binned_timestamps = {}

	for s_n, station_set in enumerate(timestamps):

		# binned based on year.day
		for x in station_set:
			_year_day = datetime.datetime.strftime(x[0], "%Y.%j")
			if not _year_day in binned_timestamps:
				binned_timestamps[_year_day] = [x]
			else:
				binned_timestamps[_year_day].append(x)

		''' for every year_day combination, load the corresponding sac file, it should (in the future) fail gracefully when it cannot find the sac file

		but that's low priority atm 

		this is also SPECIFIC to the station; to extend, i would have to create a new noise data set for every station (?) and then later merge the hdf5 files together'''

		# go through every list in binned_timestamps if fill_gaps = True

		# and convert these to 1 minute timestamps with 0.3 second overlaps based on every large interval given

		not_binned_timestamps = binned_timestamps.deepcopy()

		for _bin in not_binned_timestamps:
			print(_bin[1] - _bin[0])

		'''for year_day in binned_timestamps:
			print(year_day)
			print(stations[s_n])

			st = read(sac_parent_folder + "*{}*.SAC".format(year_day))
			st.resample(100.0)			

			for timestamp in binned_timestamps[year_day]:
				_tracename = "{}.{}.{}_NO".format(stations[s_n], year_day, datetime.datetime.strftime(timestamp[0], "%H%M%S"))

				print(_tracename)
				stt = st.copy()
				print(stt[0].stats.starttime)
				stt.trim(UTCDateTime(timestamp[0]), UTCDateTime(timestamp[1]) ,nearest_sample = False)

				csv_output_data["trace_category"] = "noise"
				csv_output_data["trace_name"] = _tracename

				datum = np.zeros((6000, 3))

				for j in range(3):
					datum[:,j] = stt[j].data[:6000]

				_g = _outgrp.create_dataset(_tracename, (6000, 3), data = datum)
				_g.attrs['trace_category'] = "noise"

			st.clear()
	_outhf.close()

	d_csv = pd.DataFrame.from_dict(csv_output_data)
	d_csv.to_csv(output_csv, index = False)
'''
	# bin the timestamps into days

	# then for every day, load the corresponding sac file


	# i guess i s

	# try passing in noise periods first to get ~ a few hundred waveforms
	# then write them to a hdf5 file along with the csv info

	# noise info needed:

	# trace_category
	# trace_name

collate_timestamps()