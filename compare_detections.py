"""
given some known files/ timestamps with grades (A/B/Z), 
evaluate a different model's output by comparing these timestamps 

"""

import os
import glob
import argparse
import numpy as np

import math
import random

import datetime
import pandas as pd

from pathlib import Path

import shutil

def load_from_grades(known_picks):

	graded_traces = []
	grades = []

	with open(known_picks, "r") as f:
		for line in f:
			_x = line.strip().split(",")
			graded_traces.append(_x[0])
			grades.append(_x[1])

	return (graded_traces, grades)

def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

def compare_grades(graded_traces, grades, df):

	THRESHOLD = 2
	
	graded_traces_dt = [datetime.datetime.strptime(".".join(x.split(".")[1:]), "%Y.%j.%H%M%S") for x in graded_traces]

	for index, row in df.iterrows():
		_timestamp = ".".join(row["unknown_wf"].split(".")[1:])

		df.at[index, 'datetime'] = datetime.datetime.strptime(_timestamp, "%Y.%j.%H%M%S")


		if row["unknown_wf"] in graded_traces:
			_index = graded_traces.index(row["unknown_wf"])
			df.at[index, 'match'] = 1
			df.at[index, 'grade'] = grades[_index]
		else:
			deltas = [np.abs((x - df.at[index, 'datetime']).total_seconds()) for x in graded_traces_dt]
			min_value = min(deltas)
			# 
			# computationally inefficient FYI it takes so long hahaa 
			# 
			if min_value < THRESHOLD:
				min_index = deltas.index(min_value)
				df.at[index, 'match'] = 1
				df.at[index, 'grade'] = grades[min_index]

			else:
				df.at[index, 'match'] = 0 # there is a better way to do this

	return df


def main(known_picks, unknown_sac_folder, dry_run = False):

	sac_pathname = [str(path) for path in Path(unknown_sac_folder).glob('*.png')]

	# should have a switch for recursive / non recursive probably but wow this is hard to manage i can see why
	# mousavi used an sql database 
	# 
	# # this should be a dataframe fml

	sac_tracename = [x.split("/")[-1].split(".png")[0] for x in sac_pathname]

	df = pd.DataFrame(np.column_stack([sac_pathname, sac_tracename]), columns = ["pathname", "unknown_wf"])
	graded_traces, grades = load_from_grades(known_picks) # from manual pick file 
	df = compare_grades(graded_traces, grades, df)

	# collate grades 
	
	print(len(df[df.grade == "A"]))
	print(len(df[df.grade == "B"]))
	print(len(df[df.grade == "Z"]))
	print(len(df[df.match == 0]))

	# create folders and move sac traces

	for g in ["A", "B", "Z"]:
		dest_folder = os.path.join(unknown_sac_folder, g)
		if not os.path.exists(dest_folder):
			os.makedirs(dest_folder)


	for index, row in df[df.match != 0].iterrows():
		start_path = row["pathname"][:-4] + "*" # bit hacky to cut off the png
		#print(start_path)
		end_path = os.path.join(unknown_sac_folder, row["grade"])


		for file in glob.glob(start_path):
			if not dry_run:
				shutil.move(file, end_path)
			else:
				print("moving {} ---> {}".format(file, end_path))



if __name__ == "__main__":
	
	# parser = argparse.ArgumentParser()
	# parser.add_argument('csv_file', type = str, help = "path to csv file. from EqT, this is X_prediction_results.csv")

	# parser.add_argument('manual_file', type = str, help = "Text file with [trace name],[manual grading]")

	# parser.add_argument('output_file', type = str, help = "Output csv file to plot in gnuplot")

	# args = parser.parse_args()

	main("manual/21mar_default_multi_repicked.txt", "imported_figures/27mar_wholemonth_aceh1e-6frozen/TA19_outputs/sac_picks", dry_run = False)

