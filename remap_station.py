import os
import pandas as pd
import shutil
import numpy as np
from pathlib import Path
import argparse
import datetime
import time
import json

# should map station names first then map station coordinates?

def parse_station_info(input_file):

	station_info = {}

	with open(input_file, 'r') as f:
		for line in f:
			sta, lon, lat = line.strip().split("\t")
			station_info[sta] = {"lon": lon, "lat": lat}	
	return station_info


def sac_remapping(search_folder, search_term, map_file, station_file, output_file):

	search_term = "*SAC"
	station_info = parse_station_info(station_file)
	station_map = create_map(map_file)

	output_str = "#!/bin/bash\n"
	mv_str = "#!/bin/bash\n"

	for sac_file in Path(search_folder).rglob(search_term):

		resp = sac_mapper(str(sac_file), station_map, station_info)

		output_str += resp["output_str"]

		if "original_path" in resp:
			mv_str += "mv {} {}\n".format(resp["original_path"], resp["new_path"])


	with open(output_file, 'w') as f:
		f.write(output_str)

	time.sleep(1)
	#os.chmod(output_file, 0o775)

	time.sleep(1)

	#with open(output_file, 'w') as f:
	#	f.write(mv_str)
	#subprocess.call(["{}".format(output_file)])	


def json_remapping(json_file, map_file, station_info_file, output_file):
	print("what")

	station_info = parse_station_info(station_info_file)

	station_map = create_map(map_file)

	with open(json_file, 'r') as f:
		phase_dict = json.load(f)

	event_list = list(phase_dict.keys())

	for event in event_list:
		try:
			ts = datetime.datetime.strptime(phase_dict[event]["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
		except:
			ts = datetime.datetime.strptime(phase_dict[event]["timestamp"], "%Y-%m-%d %H:%M:%S")

		y_m = datetime.datetime.strftime(ts, "%Y_%m")

		if not y_m in station_map:
			continue

		#print("wow")

		for station in list(phase_dict[event]["data"].keys()):
			if station in station_map[y_m]:
				print("old station", station)				
				new_station = station_map[y_m][station]
				print("new station,", new_station)
				phase_dict[event]["data"][new_station] = phase_dict[event]["data"].pop(station)



	with open(output_file, 'w') as f:
		json.dump(phase_dict, f, indent = 4)


def sac_mapper(sac_file, station_map, station_info):

	# you also need the new station coordinates........

	#station_map = create_map(map_file)

	

	sac_basepath = sac_file.split("/")[-1]
	sac_folder = "/".join(sac_file.split("/")[:-1])

	# station name is derived from the filename so it won't be affected by the appended lowercase letters
	_station = sac_basepath.split(".")[0]


	_year, _jday = sac_basepath.split(".")[1:3]

	_dt = datetime.datetime.strptime("{}.{}".format(_year, _jday), "%Y.%j")

	#waveform timestamp
	_wf_ts = datetime.datetime.strftime(_dt, "%Y_%m")

	# fix the wrongly copied over

	# build keylist

	output_list = []
	for _i in station_map:
		for _j in station_map[_i]:
			output_list.append(station_map[_i][_j])

	#print(output_list)
	reverse_station_map = {}

	for _i in station_map:
		reverse_station_map[_i] = {}
		for _j in station_map[_i]:
			reverse_station_map[_i][station_map[_i][_j]] = _j

	#print(reverse_station_map)

	if _wf_ts in station_map: # year month
	#if _station in output_list:

		# write header first 
		# add to some sort of list to keep track so maybe return to the sac_remapping function
		
		#if _station in station_map[_wf_ts]: # station name
		if _station in reverse_station_map[_wf_ts]:
			print(sac_file)
			print(_station)

			print(reverse_station_map[_wf_ts])

			# maybe return a dictionary
			# generate the str here 
			# 
			#
			
			#new_station = station_map[_wf_ts][_station]
			new_station = reverse_station_map[_wf_ts][_station]
			#try: 
			output_str = "printf \"r {}\\nch STLA {} STLO {} KSTNM {}\\nwh\\nq\\n\" | sac\n".format(
				sac_file,
				station_info[new_station]["lat"],
				station_info[new_station]["lon"],
				new_station
				)

			#new_path = os.path.join(sac_folder, station_map[_wf_ts][_station] + "." + ".".join(sac_basepath.split(".")[1:]))
			new_path = os.path.join(sac_folder, reverse_station_map[_wf_ts][_station] + "." + ".".join(sac_basepath.split(".")[1:]))

			return {
				"output_str": output_str,
				"original_path": sac_file,
				"new_path": new_path
			}
			# except:
			# 	# do some logging
			# 	print("ERROR", sac_file, _station)
			# 	return {"output_str": ""}
			# 	
			# 	
	return {"output_str": ""}		
	# return {"output_str": "printf \"r {}\\nch STLA {} STLO {} \\nwh\\nq\\n\" | sac\n".format(
	# 				sac_file,
	# 				station_info[_station]["lat"],
	# 				station_info[_station]["lon"],
	# 				)}

	# given some file name, rename it
	# change the staion header
	# 
	# also change the station coordinates but not available yet (supposing it is)
	

	# the remapping is done via like 
	# 
	# 
	# check if the date time of the file is to be remapped

	# i think change the headers first then 
	# change the file name

	



def csv_remapping(search_folder, rel_search_term, map_file, station_file, dry_run = True):

	# takes in some search folder, and passes each file by file to the mapper function
	# 
	# search term should specify the search depth (so it doesn't trawl through the sac_picks the SAC files for faster run)
	# 
	
	station_info = parse_station_info(station_file)
	
	file_list = [str(p) for p in Path(search_folder).rglob(rel_search_term)]

	for file in file_list:
		print(file)

		if not dry_run:
		
			csv_mapper(file, file, map_file, station_info) #ovewrite: should this be a flag?
		# just overwrite by default



def csv_mapper(input_csv, output_csv, map_file, station_info):

	df = pd.read_csv(input_csv)

	# i'm assuming these have event_start_time column

	df["event_start_time"] = pd.to_datetime(df["event_start_time"])


	station_map = create_map(map_file) # load in this function first so I can test locally
	# it's a small file anyway so re-parsing the file is not an expensive operation 

	# apply two masks (filter) for initial station + time frame

	# in the future there might be date filters with start/end date but it's not difficult
	# to just rewrite the mask to fit that
	# 
	
	for y_m in station_map:

		#print(y_m)
		y, m = y_m.split("_")
		y, m = int(y), int(m)

		for k, v in station_map[y_m].items():

			t_mask = df['event_start_time'].map(lambda x: x.year == y and x.month == m)
			s_mask = df['station'] == k
			#print(k,v)

			#print(df[t_mask][s_mask])
			for index, row in df[t_mask][s_mask].iterrows():
				df.at[index, "station"] = v

	# expensive rewriting operation
	for index, row in df.iterrows():
		try:
			df.at[index, "station_lat"] = station_info[row.station]["lat"]
			df.at[index, "station_lon"] = station_info[row.station]["lon"]
		except:
			try:
				drop_last = row.station[:-1]

				df.at[index, "station_lat"] = station_info[drop_last]["lat"]
				df.at[index, "station_lon"] = station_info[drop_last]["lon"]

			except:
				print(index, input_csv, "failed")



	df.to_csv(output_csv, index = False) # overwrite



	# how do i know that the mapping isn't done twice? 
	# should it be thought of as successive matrix transformations i.e.
	# will there be a lot more remappings to do in the future? which is possible right 
	# but probably not that many
	# 
	# 
	

	# want to check if the mapping is already applied 
	# i.e. IF the thing appears, change it, if not just move on



	# take in csv file as input

def multi_map(station_info,*input_files):
	pass

	# map each number to station

	# then whenever a query is made it will be a column vector multiplying by the map
	# this is so...
	# 
	# The problem with a matrix representation is that you need to 
	# collect all the possible station names and it has to maintained in a nice list somewhere
	# 

def create_map(input_file, ):
	# reads in a file, 
	# each line that starts with hashtag gives the year and month
	# each following line specifies, for that year and month, what station name changes to use

	# it should be a dictionary

	# what about like changes e.g. 1:2:3:4 but it can be reduced to 1:4
	# what about 1:2 next line 2:3 ? doesn't this mean that 1 should be mapped to 3?
	# hence the need for matrix multiplication?
	

	# there should be a way to combine maps

	station_map = {}

	_data = []

	with open(input_file, 'r') as f:
		for c, line in enumerate(f):
			if line[0] == "#":
				_year, _month = line[1:].strip().split(" ") # this would fail in an input error 
				y_m = "{}_{}".format(_year, _month) # year month	
				station_map[y_m] = {}

			else:
				try:

					k, v = [x.strip() for x in line.split(":")] # only two values (1:2)
					station_map[y_m][k] = v
				except:
					print("Might be EOF, not parsing: {}".format(line))

	return station_map



#mapper("notes/test_output.csv", "notes/test_output_test.csv", "4aug_station_remap.txt")

# read a file and create a dictionary? this is manual input obviously


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="To map all in a folder, use -sf (folder to recursively search in), -st (wildcard to look for .csv file in quotes), and -map_file (the txt file that maps stations for each month). Add dry_run flag to check file list. To do so for only one folder, use -i and -o to specify input and output files, and -map_file.")

	parser.add_argument('-i','--input')
	parser.add_argument('-o', '--output',)
	parser.add_argument('-map_file')
	parser.add_argument('-station_file', help = "tab separated file with station coordinates")

	parser.add_argument("-sf", help = "folder to search in")

	parser.add_argument("-st", help = "search term (encase in quotes so the shell doesn't expand it)")

	#parser.add_argument("-map_one", action = "store_true", help = "map for one csv file only")
	parser.add_argument("-csv", action = "store_true", help = "map for csv files only")
	parser.add_argument("-json", action = "store_true")
	parser.add_argument("-sac", action = "store_true", help = "map for sac files")

	parser.add_argument('-dry', action = "store_true", default = False)

	args = parser.parse_args()

	# if args.map_one:
	# 	csv_mapper(args.input, args.output, args.map_file)
	if args.csv:
		csv_remapping(args.sf, args.st, args.map_file, args.station_file, dry_run = args.dry)
	elif args.sac:
		sac_remapping(args.sf, args.st, args.map_file, args.station_file, args.output)

	elif args.json:
		json_remapping(args.input, args.map_file, args.station_file, args.output)

		# def json_remapping(json_file, map_file, station_info_file, output_file):

# def sac_remapping(search_folder, search_term, output_file, map_file, station_file):