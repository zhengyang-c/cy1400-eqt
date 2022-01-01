import os
import numpy as np
import pandas as pd
import argparse
from pathlib import Path
import datetime
import matplotlib.pyplot as plt

def runtime(log_folder, output_csv):

	"""
	add like multiple folder inputs via command line args, then join the outputs in the same dataframe
	
	
	"""

	# look in two places separately. first: look at raw log to get time, run parameters, no. of events
	# next, look at the output folder to get the actual events in case you want to compare... stuff.. which is kind of pointless 
	# because the `accuracy' depends on the grid spacing which is discreteised so 

	# log_folder = "imported_figures/gridtest_1227"

	folder_list = [str(p) for p in Path(log_folder).glob("*")]

	df = pd.DataFrame()

	for f in (folder_list):

		_id = f.split("/")[-1]
		_script_path = os.path.join(f, "run.sh")
		_log_path = [str(p) for p in Path(f).glob("*.txt")][0]

		with open(_script_path, "r") as _f:
			contents = _f.read()
			_contents = [x.strip() for x in contents.split(" ") if '-R' in x][0]
			print(_contents)
			_data = _contents[2:].split("/")

			df.at[_id, "horizontal_search_deg"] = float(_data[0])
			df.at[_id, "vertical_search_km"] = float(_data[1])
			df.at[_id, "horizontal_cell_deg"] = float(_data[2])
			df.at[_id, "vertical_cell_km"] = float(_data[3])



		with open(_log_path, "r") as _f:
			contents = _f.read()

			try:
				timing = [x.split("\t")[1] for x in contents.split("\n") if 'real' in x][0]

				df.at[_id, "runtime"] = (int(timing.split("m")[0]) * 60 + float(timing.split("m")[1][:-1]))
				df.at[_id, "ln_runtime"] = np.log(int(timing.split("m")[0]) * 60 + float(timing.split("m")[1][:-1]))
				n_events = [int(x.split(":")[1].strip()) for x in contents.split("\n") if 'second selection' in x][0]
				df.at[_id, "n_events"] = n_events

			except:
				print(contents)

	df["ln_n_est_cells"] = np.log((df["horizontal_search_deg"] / df["horizontal_cell_deg"]) + 1)**2 * ((df["vertical_search_km"] / df["vertical_cell_km"]) + 1)

	print(df)

	df.to_csv(output_csv, index = False)


	# folder_list = [str(p) for p in Path(output_folder).glob('*')]
	# print(folder_list)

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument('log_folder')
	ap.add_argument('output_csv')
	args = ap.parse_args()
	runtime(args.log_folder, args.output_csv)