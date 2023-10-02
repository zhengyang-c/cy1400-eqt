import pandas as pd
import os
import argparse
import datetime
from pathlib import Path

def merging_df(df):

	COINCIDENCE_TIME_RANGE = 2

	
	make_group = True
	_tempgroup = []

	for index, row in df.iterrows():

		df.at[index, 'station'] = row.station.strip()

		curr_time = row["event_datetime"]

		if index == 0:

			start_time = curr_time

			_tempgroup.append(index)

		df.at[index, 'use_or_not'] = 0


		_dt = (curr_time - start_time).total_seconds()

		#print(_dt, curr_time, prev_time)

		if not index == 0:
			if _dt < COINCIDENCE_TIME_RANGE:				
				_tempgroup.append(index)

			else: # new event group, dump the previous temp_group
				for ti in _tempgroup:
					df.at[ti, 'agreement'] = len(_tempgroup)

				df.at[_tempgroup[len(_tempgroup)//2], 'use_or_not'] = 1 # keep the middle of the pack

				_tempgroup = [index]

				start_time = curr_time

		if index == len(df.index) - 1: # last

			for ti in _tempgroup:
				df.at[ti, 'agreement'] = len(_tempgroup)
			df.at[_tempgroup[len(_tempgroup)//2], 'use_or_not'] = 1 # keep the middle of the pack
			_tempgroup = [index]

		df.at[index, 'dt'] = _dt



	df_filtered = df[df['use_or_not'] == 1]

	for index, row in df_filtered.iterrows():
		df_filtered.at[index, 'datetime_str'] = "{}.{}".format(row.station, datetime.datetime.strftime(row.event_datetime, "%Y.%j.%H%M%S"))

	df_filtered = df_filtered[df_filtered.duplicated(subset = ['datetime_str']) == False]

	return df_filtered


def local_merger(input_csv, output_csv, keepPS = False, dt = 2):
	df = pd.read_csv(input_csv, index_col = 0)

	df = preprocess(df, keepPS = keepPS)

	df_filtered = merging_df(df)

	df_filtered.to_csv(output_csv, index = False)

def preprocess(df, keepPS = False):
	# if keepPS option is False, it will drop
	# by setting the flag, it will keep those with na for p_arrival_time and s_arrival_time
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
	parser = argparse.ArgumentParser()
	parser.add_argument('input_file', help = "input raw csv")
	parser.add_argument('output_file', help = "output merged csv")
	parser.add_argument('-dt', type = int, help = "time window from the first new pick", default = 2)
	parser.add_argument('-keepPS', action = "store_true", help = "flag to keep picks with only P xor S picks", default = False)


	args = parser.parse_args()
	local_merger(args.input_file, args.output_file, dt = args.dt, keepPS = args.keepPS)

# def main():
# 	job_list = []
# 	with open("joblist.txt", "r") as f:
# 		for line in f:
# 			job_list.append(line.strip().split(".")[0])

# 	for job_name in job_list:
# 		job_folder = os.path.join("/home/zchoong001/cy1400/cy1400-eqt/detections", job_name)
# 		try:
# 			station_list = [x for x in os.listdir(job_folder) if "_merged" not in x]

# 		except:
# 			continue

# 		print(job_name)

# 		for station in station_list:
# 			csv_parent_folder = os.path.join(job_folder, station)
# 			csv_files = [str(path) for path in Path(csv_parent_folder).rglob('*X_prediction_results.csv')]

# 			try:
# 				df = concat_df(csv_files)

# 				df = preprocess(df, keepPS = True)

# 				output_raw_csv = os.path.join(job_folder, station+"_merged", "keepPS_raw.csv")
# 				df.to_csv(output_raw_csv)

# 				df_filtered = merging_df(df)
# 				output_filtered_csv = os.path.join(job_folder, station+"_merged", "keepPS_filtered.csv")			
# 				df_filtered.to_csv(output_filtered_csv)
# 			except:
# 				pass
