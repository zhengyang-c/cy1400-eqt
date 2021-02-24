import matplotlib
#matplotlib.use('TkAgg')
#from EQTransformer.utils.hdf5_maker import preprocessor

import numpy as np
import os
import math
#import matplotlib
#import matplotlib.pyplot as plt
import datetime
from helpme import *
import sys
import re
import json
import datetime
import pandas as pd
import glob
import copy
import argparse

def convert(input_folder, station_info_file, station_name, n_processor = 4):

	''' it'll only operate on 1 station so it's more atomic / and can be controlled in bash i guess


	start_yearday format: 2020_085 
	four digit year, an underscore, and a julian date
	'''

	# needed for EqT hdf5 converter
	station_json_output = 'station_list.json'

	# start_day = datetime.datetime.strptime(start_yearday, "%Y_%j")
	# end_day = datetime.datetime.strptime(end_yearday, "%Y_%j")
	# n_days = (end_day - start_day).days

	# date_list = [end_day - datetime.timedelta(days = x) for x in range(n_days + 1)]

	pre_json = {station_name:{"network": "AC", "channels":["EHZ", "EHE", "EHN"]}}


	with open(station_info_file, "r") as f:
		coordinates = f.read().split("\n")
		
		coordinates = [y.strip() for x in coordinates if len(x) > 0 for y in x.strip().split("\t") if len(y) > 0 ]

		_i = coordinates.index(station)

	pre_json["coords"] = [100, float(coordinates[_i + 1]), float(coordinates[_i + 2])]

	with open(station_json_output, 'w') as f:
		json.dump(pre_json, f)

	print(input_folder)
	#preprocessor(mseed_dir=input_folder, stations_json= station_json_output, overlap=0.3, n_processor=n_processor)


parser = argparse.ArgumentParser()

parser.add_argument('input_folder')
parser.add_argument('station_info_file')
parser.add_argument('station_name')
parser.add_argument('--n_processor', type = int)

#parser.add_argument('json_output', help = "this is an intermediate file needed by EqT")

#parser.add_argument('output_folder')

args = parser.parse_args()

convert(args.input_folder, args.station_info_file, args.start_yearday, args.end_yearday, args.station_name, args.n_processor)