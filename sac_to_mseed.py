import argparse

import obspy
from obspy import read
import numpy as np
import os
import math
from datetime import datetime
from helpme import *
import sys
import re
import json
import datetime
import pandas as pd
import glob
import copy


def convert(input_folder):
	"""
	by default, the mseed folder will be mseed_input_folder
	"""
	mseed_folder = "mseed_" + os.path.basename(input_folder)

	print(mseed_folder)

	if not os.path.exists(mseed_folder):
		os.makedirs(mseed_folder)

	folders = [x[0] for x in os.walk(input_folder)]

	folders = list(filter(lambda x: re.search(r"\/\D{2,3}\d{2,3}", x), folders))
	#all_files = []

	#print(folders)

	for folder in folders:
		files = {}

		for _file in os.listdir(folder):
			print(_file)
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

	for _station, _all_days in all_files:

		valid_days = []
		for day in _all_days:
			valid_days.append(day)

		valid_days.sort(key = lambda x: (x.split("_")[0], x.split("_")[1]))

		# for every listed file in the year list, merge all matching files in the SAC folder 

		#print(valid_days)

		for _channel in ["EHE", "EHN", "EHZ"]:

			output_file_name = "{}__{}__{}__{}__{}.mseed".format("AC", valid_days[0].split("_")[0], valid_days[0].split("_")[1], _station, _channel)

			if not os.path.exists(os.path.join(mseed_folder, _station, output_file_name)):

				for c, valid_day in enumerate(valid_days):

					_file_name = "AC.{}.00.{}.D.{}.{}.*".format(_station, _channel, valid_day.split("_")[0], valid_day.split("_")[1] )
					if c == 0:
						_st = read(os.path.join(input_folder, _station, _file_name))
					else:
						_st += read(os.path.join(input_folder, _station, _file_name))
						#print("yes but ", _file_name)

				_st.merge(method = 1) 
				# documented at https://docs.obspy.org/packages/autogen/obspy.core.trace.Trace.__add__.html#handling-overlaps
				# this will prioritise the newer trace in the case of an overlap

				# just take the year and month of the first day because i'm not bothered enough right now

				if not os.path.exists(os.path.join(mseed_folder, _station)):
					os.makedirs(os.path.join(mseed_folder, _station))
				

				_st.write(os.path.join(mseed_folder, _station, output_file_name))

				_st.clear()

parser = argparse.ArgumentParser()

#parser.add_argument('station_info')
#parser.add_argument('json_output', help = "this is an intermediate file needed by EqT")
parser.add_argument('input_folder')
#parser.add_argument('output_folder')

args = parser.parse_args()

convert(args.input_folder)
