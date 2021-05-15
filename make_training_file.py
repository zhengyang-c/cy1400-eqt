# this is meant to be run on the gekko server
"""
input: csv file with only the waveforms you want to use 
"""



import h5py
import numpy as np
from obspy import UTCDateTime
import obspy
import os
import math
import json
import datetime
import argparse

import pandas as pd






def main(sta, input_eqt_csv, input_sac_folder, output_root, dry_run = False):
	#input_selection_csv = "ta19_nopp.csv" 
	# manually picked, the files/traces you want to train on
	# technically my text file is comma separated, so...

	#input_eqt_csv = "imported_figures/detections_TA19_no_preproc/TA19_outputs/X_prediction_results.csv"
	
	#input_eqt_csv = "detections/21mar_default_merged/21mar_default_filtered.csv"
	# eqt output, need the event times and metadata from here

	#input_sac_folder = "no_preproc/TA19"
	# sac trimming, just take sac data from here lol

	station_file = "station_info.dat" # ok this is hard coded


	#output_root = "training_files/27mar_AOnly"
	output_filename = "{}.hdf5".format(output_root)
	print(output_filename)
	output_csv_file = "{}.csv".format(output_root)

	# load csv file with all the metadata (my use case: picks that were already made by EQT)


	pick_info = pd.read_csv(input_eqt_csv)

	pick_info['dt_start'] = pd.to_datetime(pick_info.event_start_time)
	pick_info['dt_end'] = pd.to_datetime(pick_info.event_end_time)
	pick_info['dt_p'] = pd.to_datetime(pick_info.p_arrival_time)
	pick_info['dt_s'] = pd.to_datetime(pick_info.s_arrival_time)
	pick_info['snr_db'] = "" 
	pick_info['snr_db'] = pick_info['snr_db'].astype('object')

	# sort by event time 

	pick_info.sort_values(by=['dt_start'], inplace = True)
	pick_info = pick_info.reset_index(drop=True)


	# get year_day, calculate the sample index for p_arrival_sample, coda_end_sample, s_arrival sample
	# train on -15 seconds and 55 seconds from p arrival
	# also calculate the start_index and end_index (-10s and +50s from p arrival)

	for index, row in pick_info.iterrows():

		year_day = datetime.datetime.strftime(row.dt_start, "%Y.%j")

		start_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.min)
		
		pick_info.at[index, "year_day"] = year_day

		# these samples are wrt to the start of the waveform, so it's 100 by defn
		pick_info.at[index, "p_arrival_sample"] = 500
		pick_info.at[index, "s_arrival_sample"] = int((row.dt_s - row.dt_p).total_seconds() * 100) + 500
		pick_info.at[index, "coda_end_sample"] = int((row.dt_end - row.dt_p).total_seconds() * 100) + 500

		# snr calculation is not really correct, will want to fix in the future
		pick_info.at[index, "snr_db"] = [(row.p_snr + row.s_snr)/2 for j in range(3)] # arithmetic mean

		dt = (row.dt_p - start_of_day).total_seconds()

		# i can do this because each SAC file is for one day only

		pick_info.at[index, "abs_start_index"] = int(dt * 100) - 500
		pick_info.at[index, "trace_category"] = "earthquake_local"


		trace_start_time = row.dt_p - datetime.timedelta(seconds = -5)
		pick_info.at[index, "trace_name"] = "{}_{}_EV".format(sta, datetime.datetime.strftime(row.dt_start, "%Y_%j.%H%M%S.%f"))
		pick_info.at[index, "trace_start_time"] = trace_start_time


	# could just reuse the existing csv file.. 
	csv_output_data = {
		"network_code":[], 
		"receiver_code":[],
		"receiver_type":[],
		"receiver_latitude":[],
		"receiver_longitude":[],
		"receiver_elevation_m":[],
		"p_arrival_sample": [],
		"s_arrival_sample": [],
		"snr_db":[], 
		"coda_end_sample":[],
		"trace_category":[],
		"trace_start_time":[],
		"trace_name":[],
	}

	headers = ['p_arrival_sample', 's_arrival_sample', 'snr_db', 'coda_end_sample', 'trace_category', 'trace_start_time', 'receiver_type', 'network_code', 'receiver_latitude', 'receiver_longitude', 'receiver_elevation_m', 'receiver_code', 'trace_name']

		# add a dry run option

	if not dry_run:


		hf = h5py.File(output_filename, 'w')
		grp = hf.create_group("data")
		
		prev_year_day = ""
		for index, row in pick_info.iterrows():
			print(index)
		#	pass

			# for each year_day, load the corresponding sac file
			# load the data into datum
			
			datum = np.zeros((6000, 3))

			if prev_year_day != row.year_day:
				st = obspy.read("{}/*{}*C".format(input_sac_folder, row.year_day))
				st.resample(100.0)
				st.detrend('demean')

			elif prev_year_day == row.year_day:
				pass

			prev_year_day = row.year_day

			try:
				for j in range(3):
					datum[:,j] = st[j].data[int(row.abs_start_index) : int(row.abs_start_index) + 6000] 

					# could break if the event is within the 1st four seconds of the day
					# or if the sac file doesn't start from 000000 but that's unlikely so that's ok
			except:
				print("help")
				continue

			_tracename = "{}_{}_EV".format(sta, datetime.datetime.strftime(row.trace_start_time, "%Y_%j.%H%M%S%f"))
			#_tracename = "{}_{}.{}_NO".format(stations[s_n], year_day, datetime.datetime.strftime(timestamp[0], "%H%M%S%f"))

			print(_tracename)

			_metadata = {}

			_metadata['trace_category'] = "earthquake_local"
			_metadata['trace_name'] = _tracename
			_metadata['p_arrival_sample'] = row.p_arrival_sample
			_metadata['s_arrival_sample'] = row.s_arrival_sample
			_metadata['snr_db'] = row.snr_db
			_metadata['coda_end_sample'] = row.coda_end_sample
			_metadata['trace_start_time'] = row.trace_start_time
			_metadata['receiver_type'] = "EH"
			_metadata['network_code'] = "AC"
			_metadata["receiver_latitude"] = ""
			_metadata["receiver_longitude"] = ""
			_metadata["receiver_elevation_m"] = ""
			_metadata['receiver_code'] = row.station

			# save metadata in temporary dictionary, then write to both the hdf5 dataset and csv file while looping through the headers


			#csv_output_data["trace_category"].append("earthquake_local")
			#csv_output_data["trace_name"].append(_tracename)

			_g = grp.create_dataset(_tracename, (6000, 3), data = datum)

			for header in _metadata:
				csv_output_data[header].append(_metadata[header])

				_g.attrs[header] = _metadata[header]


		hf.close()	

		d_csv = pd.DataFrame.from_dict(csv_output_data)
		d_csv.to_csv(output_csv_file, index = False)
	else:
		for index, row in pick_info.iterrows():
			print("start_time:", row.trace_start_time)
			print("p_arrival_sample:", row.p_arrival_sample)
			print("s_arrival_sample:", row.s_arrival_sample)


#main("TA19", "training_files/aceh_27mar_EV/21mar_default_multi_repicked.txt", "training_files/aceh_27mar_EV/A_only_default1month", dry_run = True)


parser = argparse.ArgumentParser(description = "take EQT picks from single station data and make a hdf5 training file")


# def main(sta, input_eqt_csv, input_sac_folder, output_root, dry_run = False):
parser.add_argument('sta', type = str, help = "Station name")
parser.add_argument('input_eqt_csv', type = str, help = "CSV file with all the metadata from EQT")
parser.add_argument('input_sac_folder', type = str, help = "original SAC files to slice from")
parser.add_argument('output_root', type = str, help = "filepath to file root without file extension at the back")
parser.add_argument('-d', '--dry', action = "store_true", help = "dry run")

#parser.add_argument('manual_picks', type = str, help = "Path to txt file of manual picks (this should not require any processing)")

#parser.add_argument('csv_output', type = str, help = "Path to new csv file with all noise removed")
args = parser.parse_args()
if __name__ == "__main__":
	main(args.sta, args.input_eqt_csv, args.input_sac_folder, args.output_root, args.dry)

# shift p_arrival time to sample 500



# for each event

# convert png time to like a UTCDATETIME
# match png times with event_start_times
# using the indices get the corresponding s and p arrivals

# then can load the SAC file
# trace_start_time in UTC Datetime
# trim
# resample
# compute sample number of S and P
# generate trace name



# output: csv file with 

# input: csv file saying which detections you chose
# input: csv file with the sac picks / arrival times
# input: path to the SAC file 

# load 

# output hdf5 file:
# data/ {trace_name 1, trace_name 2}

# inside each trace_name_1 is a (6000, 3) array

# output csv file:

# V network_code  AC
# V receiver code TA19
# V receiver_type EH
# receiver latitude (take from station.dat)
# receiver_longitude
# receiver_elevation
# V p_arrival_sample arrival from the beginning of file, usually around 5 - 10, 100 Hz
# V p_status manual
# p_weight (no clue, probably a expression of confidence)
# p_travel_sec (travel time for the p wave (after inversion))
# V s_arrival_sample (from beginning of file)
# s_weight (probability?)
# V s_status
# V trace_start_time # uhh
# V trace_category (noise, earthquake_local)
# V trace_name (for the hdf5)

