import pandas as pd
import datetime
import argparse
from subprocess import check_output

from pathlib import Path

"""
input: CSV file from multi_station.py
absolute filepath | station | year | jday | start_time | fullday

missing info: want to know B and E time from saclst


Steps:
1) --get and -o option for multi_station.py to get all SAC files in specified folder (currently hardcoded)
2) saclst to find length of each SAC file, write the start and end date times into a CSV file 
3) find overlaps:

(StartDate1 <= EndDate2) and (StartDate2 <= EndDate1) from 
https://stackoverflow.com/questions/325933/determine-whether-two-date-ranges-overlap


first fill the list with 000000 day files, since those are well-behaved
as a sanity check, verify that none of them overlap with each other (n^2)


next, for each file that doesn't have "000000" at the back, check if it has any overlap with all of the 00 files.
if it does, want to know:
	using a 2s exclusion window (hmmmm) 
	absolute duration of overlap i.e. if it's like 5 seconds just don't bother
	generate blacklist to ignore (start and end dates for each station)
	blacklists could be a json file? or csv kind of the same effect

next, apply the blacklist (global blacklist so it's only one file) using the hdf5 generation process


lastly, how many times were was agreement = 2 * threshold? this would mean that there were good detections w overlap
running awk to verify for the 7jul dataset.
NONE
None of theM
"""


def main():
	input_csv = "station_time/all_jul_aug_2020.csv"

	df = pd.read_csv(input_csv)


	# first generate saclst start and end times

	# not sure if saclst can handle long file names, but they are under 128 char so it's ok

	for index, row in df.iterrows():

		out = check_output(["saclst", "B", "E", "KZDATE", "KZTIME", "f", row.filepath])
		out = [(x) for x in out.decode('UTF-8').strip().split(" ") if x != ""]

		df.at[index, "B"] = float(out[1])
		df.at[index, "E"] = float(out[2])
		df.at[index, "KZDATE"] = str(out[3])
		df.at[index, "KZTIME"] = str(out[4])

		#

	df.to_csv(input_csv, index = False)

	# gf = df.groupby(by = "station")

	# for sta, _df in gf:
	# 	# find number of non-full day files. if there are none, there is nothing to do

	# 	# sadly all of them have non-full day files (probably at the start)

	# 	# if (len(_df[_df["fullday"]]) == 0):
	# 	# 	print("no need fix")

	# 	full_df = _df[_df["fullday"] == 1]

		# do sanity check for full_df

		  

		


main()

