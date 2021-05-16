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


NAME YOUR FILES {STA}.hdf5 and so on 

future multi station noise: 
predict separately; the .csv and hdf5 can be merged for training purposes anyway


'''

import h5py as h5
import glob
import os
import argparse
import numpy as np
#import matplotlib
#matplotlib.use("TkAgg")
#import matplotlib.pyplot as plt
import math
import random
import datetime
import obspy
from obspy import read
import pandas as pd
from obspy import UTCDateTime

from pathlib import Path

from merge_csv import merging_df

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = "Generate noise from single station 3C waveforms using a blacklist method by blacklisting known good picks.")

	parser.add_argument('sta', type = str, help = "station name")
	parser.add_argument('csv_folder', type = str, help = "folder containing csvs to merge (assuming they aren't, but they should)")
	parser.add_argument('sac_parent_folder', type = str, help = "")
	parser.add_argument('output_root', type = str, help = "")

	#parser.add_argument('manual_picks', type = str, help = "Path to txt file of manual picks (this should not require any processing)")

	#parser.add_argument('csv_output', type = str, help = "Path to new csv file with all noise removed")
	args = parser.parse_args()

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


def collate_timestamps(sta, csv_parent_folder, sac_parent_folder, output_root):
	#csv_parent_folder = "/home/zchoong001/cy1400/cy1400-eqt/training_files/generate_noise_27mar"

	csv_files = [str(path) for path in Path(csv_parent_folder).glob('*.csv')]

	# so from multiple .csv files (because i didn't write merging yet, collate all the picks
	# to make a blacklist

	# so i want to feed it all the events i tagged as A/B

	# which means i want to filter/add a column to the csv file

	global_list = []

	_path = Path(output_root)

	_outputparent = _path.parent.absolute()

	if not os.path.exists(_outputparent):
		os.makedirs(_outputparent)

	df = pd.concat((pd.read_csv(f) for f in csv_files), ignore_index = True)

	#print(df)

	#

	df.event_datetime = pd.to_datetime(df.event_datetime) # this assumes that they've already been processed before
	# which is reasonable since when generating a noise data set you'll have a multirun --> requires merging --> event_Datetime column should be present

	df.sort_values(by=['event_datetime'], inplace = True)
	df = df.reset_index(drop=True)

	
	df = df.assign(use_or_not=0)
	df = df.assign(dt=0)
	df = df.assign(agreement=0)
	df = merging_df(df) # it's more of a formality? to remove duplicate events 

	# take the timestamps, have list of (start end points) that are - 10 seconds before and 60 seconds after each timestamp
	# these are the event blacklists
	# 
	# what you want to do next is the merge the blacklists
	

	blacklists = []

	for timestamp in list(df.event_datetime):
		_start = timestamp - datetime.timedelta(seconds = 10) # 10 because sometimes there are bad picks so
		_end = timestamp + datetime.timedelta(seconds = 60)

		if len(blacklists) > 0:
			if _start < blacklists[-1]:
				blacklists[-1] = _end # merge

			else:
				blacklists.append(_start)
				blacklists.append(_end)
		else: # sorry for writing ugly code
			blacklists.append(_start) 
			blacklists.append(_end)

	def handle_blacklist(blacklist):
		overlap = 0.3
		unravelled_blacklist = []

		start_of_first_day = datetime.datetime.combine(blacklist[0].date(), datetime.time.min)
		end_of_last_day = datetime.datetime.combine(blacklist[-1].date(), datetime.time.max)
		unravelled_blacklist.append(start_of_first_day)

		unravelled_blacklist.extend(blacklist)

		unravelled_blacklist.append(end_of_last_day)

		new_blacklist = []
		for _i in range(int(len(unravelled_blacklist)/2)):
			new_blacklist.append((unravelled_blacklist[2 * _i], unravelled_blacklist[2 * _i + 1]))

		new_cut_noise_ts = []

		for _i in new_blacklist:
			n_cuts = ((_i[1] - _i[0]).seconds - (overlap * 60))/((1 - overlap)*60)
			if math.floor(n_cuts) >= 1:
				pass
			else:
				continue
			for j in range(math.floor(n_cuts)):
				new_start = _i[0] + datetime.timedelta(seconds = (1 -overlap) * 60) * j # ah
				new_end = new_start + datetime.timedelta(seconds = 60)
				new_cut_noise_ts.append((new_start, new_end))

		#print(new_cut_noise_ts[:5])
		cut_sac_file([sta], [new_cut_noise_ts], sac_parent_folder, output_root)
		
		#print(len(new_cut_noise_ts))


	handle_blacklist(blacklists)

''' timestamps: a list of tuples, for noise start and end periods

stations is a list for future extensibility
''' 
def cut_sac_file(stations, timestamps, sac_parent_folder, output_root):

	#sac_parent_folder = "/home/zchoong001/cy1400/cy1400-eqt/no_preproc/TA19/"

	sac_files = [str(path) for path in Path(sac_parent_folder).rglob('*.SAC')]

	#print(sac_files)

	#output_root = "training_files/aceh_noise_13mar_wholeday/aceh_noise_13mar_wholeday"
	output_h5 = output_root + ".hdf5"
	output_csv = output_root + ".csv"

	csv_output_data = {
		"trace_category":[],
		"trace_name":[],
	}

	empty_headers = ["p_arrival_sample", "s_arrival_sample", "snr_db", "coda_end_sample", "receiver_latitude", "receiver_longitude", "receiver_elevation_m"]

	_outhf = h5.File(output_h5, "w")

	_outgrp = _outhf.create_group("data")

	binned_timestamps = {}

	for s_n, station_set in enumerate(timestamps):
		# binned based on year.day
		for x in station_set:
			_year_day = datetime.datetime.strftime(x[0], "%Y.%j")
			_year_day_2 = datetime.datetime.strftime(x[1], "%Y.%j")

			# reject the edge case of timestamp crossing a day...
			if not _year_day == _year_day_2:
				continue

			if not _year_day in binned_timestamps:
				binned_timestamps[_year_day] = [x]
			else:
				binned_timestamps[_year_day].append(x)

		''' for every year_day combination, load the corresponding sac file, it should (in the future) fail gracefully when it cannot find the sac file

		but that's low priority atm 

		this is also SPECIFIC to the station; to extend, i would have to create a new noise data set for every station (?) and then later merge the hdf5 files together'''

		# go through every list in binned_timestamps if fill_gaps = True

		# and convert these to 1 minute timestamps with 0.3 second overlaps based on every large interval given


		for year_day in binned_timestamps:
			print(year_day)
			print(stations[s_n])

			st = read(os.path.join(sac_parent_folder,"*{}*.SAC".format(year_day)))
			st.resample(100.0)
			st.detrend('demean')

			start_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.min)

			for timestamp in binned_timestamps[year_day]:

				# timestamp is a list containing [start_time, end_time]
				
				_tracename = "{}_{}.{}_NO".format(stations[s_n], year_day, datetime.datetime.strftime(timestamp[0], "%H%M%S%f"))

				dt = int((timestamp[0] - start_of_day).total_seconds() * 100)

				print(_tracename)

				csv_output_data["trace_category"].append("noise")
				csv_output_data["trace_name"].append(_tracename)

				datum = np.zeros((6000, 3))
				try:

					for j in range(3):
						datum[:,j] = st[j].data[dt : dt + 6000]
				except:
					print("@@@@")
					continue

				_g = _outgrp.create_dataset(_tracename, (6000, 3), data = datum)
				_g.attrs['trace_category'] = "noise"
				_g.attrs['trace_name'] = _tracename
				_g.attrs['receiver_code'] = stations[s_n]
				_g.attrs['receiver_type'] = "EH"
				_g.attrs['network_code'] = "AC"

				for _header in empty_headers:
					_g.attrs[_header] = ""
	
				_g.attrs["trace_start_time"] = datetime.datetime.strftime(timestamp[0], "%Y-%m-%d %H:%M:%S")



			st.clear()

	_outhf.close()

	d_csv = pd.DataFrame.from_dict(csv_output_data)
	d_csv.to_csv(output_csv, index = False)

	# bin the timestamps into days

	# then for every day, load the corresponding sac file


	# i guess i s

	# try passing in noise periods first to get ~ a few hundred waveforms
	# then write them to a hdf5 file along with the csv info

	# noise info needed:

	# trace_category
	# trace_name

collate_timestamps(args.sta, args.csv_folder, args.sac_parent_folder, args.output_root)