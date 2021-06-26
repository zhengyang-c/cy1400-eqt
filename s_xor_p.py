import pandas as pd
import os
from pathlib import Path

import datetime

from merge_csv import concat_df, merging_df



# goal:

# basically run merge_csv.py but without throwing away all the P and S picks
# and then later skip the recompute SNR check + filter using agreement number
# 
# and then finally plot out the SAC files.... 
# 

def _preprocess(df):
	# drop any row with no p or s arrival pick!!
	#df.dropna(subset=['p_arrival_time', 's_arrival_time'], inplace = True)
	#
		
	df = df[(df['p_arrival_time'].isnull()) | (df['s_arrival_time'].isnull())]

	df['p_datetime'] = pd.to_datetime(df.p_arrival_time)
	df['event_datetime'] = pd.to_datetime(df.event_start_time)

	df.sort_values(by=['event_datetime'], inplace = True)

	df = df.reset_index(drop=True)

	return df


def find_sp(search_path, output_csv, multi = 20):

	file_list = [str(p) for p in Path(search_path).rglob("*.csv")]
	print(file_list)

	if len(file_list) == 0:
		print("s_xor_p: no files found, quitting")
		return

	df = concat_df(file_list)
	df = _preprocess(df)

	df = merging_df(df)

	df = df[df['agreement'] == multi]

	df.to_csv(output_csv, index = False)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	#parser.add_argument('source_folder', help = "sac_picks folder, from the eqt plotter")

	parser.add_argument('search_path', help = "folder to look for csv files")
	parser.add_argument('output_csv', help = "output csv with files to plot")	
	parser.add_argument('-multi', help = "no. of repeats that were performed", type = int, default = 20)
	

	args = parser.parse_args()
	find_sp(args.search_path, args.output_csv, args.multi)
