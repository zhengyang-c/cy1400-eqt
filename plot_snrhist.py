# input:
# load a folder, create a representation of the folder
# then load the csv, match each item to the csv
# then plot the distribution of SNR for all A, B, and Z picks
#  
# the snr is the p_snr and s_snr added together 

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import glob
import datetime
from pathlib import Path

import argparse
import subprocess


# load a csv file, return the dataframe filtered by the timestamps (event_datetime)
# csv_path should have all the metadata that is impt (p arrival, s arrival, snr)
def csv_filter(csv_path, list_of_timestamps):
	df = pd.read_csv(csv_path)

	df["event_ts"] = pd.to_datetime(df["event_start_time"])

	for index, row in df.iterrows():
		test_str = "{}.{}".format(row["station"], datetime.datetime.strftime(row["event_ts"], "%Y.%j.%H%M%S"))
		df.at[index, "keep"] = test_str in list_of_timestamps

		try:
			_manualindex = int(list_of_timestamps.index(test_str))
			df.at[index, "input_index"] = _manualindex
		except:
			df.at[index, "input_index"] = None

	df = df[df.keep == True]

	return df

def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

def datetime_to_str(x, dx):
	return datetime.datetime.strftime(x  + datetime.timedelta(seconds = dx), "%Y-%m-%d %H:%M:%S")




def plot(sac_folder, csv_file, output_file, plot_file):
	# get file list first

	#sac_folder = "imported_figures/21mar_default_merge/sac_picks"
	#csv_file = "imported_figures/21mar_default_merge/21mar_default_filtered.csv"
	
	#output_file = "plot_data/10apr_snr_default1month.csv"
	#plot_file = "plots/"



	grades = []
	filenames = []

	for p in Path(sac_folder).rglob("*png"):
		_p = str(p)

		_grade = _p.split("/")[-2]

		grades.append(_grade)

		filenames.append(".".join(_p.split("/")[-1].split(".")[:-1])) # get the filename without the extension

		# there is defn a better way to do this
	#print(filenames)
	df = csv_filter(csv_file, filenames)

	#print(df)

	#print(df.input_index)

	# collect SNR for A B Z

	for index, row in df.iterrows():
		df.at[index, "grade"] = grades[int(row["input_index"])]

	print(df.grade)

	write_data = []

	bins = np.arange(0, 100, 5)

	for _grade in ["A", "B", "Z"]:

		hist, _bins = np.histogram(df[df.grade == _grade].p_snr.values + df[df.grade == _grade].s_snr.values, bins = bins) 

		# normalised because.... should be absolute number tbh

		write_data.extend([hist, (_bins[1:] + _bins[:-1])/2]) # wow u can do this?

	outputdf = pd.DataFrame(np.column_stack(write_data), columns = ["A", "A_bins", "B", "B_bins", "Z", "Z_bins"])
	outputdf.to_csv(output_file, index = False)

	process = subprocess.Popen(["gnuplot", "-c", "plot_snrhist.gn", output_file, plot_file])


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description = "Given EQT picks grouped into A, B, and Z grades, plot distribution of SNR for each grade.")
	parser.add_argument('sac_folder', type = str, help = "sac_picks folder containing pngs")

	parser.add_argument('csv_file', type = str, help = "Filtered CSV file containing SNR info.")

	parser.add_argument('output_file', type = str, help = "plaintext file to store plotting data for gnuplot")

	parser.add_argument('plot_file', type = str, help = "pdf file for gnuplot output")

	args = parser.parse_args()

	plot(args.sac_folder, args.csv_file, args.output_file, args.plot_file)