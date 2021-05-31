import pandas as pd
import json
import os
from pathlib import Path
import numpy as np
import argparse
import datetime


parser = argparse.ArgumentParser(description = "Using the merged csv file from merge_csv.py, throw away the events that were manually marked as noise (Z), using some comma separated file (look at the manual folder e.g. TA19.XX,Z and output to a new csv file.")

parser.add_argument('csv_input', type = str, help = "")

parser.add_argument('manual_picks', type = str, help = "Path to txt file of manual picks (this should not require any processing)")

parser.add_argument('csv_output', type = str, help = "Path to new csv file with all noise removed")

#parser.add_argument('-z', action='store', help = "Flag to indicate new noise string. Converted to lower case.")

args = parser.parse_args()

def main(csv_input, manual_picks, csv_output ):
	df = pd.read_csv(csv_input)

	noise_str = "z"

	noise_labels = []

	with open(manual_picks, "r") as f:
		for line in f:
			if line.strip().split(",")[1].lower() == "z" or line.strip().split(",")[1].lower() == "b":
				noise_labels.append(line.strip().split(",")[0])



	print(len(noise_labels))

	def mask(df, f):
		return df[f(df)]

	#df.mask(lambda x: )


	df['event_datetime'] = pd.to_datetime(df.event_datetime)

	for index, row in df.iterrows():

		df.at[index, 'event_keep'] = "{}.{}".format(row["station"], datetime.datetime.strftime(row["event_datetime"], "%Y.%j.%H%M%S")) not in noise_labels

	#print(df.event_keep)

	df = df[df.event_keep == True]

	df.to_csv(csv_output, index = False,)
	

#main("imported_figures/21mar_default_merge/21mar_default_filtered.csv", "manual/21mar_default_multi_repicked.txt", "imported_figures/21mar_default_merge/27mar_no_z.csv") # these are the A and B events
main(args.csv_input, args.manual_picks, args.csv_output)