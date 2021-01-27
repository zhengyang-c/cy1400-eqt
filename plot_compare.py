import glob
import os
import argparse
import numpy as np
from obspy import read
import obspy

def main(input_file, *input_folders):

	# input file: basically a log file as printed above, with one header row
	# along with 4 columns, {$n, $timestamp.png, (1/0), (1/0) ... }

	print(input_file)
	print(input_folders[0])

	# input_folders: an ORDERED LIST of where the SAC files are 

	global_list = []

	with open(input_file, 'r') as f:
		for c, line in enumerate(f):
			if c == 0:
				continue
			global_list.append(line.strip().split("\t"))
	print(global_list)

	for line in global_list:
		event = line[1].split(".")
		_sta = event[0]
		_year = (event[1])
		_day = (event[2])
		_time = event[3]

		for _channel in ["EHZ", "EHE", "EHN"]:
			file_name = "AC.{}.00.{}.D.{}.{}.000000.SAC*".format(_sta, _year, _day)



	# reading in the input file, STA.YEAR.DAY.TIMESTAMP.png
	# determine the day 

	# for each folder in input folders, (folder should immediately contain the SAC files)
	# if it's a new day, load the corresponding SAC file ()
	# if not a new day, don't load since this presumably takes time 
	
	# plot 3 channels vs 3 channels in a top down, maybe use a colour or something
	# to indicate which was the one that got detected

	

	pass


parser = argparse.ArgumentParser()
parser.add_argument('input_file', type = str)
parser.add_argument('input_folder', type = str, nargs='*')

args = parser.parse_args()

main(args.input_file, args.input_folder)

#../../EOS_SAC/TA19 and no_preproc/TA19
