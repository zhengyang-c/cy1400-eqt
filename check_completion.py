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

df = pd.concat(df_list)

print(df)

# hdf5 dir:

# look for the node encode files



# check all hdf5 files and csv files generated

# check merge_filtered
# check merge_filtered_snr_customfilter, check length
# ls | wc -l the sac_picks folder and check the no. of files
# 

# node_encode folders
# id,sta,hdf5_folder,prediction_output_folder,merge_output_folder,start_day,end_day,multi,model_path,nodes,snr_threshold,station_json,job_name,write_hdf5,run_eqt,plot_eqt,merge_csv,filter_csv,recompute_snr,write_headers,sac_select
