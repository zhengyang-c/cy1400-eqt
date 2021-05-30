# goals:

# prepre sac --> hdf5 file, estimating how much space it'll take
# and allowing for station selection / time frame selection
# 
# 
# first choose station, then choose time frame
# 
# want to have tools to show uptime for the station


# which suggests having different scripts or just like

# multi_station -up -o save.png -sta TA01-TA19.txt
# to show graphically or sth -st

# multi_station -make -s input.txt -o save_folder

# multi_station -choose sac_folders -o input.txt



import argparse
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
import os


#get_all_files("/home/eos_data/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/")


def get_all_files(sac_folder):
	# look inside /tgo/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/ 
	# for .SAC files
	# 
	
	# how does SAC to miniSEED conversion work again
	# i think have a pandas dataframe, find the station. 
	# you want the path information for each of them
	
	folder_list = ["Deployed-2019-12-MSEED",
	"Deployed-2020-01-MSEED",
	"Deployed-2020-02-MSEED",
	"Deployed-2020-03-MSEED",
	"Deployed-2020-04-MSEED",
	"Deployed-2020-05-MSEED",
	"Deployed-2020-07-MSEED",]

	all_files = []

	for _f in folder_list:
		all_files.extend([str(p) for p in Path(os.path.join(sac_folder, _f)).rglob("*SAC")])


	#print(all_files)

	df = pd.DataFrame()

	df["filepath"] = all_files

	#print(df)

	for index, row in df.iterrows():
		_sta = row.filepath.split("/")[-2] # second last entry should be the station name

		# the sac files have their channel in front and not behind so... 

		# check if all 3 channels are available too?

		_file = row.filepath.split("/")[-1]

		_year = _file.split(".")[5]
		_jday = _file.split(".")[6]

		_datetime = datetime.datetime.strptime("{}.{}".format(_year,_jday), "%Y.%j")

		df.at[index, 'station'] = _sta
		df.at[index, 'year'] = (_year)
		df.at[index, 'jday'] = (_jday)
		df.at[index, 'start_time'] = _file.split(".")[7]

		df.at[index, 'fullday'] = (_file.split(".")[7] == "000000")

		# fullday?

	df.to_csv("station/all_aceh_sac.csv", index = False)



	# get station, check full day, get year, julian day, month

	# then print csv file


# since the uptime information is likely to be static, might as well generate the .csv uptimes once and then load from there
# 10^5 files monkas
# 


def plot_uptime():
	pass


def select_files(selector_file = "station/TA19.txt", start_date = "2020_085", end_date = "2020_108", y_jul = True, y_mon = False, all_csv_path = "station/all_aceh_sac.csv"):
	
	# start_date format = e.g. 2020_03 for month

	if y_jul and y_mon:
		print("invalid options")
		return 0

	if y_jul:
		_parse_char = "j"
	elif y_mon:
		_parse_char = "m"

	start_date = datetime.datetime.strptime(start_date, "%Y_%{}".format(_parse_char))
	end_date = datetime.datetime.strptime(end_date, "%Y_%{}".format(_parse_char))

	df = pd.read_csv(all_csv_path)

	# kinda inefficient bc 10^5 rows but it's fine bc it won't be used very often

	for index, row in df.iterrows():
		df.at[index, 'dt'] = datetime.datetime.strptime("{}_{}".format(row.year, row.jday), "%Y_%j")


	#station_list = []

	with open(selector_file, 'r') as f:
		station_list = f.read().split("\n")

	station_list = list(filter(lambda x: x != "", station_list))

	print(station_list)

	print(df[df["station"].isin(station_list) & (df["fullday"]) & (df["dt"] >= start_date) & (df["dt"] <= end_date)])




	# generate a file list to feed into sac_to_hdf5 script

	# attempt to look for complete files, all 3 C


select_files()
	# list of stations in some file,
	# or pass via argument
	# 
	# 
	# then start day and end day
	# and then try to find all the sac files and then save the path somewhere ? this should feed directly to sac_Tohdf5