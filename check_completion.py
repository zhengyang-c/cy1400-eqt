import pandas as pd
import os
import subprocess
from pathlib import Path
import numpy as np
import datetime


job_list = []
with open("joblist.txt", "r") as f:
	for line in f:
		job_list.append(line.strip().split(".")[0])

print(job_list)

df_list = []

for job_name in job_list:
	df = pd.read_csv(os.path.join("node_encode", job_name + ".csv"))
	df_list.append(df)

df = pd.concat(df_list, ignore_index = True)

print(df)
# hdf5 dir:

# look for the node encode files
def summary_of_files():
	summary_df = pd.DataFrame()

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
			summary_df.at[index, k] = v

		for k,v in checks.items():
			summary_df.at[index, k] = v

	summary_df.to_csv("07july_summary_3.csv", index = False)

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
					station_dict[row.sta] = {day: [hr]}
				else:
					station_dict[row.sta][day].append(hr)

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

	big_df = pd.concat(df_list)

	big_df.to_csv("08jul_aceh_full_uptime.csv")
	summary_df.to_csv("08jul_aceh_summary_uptime.csv")


	# for each station, find the number of full days, number of partial days (hrs / 24)





infer_actual_uptime()

# check all hdf5 files and csv files generated

# check merge_filtered
# check merge_filtered_snr_customfilter, check length
# ls | wc -l the sac_picks folder and check the no. of files
# 

# node_encode folders
# id,sta,hdf5_folder,prediction_output_folder,merge_output_folder,start_day,end_day,multi,model_path,nodes,snr_threshold,station_json,job_name,write_hdf5,run_eqt,plot_eqt,merge_csv,filter_csv,recompute_snr,write_headers,sac_select