from subprocess import check_output
import datetime
import pandas as pd
import argparse


def main():

	#input_csv = "real_postprocessing/julaug_20_assoc/julaug20_compiled_customfilter.csv"

	sac_file_csv = "all_jul_aug_2020.csv"

	output_csv = "all_jul_aug_2020_ts.csv"
	#df = pd.read_csv(input_csv)
	sac_df = pd.read_csv(sac_file_csv)
	"""
	want to eventualy move this code into multi_station.py s.t.
	i can generate starting sequences more reliably? currently it just uses all the sac files inside and doesn't handle partial days very well

	tbf chenyu's run on jul-aug might have this problem

	so i should probably fix it fml

	need to find:
	(1) the missing partial day files that would have been excluded
	(2) from the raw list of detections, the maximum gaps between events (?) i need access to the hdf5 csv 
	(3) or, from the available SAC files, infer the maximum possible uptime

	(4) the "empirical" uptime can only come from the hdf5_csv


	so i need to patch for julaug, which is fine i guess, i can do this next week

	"""
	for index, row in sac_df.iterrows():
		# 108 characters for filename hehe

		out = check_output(["saclst", "KZDATE", "KZTIME", "B", "E", "f", row.filepath])

		out = [x for x in out.decode('UTF-8').strip().split(" ") if x != ""]

		sac_df.at[index, "kzdate"] = out[1]
		sac_df.at[index, "kztime"] = out[2]
		sac_df.at[index, "B"] = out[3]
		sac_df.at[index, "E"] = out[4]


	sac_df.to_csv(output_csv, index = False)



	# with the timestamps of each detection, need to infer the source file, without having information about the 
	# original hdf5 csv that is generated at the start


	# first use the full day file? and if cannot, then look for partial day files with jday - 1

	# tbh i should check the start and end times of the SAC files right that would clear up ALL the ambiguity



def sac_file_checker():

	# probably not going to write this 
	# because i can just regenerate the entire archive and it would honestly be easier
	# than patching it 

	input_csv = "~/julaug20_compiled_customfilter.csv"
	#input_csv = "julaug_customfilter_matched_patch.csv"
	output_csv = "julaug_customfilter_matched_patch.csv"

	sac_csv = "~/all_jul_aug_2020_ts.csv"
	s_df = pd.read_csv(sac_csv)

	# this is the matcher function

	df = pd.read_csv(input_csv)

	df["event_start_time"] = pd.to_datetime(df["event_start_time"])




	for index, row in s_df.iterrows():
		s_df.at[index, "start_dt"] = datetime.datetime.strptime("{} {}".format(row.kzdate, row.kztime), "%Y/%m/%d %H:%M:%S.%f")

	for index, row in df.iterrows():
		# get station
		# this feel like a n^2 search omg this is going to be so slow
		jday = int(datetime.datetime.strftime(row.event_start_time, "%j"))
		# filter by station, jday
		# see number of candidates

		_df = s_df[((s_df["jday"] == jday) & (s_df["station"] == row.station))]

		# if there's more than 1 option, need to tie break
		# want to save the file to look in i.e. 
		# there's a lot of duplicate work done e.g. a lot of common station days but at the same time....
		# it's more of a O(n) since the second search just uses filtering and is not a brute force search which is still acceptable

		# want to check that the time stamp is within the kzdate and time

		print(row.station, jday)

		for s_index, s_row in _df.iterrows():
			_df.at[s_index, "is_within"] = (((row.event_start_time - s_row.start_dt).total_seconds()) < s_row.E) and (((row.event_start_time - s_row.start_dt).total_seconds()) > s_row.B) 

			print("event_start_time", row.event_start_time)
			print("row_start_time", s_row.start_dt)
			print("is within: ", (((row.event_start_time - s_row.start_dt).total_seconds()) < s_row.E - 125) and (((row.event_start_time - s_row.start_dt).total_seconds()) > s_row.B - 30))

		_fdf = _df[_df["is_within"] == True]


		print(_fdf["start_dt"])
		# if len(_fdf) != 3:
		# 	# we have a problem, log and fix it later (?)
		# 	# or attempt to search for other jdays

		# 	with open("log/sac_timing.txt", "a") as f:
		# 		#print(row.event_start_time, row.station)
		# 		f.write("{} {}\n".format(row.event_start_time, row.station))

			

		search_term = _fdf["filepath"].iloc[0]

		df.at[index, "source_file"] = search_term



	df = df.merge(sac_csv, how = "left", left_on = "source_file", right_on = "filepath") 

	for index, row in df.iterrows():
		for x in [".EHE.", ".EHN.", ".EHZ."]:
			if x in row.source_file:
				search_term = row.source_file.replace(x, ".EH*.")
				break
		df.at[index, "source_file"] = search_term


	df.to_csv(output_csv, index = False)




def diy_filter():

	input_csv = "real_postprocessing/julaug_20_assoc/julaug20_compiled_customfilter.csv"
	output_csv = ""

	"""
	not really sure what other filters i'll use in the future aside from local file root but
	i guess this bit can be manual :) 
	"""

	df = pd.read_csv(input_csv)
sac_file_checker()
