import pandas as pd
import json
import os
from pathlib import Path
import numpy as np
import argparse
import datetime
import shutil
import matplotlib.pyplot as plt

from merge_csv import preprocess, merging_df

def load_from_grades(known_picks):

	graded_traces = []
	grades = []

	with open(known_picks, "r") as f:
		for line in f:
			_x = line.strip().split(",")
			graded_traces.append(_x[0])
			grades.append(_x[1])

	return (graded_traces, grades)


def main():
	sac_folder = "imported_figures/21mar_default_merge/sac_picks"

	txt_file = "manual/21mar_default_multi_repicked.txt" # this is assumed to be correct uhh
	csv_file = "imported_figures/21mar_default_merge/21mar_default_filtered.csv"
	plot_file = "plots/"
	# there are A, B, Z files inside

	# for now just assume the grade structure bc i cba

	# first load csv

	# then load all the files inside A/B/Z, associate each df row with a path

	# for all files in A/B, 

	SNR_THRESHOLD = 10

	sac_pathname = [str(path) for path in Path(sac_folder).rglob('*.png')]

	# should have a switch for recursive / non recursive probably but wow this is hard to manage i can see why
	# mousavi used an sql database 
	# 
	# # this should be a dataframe fml

	sac_tracename = [x.split("/")[-1].split(".png")[0] for x in sac_pathname]

	#df = pd.DataFrame(np.column_stack([sac_pathname, sac_tracename]), columns = ["pathname", "unknown_wf"])

	graded_traces, grades = load_from_grades(txt_file) # from manual pick file 

	df = pd.read_csv(csv_file)

	df.event_datetime = pd.to_datetime(df.event_datetime)

	for index, row in df.iterrows():
		df.at[index, 'tracename'] = "{}.{}".format(row.station, datetime.datetime.strftime(row.event_datetime, "%Y.%j.%H%M%S"))

	grade_df = pd.DataFrame(np.column_stack([graded_traces, grades]), columns = ["tracename", "grades"])

	merged = grade_df.merge(df[df.duplicated(subset = ['tracename']) == False], on = 'tracename', how = 'inner')

	#print(merged)

	print(merged[(merged.grades == "B") & (merged.p_snr > 10)])


	ax1 = merged[merged.grades == "A"].p_snr.plot.hist()

	ax2 = merged[merged.grades == "B"].p_snr.plot.hist()

	plt.figure()

	#ax1.plot()
	plt.show()







	# iterate through csv file, match grade and path which is pretty inefficient ngl it's n^2

def test_merge():
	df = pd.read_csv("imported_figures/21mar_default_merge/21mar_default_raw.csv")

	df = preprocess(df)

	df = merging_df(df)

	print(df)


main()