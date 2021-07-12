import pandas as pd
import os
import argparse

from pathlib import Path
# DESIRED ARGUMENTS:
# -collapse_2s
# -filterbyagreement
# input file
# output file

# input:
# csv folder
# detections/job_name/STA/multi_00/X_prediction
# 
# 
# output:
# merged_raw and merged_filtered csv file 
# 

from merge_csv import merging_df


def main():
	job_list = []
	with open("joblist.txt", "r") as f:
		for line in f:
			job_list.append(line.strip().split(".")[0])

	for job_name in job_list:
		job_folder = os.path.join("/home/zchoong001/cy1400/cy1400-eqt/detections", job_name)

		station_list = [x for x in os.listdir(job_folder) if "_merged" not in x]

		print(job_name)

		for station in station_list:
			csv_parent_folder = os.path.join(job_folder, station)
			csv_files = [str(path) for path in Path(csv_parent_folder).rglob('*X_prediction_results.csv')]

			df = concat_df(csv_files)

			df = preprocess(df, keepPS = True)

			output_raw_csv = os.path.join(job_folder, station+"_merged", "keepPS_raw.csv")
			df.to_csv(output_raw_csv)

			df_filtered = merging_df(df)
			output_filtered_csv = os.path.join(job_folder, station+"_merged", "keepPS_filtered.csv")			
			df_filtered.to_csv(output_filtered_csv)

		break

def preprocess(df, keepPS = False):
	# drop any row with no p or s arrival pick!!
	if not keepPS:
		df.dropna(subset=['p_arrival_time', 's_arrival_time'], inplace = True)

	df['p_datetime'] = pd.to_datetime(df.p_arrival_time)

	df['event_datetime'] = pd.to_datetime(df.event_start_time)

	#print(df['p_datetime'])
	df.sort_values(by=['event_datetime'], inplace = True)


	df = df.reset_index(drop=True)

	return df

def concat_df(list_of_csvs):
	df_objects = []
	
	for csv_file in list_of_csvs:
		_tempdf = pd.read_csv(csv_file)
		_relpath = '/'.join(csv_file.split("/")[-3:-1])

		_tempdf['relpath'] = _relpath

		df_objects.append(_tempdf)

	df = pd.concat(df_objects)
	return df

if __name__ == "__main__":
	main()