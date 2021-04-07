# this is meant to be run on EQT

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


parser = argparse.ArgumentParser(description = "take EQT picks from single station data and make a hdf5 training file")

parser.add_argument('input_selection_csv', type = str, help = "The manual picks / gradings")
parser.add_argument('input_eqt_csv', type = str, help = "CSV file with all the metadata from EQT")
parser.add_argument('input_sac_folder', type = str, help = "original SAC files")
parser.add_argument('output_root', type = str, help = "filepath to root without file extension at the back")

#parser.add_argument('manual_picks', type = str, help = "Path to txt file of manual picks (this should not require any processing)")

#parser.add_argument('csv_output', type = str, help = "Path to new csv file with all noise removed")
args = parser.parse_args()


def main(sta, input_selection_csv, output_root, dry_run = False):
	#input_selection_csv = "ta19_nopp.csv" 
	# manually picked, the files/traces you want to train on
	# technically my text file is comma separated, so...

	#input_eqt_csv = "imported_figures/detections_TA19_no_preproc/TA19_outputs/X_prediction_results.csv"
	
	input_eqt_csv = "detections/21mar_default_merged/21mar_default_filtered.csv"
	# eqt output, need the event times and metadata from here

	input_sac_folder = "no_preproc/TA19"
	# sac trimming, just take sac data from here lol

	station_file = "station_info.dat"


	#output_root = "training_files/27mar_AOnly"
	output_filename = "{}.hdf5".format(output_root)
	output_csv_file = "{}.csv".format(output_root)

	list_of_chosen_waveforms = []

	grading_structure  = {"a": {"max": 514, "current": 0}, "b": {"max": 0, "current":0}}

	# i can set no. of WF to use. if -1, then use all available

	with open(input_selection_csv, "r") as f:
		for line in f:
			[_a, _b] = line.strip().split(",")
			_b = _b.lower()
			#_b: grade
			#_a: event label
			
			if _b in grading_structure.keys():
				grading_structure[_b]["current"] += 1

				if grading_structure[_b]["current"] <= grading_structure[_b]["max"]:
					list_of_chosen_waveforms.append(_a)

	# load pick file


	pick_info = pd.read_csv(input_eqt_csv)

	#print(pick_info.head())

	def get_utc(x):
		try:
			return UTCDateTime(datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
		except:
			return UTCDateTime(datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f"))

	#list_of_end_picks = [get_utc(x) for x in list(pick_info['event_end_time'])] # for coda

	#list_of_p_arrival = [get_utc(x) for x in list(pick_info['p_arrival_time'])]
	#list_of_s_arrival = [get_utc(x) for x in list(pick_info['s_arrival_time'])]

	list_of_start_picks = [get_utc(x) for x in list(pick_info['event_start_time'])]
	list_of_end_picks =   [get_utc(x) for x in list(pick_info['event_end_time'])]
	list_of_p_arrival = list(pick_info['p_arrival_time'])
	list_of_s_arrival = list(pick_info['s_arrival_time'])

	list_of_s_prob = list(pick_info['s_probability'])
	list_of_p_prob = list(pick_info['p_probability'])

	list_of_p_snr = list(pick_info['p_snr'])
	list_of_s_snr = list(pick_info['s_snr'])

	# coda_end: use the event_end_time u dum dum

	# snr_db: looks like SNR for all 3 channels? just try and put 20 for everything??
	# or use geometric mean of P_SNR and S_SNR

	indices_actual_picks = []

	##
	## MATCHING, append indices that point to the csv data (also because i dno't like pandas)
	##
	##
	## there are probably issues for extensibility i.e. more csv file inputs because what i did with noise was to merge the hdf5s

	for c, pick in enumerate(list_of_chosen_waveforms):
		#print(pick)
		[_sta, _year, _day, _time, _] = pick.split(".")
		_event_time = UTCDateTime("{},{},{}".format(_year,_day,_time))

		for d, _pick in enumerate(list_of_start_picks): # this is not very efficient heh
			if -2 <= (_pick - _event_time) <= 2:
							
				try: # should not be an issue with multi run and merging, but just to be sure
					assert UTCDateTime(list_of_p_arrival[d])
					assert UTCDateTime(list_of_s_arrival[d])
					indices_actual_picks.append(d)
				except:	
					continue


	#print(indices_actual_picks)
	#print(len(indices_actual_picks))

	# TODO add check if the file exists

	if not dry_run:
		hf = h5py.File(output_filename, 'w')
		grp = hf.create_group("data")
	#dset = grp.create_dataset("TA19_test", (6000, 3), dtype = 'i')

	csv_output_data = {
		#"network_code":[], 
		#"receiver_code":[],
		#"receiver_type":[],
		#"receiver_latitude":[],
		#"receiver_longitude":[],
		#"receiver_elevation_m":[],
		"p_arrival_sample": [],
		"s_arrival_sample": [],
		"snr_db":[], 
		"coda_end_sample":[],
		"trace_category":[],
		#"trace_start_time":[],
		"trace_name":[],
	}

	binned_indices = {}

	
	# i pick is not really used / is the filename
	# 
	for i_source in indices_actual_picks:
		# collate year_day
		_year_day = datetime.datetime.strftime(list_of_start_picks[i_source], "%Y.%j")

		if _year_day not in binned_indices:
			binned_indices[_year_day] = [i_source]
		else:
			binned_indices[_year_day].append(i_source)

	print(binned_indices)
'''
	if not dry_run:
		for i in indices_actual_picks:
			# calculate coda, snrs 
			# 
			#print(list_of_chosen_waveforms[i[0]])	
			[_sta, _year, _day, _time, _] = list_of_chosen_waveforms[i[0]].split(".")
			length_of_event = list_of_end_picks[i[1]] - list_of_start_picks[i[1]]

			#print(length_of_event)

			# modify generate_noise.py


			# change this to load one year day, and then trim from there
			#st = obspy.read(os.path.join(input_sac_folder, "{}.{}.{}.{}.*.SAC".format(_sta, _year, _day, _time)))
			stt = st.copy()

			stt.resample(100.0)

			_start = stt[0].stats.starttime

			#print(_start)


			intended_start_time = get_utc(list_of_p_arrival[i[1]]) - 5
			intended_end_time = get_utc(list_of_p_arrival[i[1]]) + 55

			#print(intended_start_time)
			#print(intended_end_time)
			#print(stt[0].stats.endtime)

			stt.trim(intended_start_time, intended_end_time, nearest_sample = False)

			_p_sample = 500 # well it could be off by 1 sample
			_s_sample = int(_p_sample + 100 * (get_utc(list_of_s_arrival[i[1]]) - get_utc(list_of_p_arrival[i[1]])))

			_coda = int(_p_sample + 100 * (list_of_end_picks[i[1]] - get_utc(list_of_p_arrival[i[1]])))
			

			snrs = [(float(list_of_p_snr[i[1]]) + float(list_of_s_snr[i[1]]))/2 for j in range(3)] # should use the snr calculation used by them ufgh
			
			
			datum = np.zeros((6000, 3))
			for j in range(3):
				datum[:,j] = stt[j].data[:6000]

			#print(datum)
			ds_name = "{}_{}.{}.{}_EV".format(_sta, _year, _day, _time)
			print(ds_name)
			csv_output_data["coda_end_sample"].append(_coda)
			csv_output_data["trace_name"].append(ds_name)
			csv_output_data["p_arrival_sample"].append(_p_sample)
			csv_output_data["s_arrival_sample"].append(_s_sample)
			csv_output_data["trace_category"].append("earthquake_local")
			csv_output_data["snr_db"].append(snrs)
			#csv_output_data["trace_name"].append(ds_name)

			_g = grp.create_dataset(ds_name, (6000, 3), data = datum)
			_g.attrs['p_arrival_sample'] = _p_sample
			_g.attrs['s_arrival_sample'] = _s_sample
			_g.attrs['snr_db'] = snrs
			_g.attrs['coda_end_sample'] = _coda
			_g.attrs['trace_category'] = "earthquake_local"
			_g.attrs['trace_start_time'] = str(UTCDateTime(intended_start_time))
			_g.attrs['receiver_type'] = "EH"
			_g.attrs['network_code'] = "AC"
			_g.attrs["receiver_latitude"] = ""
			_g.attrs["receiver_longitude"] = ""
			_g.attrs["receiver_elevation_m"] = ""
			_g.attrs['receiver_code'] = _sta
			_g.attrs['trace_name'] = ds_name


			#print(stt)	

			# sampling rate --> 250
			# sampling rate --> 100
		hf.close()

		d_csv = pd.DataFrame.from_dict(csv_output_data)
		d_csv.to_csv(output_csv_file, index = False)
	else:
		for i in indices_actual_picks:
			print(i)


'''

main("TA19", "training_files/aceh_27mar_EV/21mar_default_multi_repicked.txt", "training_files/aceh_27mar_EV/A_only_default1month", dry_run = True)

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




"""
1) get list of traces 

2) for each trace, 
- trim the file to 6000 samples exactly, with p arrival at 5s
--> get p arrival time from the .csv file
--> get s arrival time from the .csv file
--> compute the no. of samples / (where it is) relative to the start of the trim

- resample to 100Hz 



"""