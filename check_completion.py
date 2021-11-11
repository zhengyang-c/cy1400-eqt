import pandas as pd
import os
import subprocess
from pathlib import Path
import numpy as np
import datetime
import json



def summary_of_files():

	job_list = ["oct20_aa_fix1", "oct20_aa_fix2", "oct20_aa_fix3", "oct20_group_b","oct20_sub_0","oct20_sub_1", "oct20_sub_2", "oct20_sub_3", "oct20_sub_4","oct20_sub_5","oct20_sub_6","oct20_sub_7","oct20_sub_8",]
	summary_df = pd.DataFrame()

	c = 0

	for job in job_list:
		df = pd.read_csv(os.path.join("node_encode", job + ".csv"))

		for index, row in df.iterrows():

			# check hdf5 folder for sta.csv and sta.hdf5

			flags = {
				"sta": row.sta,

				"job_name":row.job_name,

				"sac_csv": os.path.exists(os.path.join(row.hdf5_folder, row.sta + ".csv")),

				"sac_hdf5": os.path.exists(os.path.join(row.hdf5_folder, row.sta + ".hdf5")),

				"prediction_made": os.path.exists(row.prediction_output_folder),

				"merge_filtered": os.path.exists(os.path.join(row.merge_output_folder, "merge_filtered.csv")),

				"merge_filtered_snr": os.path.exists(os.path.join(row.merge_output_folder, "merge_filtered_snr.csv")),

				"merge_filtered_snr_customfilter": os.path.exists(os.path.join(row.merge_output_folder, "merge_filtered_snr_customfilter.csv")),

				"n_lines": 0,

				"sac_pick_files":0,
			}

			if flags["merge_filtered_snr_customfilter"]:
				flags["n_lines"] = int(subprocess.check_output(["wc", "-l", os.path.join(row.merge_output_folder, "merge_filtered_snr_customfilter.csv")]).decode("utf8").split()[0]) - 1
				flags["sac_pick_files"] = len(os.listdir(os.path.join(row.merge_output_folder, "sac_picks")))

			checks = {
				"non_zero_files": flags["sac_csv"] and flags["sac_hdf5"],
				"all_plotted": flags["n_lines"] * 4 == flags["sac_pick_files"],
			}

			for k,v in flags.items():
				summary_df.at[c, k] = v

			for k,v in checks.items():
				summary_df.at[c, k] = v

	summary_df.to_csv("oct20_summary.csv", index = False)

def infer_actual_uptime():
	# read through all the generated .csv files and like parse them
	with open("station/all_stations.txt", "r") as f:
		station_list = [line.strip() for line in f if line.strip != ""]

	station_dict = {station: {} for station in station_list}

	for index, row in df.iterrows():
		# open the .csv file with aLL the trace names
		csv_path = os.path.join(row.hdf5_folder, row.sta + ".csv")
		if os.path.exists(csv_path):
			_df = pd.read_csv(csv_path)
			_df["hours"] = _df["start_time"].str.slice(stop = 13)

			unique_hours = _df["hours"].unique()

			for dayhr in unique_hours:
				day = datetime.datetime.strftime(datetime.datetime.strptime(dayhr[:10], "%Y-%m-%d"), "%j")
				hr = dayhr[-2:]

				if day not in station_dict[row.sta]:
					station_dict[row.sta][day] = [hr]
				else:
					station_dict[row.sta][day].append(hr)

	with open('08jul_aceh.json', 'w') as f:
		json.dump(station_dict,f)


		#print(station_dict)
	# then summarise findings

	df_list = []

	summary_df = pd.DataFrame()

	for sta in station_dict:

		_df = pd.DataFrame()
		# structure: {
		# day: []
		# day: []
		# }
		# 
		# want to find: total no. of fulldays, total duration (summed), which specific days are full, which specific days are partial
		fday_counter = 0
		hr_counter = 0
		c = 0
		for day in station_dict[sta]:
			#print(day)
			#print(station_dict[sta][day])
			_df.at[c, sta + "_days"] = day
			_df.at[c, sta + "_hrs"] = len(station_dict[sta][day])

			if len(station_dict[sta][day]) == 24:
				print("ASDFSFDSF")
				fday_counter += 1
			hr_counter += len(station_dict[sta][day])

			c += 1

		summary_df.at[sta, "full_days"] = fday_counter
		summary_df.at[sta, "total_days"] = hr_counter / 24

		df_list.append(_df)

	# write text summary

	big_df = pd.concat(df_list, axis = 1)

	big_df.to_csv("08jul_aceh_full_uptime.csv")
	summary_df.to_csv("08jul_aceh_summary_uptime.csv")
#infer_actual_uptime()

def verify_sac_files():

	error_df = pd.DataFrame()

	counter = 0
	for index, row in df.iterrows():	

		if not os.path.exists(row.merge_output_folder):
			continue

		plotted_sac_files = os.listdir(os.path.join(row.merge_output_folder, "sac_picks"))
		_df = pd.read_csv(os.path.join(row.merge_output_folder, "merge_filtered_snr_customfilter.csv"))
		_df.event_start_time = pd.to_datetime(_df.event_start_time)

		for _index, _row in _df.iterrows():

			event_id = "{}.{}".format(_row.station,datetime.datetime.strftime(_row.event_start_time,"%Y.%j.%H%M%S"))

			for i in ["EHE", "EHN", "EHZ"]:
				if event_id + "." + i + ".SAC" not in plotted_sac_files:

					error_df.at[counter, "job_name"] = row.job_name
					error_df.at[counter, "station"] = _row.sta
					error_df.at[counter, "event_id"] = event_id
					counter += 1

	error_df.to_csv("9jul_plottingerror.csv", index = False)



summary_of_files()