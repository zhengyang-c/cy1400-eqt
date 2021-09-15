import os
import pandas as pd
from pathlib import Path
import numpy as np
import datetime

def parse_times():

	CUT_OFF = 1

	timing_folder = "imported_figures/random10_150-180_timing"
	day_df = plot_all_uptime(
		"imported_figures/10jun_random10_150-180/10random_stationlist.txt", 
		start_date = "2020.150", 
		end_date = "2020.180", 
		all_csv_path = "imported_figures/10jun_random10_150-180/20jun_random10_1month.csv")

	# timing data:

	file_list = ([str(p) for p in Path(timing_folder).glob("*.txt")])

	df_list = []
	for file in file_list:
		df = pd.read_csv(file, header = None)
		df.columns = ['script', 'start', 'time']
		df["station"] = file.split("/")[-1].split(".")[0]
		

		df = df[df.time > CUT_OFF]

		df_list.append(df)

	df = pd.concat(df_list)

	

	df = pd.merge(df, day_df, on = "station")
	#print(df)

	# get average sac_hdf time per day

	df['time_per_day'] = df['time'] / df['up_days']
	#plt.figure()

	#df[["script"] == "run_eqt.py"].plot.scatter(x = '', y = '')
	
	# sth = (df[df["script"] == "sac_to_hdf5"].time_per_day)

	# run = (df[df["script"] == "run_eqt.py"].time_per_day)

	# rec = (df[df["script"] == "recompute_snr"].time_per_day)

	# plt = (df[df["script"] == "plot_eqt"].time_per_day)

	# print(list(map(np.mean, [sth, run, rec, plt])))
	# print(list(map(np.std, [sth, run, rec, plt])))
	# 




	# get average run_eqt time per day
	# get time of postprocessing 
	# plot incrase in run eqt per time
	# 
def plot_all_uptime(selector_file, start_date, end_date, all_csv_path = "station/all_aceh_sac.csv"):

	# selector file: list of stations

	with open(selector_file, 'r') as f:
		station_list = f.read().split("\n")

	station_list = list(filter(lambda x: x != "", station_list))

	n_stations = len(station_list)

	_parse_char = "j"

	start_date = datetime.datetime.strptime(start_date, "%Y.%{}".format(_parse_char))
	end_date = datetime.datetime.strptime(end_date, "%Y.%{}".format(_parse_char))

	n_days = (end_date - start_date).days + 1
	
	image = np.zeros((n_stations, n_days))


	df = pd.read_csv(all_csv_path)
	
	if not 'dt' in df.columns:
		
		for index, row in df.iterrows():
			df.at[index, 'dt'] = datetime.datetime.strptime("{}.{}".format(row['year'], row['jday']), "%Y.%j")

	else:
		df["dt"] = pd.to_datetime(df["dt"])

	for index, row in df.iterrows():

		if row.station in station_list and row['dt'] >= start_date and row['dt'] <= end_date:
			station_index = station_list.index(row.station)
			day_index = (row["dt"] - start_date).days

			image[station_index, day_index] = 1


	day_df = pd.DataFrame()
	for i in range(n_stations):
		day_df.at[i, "station"] = station_list[i]
		day_df.at[i, "up_days"] = np.sum(image[i, :])
		day_df.at[i, "total_days"] = n_days

	return day_df

	

parse_times()

