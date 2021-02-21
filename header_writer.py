import obspy
from obspy import read
import os
import pandas as pd
import glob
from obspy import UTCDateTime
import argparse


def get_utc(x):
	# 2020-03-25 01:38:08.750000
	try:
		_us = x.split(".")[1]
		[__year, __month, __day] = x.split(" ")[0].split("-")
		[__hour, __minute, __second] = x.split(".")[0].split(" ")[1].split(":")
		
		__year, __month, __day, __hour, __minute, __second, _us = int(__year), int(__month), int(__day), int(__hour), int(__minute), int(__second), int(_us)

		return UTCDateTime(year = __year, month = __month, day = __day, hour = __hour, minute = __minute, second = __second, microsecond =_us)
	except:
		try: # this is pretty bad
			return UTCDateTime(x) 
		except: # checks for NaN
			#sprint(x)
			return -1
def get_day(x):
	#print(x)
	[__year, __month, __day] = x.split(" ")[0].split("-")

	__year, __month, __day = int(__year), int(__month), int(__day)
	#[__hour, __minute, __second] = x.split(".")[0].split(" ")[1].split(":")

	return UTCDateTime(year = __year, month = __month, day = __day)

def main(csv_file, output_file, station_file):


	# load the csv file and match 
	with open(station_file, "r") as f:
		coordinates = f.read().split("\n")		
		coordinates = [y.strip() for x in coordinates if len(x) > 0 for y in x.strip().split("\t") if len(y) > 0 ]

	i = coordinates.index("TA19")
	stlo, stla = float(coordinates[i + 1]), float(coordinates[i+2])

	pick_info = pd.read_csv(csv_file)

	
	#print(pick_info)

	list_of_days = [get_day(x) for x in pick_info["event_start_time"]]

	list_of_p_picks = [get_utc(x) for x in pick_info['p_arrival_time']]
	list_of_s_picks = [get_utc(x) for x in pick_info['s_arrival_time']]
	list_of_end_times = [get_utc(x) for x in pick_info['event_end_time']] 

	with open(output_file, 'w') as f:
		for i in range(len(list_of_p_picks)):
			if list_of_p_picks[i] == -1:
				p_diff = "-12345"
			else:
				p_diff = list_of_p_picks[i] - list_of_days[i]
			if list_of_s_picks[i] == -1:
				s_diff = "-12345"
			else:
				s_diff = list_of_s_picks[i] - list_of_days[i]
			f.write("{},{},{},{}\n".format(stlo, stla, p_diff, s_diff))

				
			#print(list_of_p_picks[0] - list_of_days[0])
			#print(list_of_s_picks[0] - list_of_days[0])
		#print(list_of_end_times[0] - list_of_days[0])

	# get the diffs, write them to a file, then have bash read that asndnifsdjfisdf 

#	print(list_of_days[0])

	#print(list_of_p_picks[0] - list_of_days[0])



	# compute seconds from start of day, and write to a column inside the csv file

	# this will do the arithmetic for the bash script because it is a dumb as a sack of bricks
	# oh my god

	# write p and s arrival times if they apply
	#for file_name in glob.glob(os.path.join(input_folder,"*.SAC")):
	#	print(file_name)

	# match to the .csv file

parser = argparse.ArgumentParser()
parser.add_argument("csv_file") # csv
parser.add_argument("output_file") # next to .csv
parser.add_argument("station_file") #station_info.dat

args = parser.parse_args()

#print(args.input_folder, args.csv_file, args.station_file)
main(args.csv_file, args.output_file, args.station_file)