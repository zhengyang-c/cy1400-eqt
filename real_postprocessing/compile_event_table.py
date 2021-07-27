import pandas as pd
from pathlib import Path
import shutil


def main():
	search_folder = "/home/zchoong001/cy1400/cy1400-eqt/detections/aceh_5jul"

	search_term = "*/*/merge_filtered_snr_customfilter.csv"

	file_list = [str(p) for p in Path(search_folder).rglob(search_term)]

	df_list = []

	#print(file_list, len(file_list))

	# want to concat all the csvs

	# also want to have each csv link to all the plots 

	# i think concat all the csv, add a column for the sac_picks folder, then
	# column for whether 3 corresponding .SAC files exist
	# and the wildcard check for that
	# 
	

	for f in file_list:
		_df = pd.read_csv(f)
		_df['local_file_root'] = "/".join(f.split("/")[:-1])

		df_list.append(_df)
	#df = pd.concat((pd.read_csv(f) for f in file_list), ignore_index = True)

	df = pd.concat(df_list, ignore_index = True)

	df.to_csv("7jul_compiled_customfilter.csv", index = False)

	#df = pd.read_csv("7jul_compiled_customfilter.csv")

	#for index, row in df.iterrows():








main()