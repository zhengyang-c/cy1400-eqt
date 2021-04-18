'''
DOES POST PROCESSING FOR MULTI-RUNS for a SINGLE STATION


summary:
--------
- while merging csv files, add a column for the relative path to the sac trace e.g. multirun_5/TA19_outputs/sac_picks/*.SAC
- so get the realpath and then keep the last 3 directories

after merging csv files, sort by time.

find the temporal coincidence histogram just to see what kind of fuzz we're looking at 

after that, each entry will have the time distance between itself and the next event

so when going through, it will try to create groups. if there is more than one entry in the group, it'll try to take the average

whether a group or not is created depends on some kind of window e.g. +/-2 seconds 

filter away the sac traces with no p pick or s pick. 
now, the csv file should be filtered. copy (i think, since it's reversible) the sac traces into a new folder 
print the filtered csv file

and now it's ready for manual picking

ALSO the agreement between runs (e.g. 3 out of 5 runs pick this, so agreement = 3) is not that meaningful
if the model is noisy in the first place, then it'll just keep picking noise right 
but i'll leave it in just in case
'''



import argparse


#print(args)


from shutil import copyfile
import glob
import os, sys
import numpy as np
#import matplotlib
#matplotlib.use('TkAgg')
import datetime
#import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd



def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

def datetime_to_str(x, dx):
	return datetime.datetime.strftime(x  + datetime.timedelta(seconds = dx), "%Y-%m-%d %H:%M:%S")

def preprocess(df):
	# drop any row with no p or s arrival pick!!
	df.dropna(subset=['p_arrival_time', 's_arrival_time'], inplace = True)

	df['p_datetime'] = pd.to_datetime(df.p_arrival_time)

	df['event_datetime'] = pd.to_datetime(df.event_start_time)

	#print(df['p_datetime'])
	df.sort_values(by='event_datetime', inplace = True)


	df = df.reset_index(drop=True)

	return df

def concat_df(list_of_csvs):
	df_objects = []
	
	for csv_file in list_of_csvs:
		_tempdf = pd.read_csv(csv_file)
		_relpath = '/'.join(csv_file.split("/")[-3:-1])

		_tempdf['relpath'] = _relpath

		df_objects.append(_tempdf)

	df = pd.concat(df_objects)
	return df

def merging_df(df):

	COINCIDENCE_TIME_RANGE = 2

	
	make_group = True
	_tempgroup = []

	for index, row in df.iterrows():

		curr_time = row["event_datetime"]

		if index == 0:
			prev_time = curr_time
			_tempgroup.append(index)

		df.at[index, 'use_or_not'] = 0

		_dt = (curr_time - prev_time).total_seconds()
		#print(_dt, curr_time, prev_time)

		if not index == 0:
			if _dt < COINCIDENCE_TIME_RANGE:				
				_tempgroup.append(index)

			else: # new event group, dump the previous temp_group
				for ti in _tempgroup:
					df.at[ti, 'agreement'] = len(_tempgroup)

				df.at[_tempgroup[len(_tempgroup)//2], 'use_or_not'] = 1 # keep the middle of the pack

				_tempgroup = [index]

		if index == len(df.index) - 1:

			for ti in _tempgroup:
				df.at[ti, 'agreement'] = len(_tempgroup)
			df.at[_tempgroup[len(_tempgroup)//2], 'use_or_not'] = 1 # keep the middle of the pack
			_tempgroup = [index]

		df.at[index, 'dt'] = _dt

		prev_time = curr_time

	df_filtered = df[df['use_or_not'] == 1]

	return df_filtered

def merge_csv(station, csv_parent_folder, merge_folder, output_csv_name, dry_run = False):

	# just merge csv files can alr
	# then use bash to mv 
	#output_csv = "imported_figures/detections/TA19_nopp_multirun.csv"
	# the output csv shouldn't be in the same directory as the merged stuff

	csv_files = [str(path) for path in Path(csv_parent_folder).rglob('*.csv')]

	parent_of_parent = os.path.dirname(csv_parent_folder)

	#print(csv_files)

	df = concat_df(csv_files)
	
	df = preprocess(df)

	 # after concatenating, the index is messed up 

	''' now loop through and look at the coincidence timings. if it's within 2 seconds, then discard 

	standardise to using event time for file names because the files are saved using event_times
	and this is because sometimes the EQT pick won't have p arrival
	tbh this could be fixed upstream but this is probably fine
	'''

	df_filtered = merging_df(df)



	if not os.path.exists(merge_folder):
		if not dry_run:
			os.makedirs(merge_folder)
		else:
			print("mkdir {}".format(merge_folder))
	if not os.path.exists(os.path.join(merge_folder, "sac_picks")):
		if not dry_run:
			os.makedirs(os.path.join(merge_folder, "sac_picks"))
		else:
			print("mkdir {}".format(os.path.join(merge_folder, "sac_picks")))

	if dry_run:
		print(df)
		print(df_filtered)
	else:
		df.to_csv(os.path.join(merge_folder, output_csv_name + "_raw.csv"), index = False)
		df_filtered.to_csv(os.path.join(merge_folder, output_csv_name + "_filtered.csv"), index = False)

	# move files to a new folder

	failed = []

	for index, row in df_filtered.iterrows():
		# copy the sac files, and then the png files
		_timestamp = row['event_datetime'].strftime("%H%M%S")
		_year = row['event_datetime'].strftime("%Y")
		_day = row['event_datetime'].strftime("%j") # julian day

		_filenames = []

		for cha in ["EHE", "EHN", "EHZ"]:
			_filename = "{}.{}.{}.{}.{}.SAC".format(station, _year, _day, _timestamp, cha)
			_filenames.append(_filename)

		_filenames.append("{}.{}.{}.{}.png".format(station, _year, _day, _timestamp))

		for c, _filename in enumerate(_filenames):
			source_path = os.path.join(csv_parent_folder, row["relpath"],"sac_picks", _filename)
			dest_path = os.path.join(merge_folder, "sac_picks", _filename)

			if not os.path.exists(source_path):
				print("Warning! not found: {}".format(source_path))
				#print("event_datetime", row["event_datetime"])
				#print("event_start_time", row["event_start_time"])
				failed.append((index, source_path))

			else:
				if dry_run:
					print("SOURCE: {}\nDEST:{}\n".format(source_path, dest_path))
				else:
					copyfile(source_path, dest_path)

	print("{} events missing".format(len(failed)))

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description = "One station csv merger for multiple EQT outputs, filtering duplicates. Then, copy the filtered files to a new folder. It also creates two new columns, one for the coincidence time (current event - previous event), and another for the no. of folders reporting that event.The time window used is 2 seconds, so if the present event is within 2 seconds of the previous one, they are grouped together.")

	parser.add_argument('station', type = str, help = "station name e.g. TA19. This is for single station multi runs only.")

	parser.add_argument('csv_folder', type = str, help = "Parent folder containing detection folders from use_eqt.py. Usually it should contain more than one detection folder.")

	parser.add_argument('merge_folder', type = str, help = "The new folder to put all the merged files in.")

	parser.add_argument('output_csv_name', type = str, help = "File name to create filtered and raw merged csv. This is NOT a file path, just the root name.")

	#parser.add_argument('merge_folder', type = str, help = "folder in which to copy the filtered .SAC and .png files")
	parser.add_argument('-d', action='store_true', help = "Flag for DRY RUN. Does not perform any file writing operations, prints wherever possible")

	args = parser.parse_args()

	#merge_csv("TA19", "imported_figures/mergetest", "imported_figures/17mar_aceh_LR1e-6_multi", "17mar_aceh_LR1e-6_testmerge", dry_run = True)
	merge_csv(args.station, args.csv_folder, args.merge_folder, args.output_csv_name, args.d)


#merge_csv(args.csv_folder, args.output_csv)
