import pandas as pd
import os
import subprocess
from pathlib import Path

job_list = []
with open("joblist.txt", "r") as f:
	for line in f:
		job_list.append(line.strip().split(".")[0])

print(job_list)

df_list = []

for job_name in job_list:
	df = pd.read_csv(os.path.join("node_encode", job_name + ".csv"))
	df_list.append(df)

df = pd.concat(df_list, reset_index = True)

print(df)
# hdf5 dir:

# look for the node encode files

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

summary_df.to_csv("07july_summary.csv", index = False)

	# 


# check all hdf5 files and csv files generated

# check merge_filtered
# check merge_filtered_snr_customfilter, check length
# ls | wc -l the sac_picks folder and check the no. of files
# 

# node_encode folders
# id,sta,hdf5_folder,prediction_output_folder,merge_output_folder,start_day,end_day,multi,model_path,nodes,snr_threshold,station_json,job_name,write_hdf5,run_eqt,plot_eqt,merge_csv,filter_csv,recompute_snr,write_headers,sac_select
