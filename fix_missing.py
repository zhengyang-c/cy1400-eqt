import pandas as pd
from pathlib import Path
import os
import datetime
import filecmp


# first find all used sac files and exclude them



def select_files(selector_file, start_date, end_date, y_jul = True, y_mon = False, all_csv_path = "station/all_aceh_sac.csv", output_file = ""):

	
	# start_date format = e.g. 2020_03 for month

	if y_jul and y_mon:
		print("invalid options")
		return 0

	if y_jul:
		_parse_char = "j"
	elif y_mon:
		_parse_char = "m"


	_startdate, _enddate = start_date, end_date


	start_date = datetime.datetime.strptime(start_date, "%Y.%{}".format(_parse_char))
	end_date = datetime.datetime.strptime(end_date, "%Y.%{}".format(_parse_char))

	df = pd.read_csv(all_csv_path)

	# kinda inefficient bc 10^5 rows but it's fine bc it won't be used very often

	for index, row in df.iterrows():
		df.at[index, 'dt'] = datetime.datetime.strptime("{}.{}".format(row.year, row.jday), "%Y.%j")


		for _cha in ["EHE", "EHN", "EHZ"]:
			if _cha in row.filepath:
				df.at[index,'channel'] = _cha


	#station_list = []

	with open(selector_file, 'r') as f:
		station_list = f.read().split("\n")

	station_list = list(filter(lambda x: x != "", station_list))

	print(station_list)

	_df = df[df["station"].isin(station_list) & (df["fullday"]) & (df["dt"] >= start_date) & (df["dt"] <= end_date)]

	m_df = df[df["station"].isin(station_list) & (df["fullday"] == 0) & (df["dt"] >= start_date) & (df["dt"] <= end_date)]

	print(m_df)

	m_df.to_csv("missing_sac_5jul.csv", index = False)


select_files("station/all_stations.txt", "2020.001", "2020.366")


def remove_duplicate():

	df = pd.read_csv("missing_sac_5jul.csv")

	df = df[~df["start_time"].str.contains("-1", na = False)]

	print(df)

def check_duplicate():

	df = pd.read_csv("missing_sac_5jul.csv")

	df = df[df["start_time"].str.contains("-1", na = False)]

	for index, row in df.iterrows():

		original = row.filepath[:-6] + ".SAC"
		to_test = row.filepath

		if not (filecmp.cmp(original, to_test)):
			print(original, "duplicate not the same")


	# write them to a file

	# make a bash script that outputs to a file

	# call the bash script 

	# about 200 duplicates which... are probably duplicates... with the -1 at the back? 

check_duplicate()