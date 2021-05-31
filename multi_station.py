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


def get_all_files(sac_folder, output_file):
	# look inside /tgo/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/ 
	# for .SAC files
	# 
	
	# how does SAC to miniSEED conversion work again
	# i think have a pandas dataframe, find the station. 
	# you want the path information for each of them
	
	folder_list = ["Deployed-2019-12-MSEED", # this is actually hardcoded
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
	# "station/all_aceh_sac.csv"
	df.to_csv(output_file, index = False)

	sac_files = []
	#_df = pd.load_csv(csv_paths)

	for _sta in _df.station.unique():
		print(_sta)

		_paths = []

		for index, row in _df[_df["station"] == _sta].iterrows():
			_paths.append(_df.loc[index, "filepath"])

		sac_files.append({"paths": _paths, "sta": _sta})

	sac_files.sort()

	print(sac_files)


	# get station, check full day, get year, julian day, month

	# then print csv file


# since the uptime information is likely to be static, might as well generate the .csv uptimes once and then load from there
# 10^5 files monkas
# 


def plot_uptime():
	pass


def select_files(selector_file = "station/TA19.txt", start_date = "2020_085", end_date = "2020_108", y_jul = True, y_mon = False, all_csv_path = "station/all_aceh_sac.csv", output_file = "station/TA19_2020_085-108"):
	
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

	_df = df[df["station"].isin(station_list) & (df["fullday"]) & (df["dt"] >= start_date) & (df["dt"] <= end_date)]

	_df.sort_values("jday", inplace = True)

	_df.to_csv("station/test.csv")

	# want to check if it's complete, whether it's all fulldays, if any gaps

	# which should also show me the missing files

	n_days = (end_date - start_date).days + 1
	n_stations = len(station_list)

	image = np.zeros((n_stations, n_days))

	expected_files = n_days * 3

	if len(_df.index) < expected_files:
		print("some missing, can report on the no. of missing + flag to continue")

		print("expected: ", expected_files, "actual: ", len(_df.index))

		# there's no point giving this information bc i can't magic the data from thin air
		# but gd to let the user know right hm missing
		# 
		# i.e. provide the uptime plot 
	elif len(_df.index) > expected_files:
		print("more files than expected which is odd, have to filter so that it's only 3")

		print("This shouldn't happen")
	else:
		print("all files present, no issues :)")


	if output_file:
		_df.to_csv(output_file, index = False)






	# check: all channels, all days, full day


	# all channel


	# generate a file list to feed into sac_to_hdf5 script

	# attempt to look for complete files, all 3 C

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = "utils for preparing multistation hdf5 files, running eqt (future) and plotting sac files")

	parser.add_argument("--get", help = "name of parent SAC folder. get all SAC files available in a data folder, print to csv", default = None)
	parser.add_argument("-i", "--input", help = "input file")
	parser.add_argument("-o", "--output", help = "output file")


	parser.add_argument("-sf", "--selector", help = "txt file with linebreak separated station names, specifying stations of interest")


	parser.add_argument("-s", "--startdate", help = "underscore separated year with julian day e.g. 2020_085 for start date (inclusive)")
	parser.add_argument("-e", "--enddate", help = "underscore separated year with julian day e.g. 2020_108 for enddate (inclusive)")
	parser.add_argument("-m", "--month", help = "flag to use month. default is Julian day. e.g. 2020_03 to represent March", action = "store_true", default = False)
	parser.add_argument("-j", "--julian", help = "default is True, to use Julian day to specify start and end date", action = "store_true", default = True)

	args = parser.parse_args()

	if args.selector:
		select_files(args.selector, args.startdate, args.enddate, args.julian, args.month, args.input, args.output)
	elif args.get:
		get_all_files(args.get, args.output)


	# list of stations in some file,
	# or pass via argument
	# def select_files(selector_file = "station/TA19.txt", start_date = "2020_085", end_date = "2020_108", y_jul = True, y_mon = False, all_csv_path = "station/all_aceh_sac.csv", output_file = "station/TA19_2020_085-108"):
	# 
	# then start day and end day
	# and then try to find all the sac files and then save the path somewhere ? this should feed directly to sac_Tohdf5
	# 