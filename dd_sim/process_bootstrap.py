import json
import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import argparse as ap

def make_reloc_catalog(input_file, ):

	df = pd.DataFrame()

	# ID, LAT, LON, DEPTH, X, Y , Z (relative to centroid), EX, EY , EZ (ignore, using LSQR), YR, MO, DY, HR, MI, SC, MAG( 0), nccp, nccs (cross corr), NCTP, NCTS (catalogue p and s), RCC, RCT (residuals for cross corr and catalogue ), CID cluster id

	labels = ["ID", "LAT", "LON", "DEPTH", "X", "Y", "Z", "EX", "EY", "EZ", "YR", "MO", "DY", "HR", "MI","SC", "MAG", "NCCP", "NCCS", "NCTP", "NCTS", "RCC", "RCT", "CID"]

	with open(input_file, 'r') as f:
		for c, line in enumerate(f):
			if not len(line): continue

			#print(line)

			_data = [x.strip() for x in line.split(" ") if x != ""]

			#print(_data)

			for i in range(len(_data)):
				#print(_data[i])
				#print(labels[i])
				df.at[c, labels[i]] = _data[i]

	return df

def main(input_folders, output_json = ""):

	"""
	first collate the locations, for every event in a dictionary
	i.e. each event is a dictionary with a list of locations

	normalise the location using the mean:
	convert the lat lon into cartesian coordinates centred at the mean
	so it's in units of km i.e. want to define error ellipse in units of km

	how do you take the mean of lat lon (just average?)

	want to plot a 2d heat map (?) obtain a density distribution estimation based on locations

	want to plot vertical distributions as a histogram

	want to try to fit error ellipsoids (?) but not sure if that requires any coordinate transformation

	"""

	# input_folder = "dd_100"

	all_files = []

	for input_folder in input_folders:

		all_files.extend([str(p) for p in Path(input_folder).rglob("*.reloc")])

	data = {}

	for f in all_files:
		print(f)
		_df = make_reloc_catalog(f)
		for index, row in _df.iterrows():
			_id = str(row.ID).zfill(6)
			if row.ID not in data:
				data[_id] = []

			try:
				data[_id].append([float(row.LON), float(row.LAT), float(row.DEPTH)])
			except:
				print(row.LAT, row.LON, row.DEPTH)
				pass

	with open(output_json, "w") as f:
		json.dump(data, f, indent = 4)

	

	# open the .reloc file

	# use the same parser as postprocessing


if __name__ == "__main__":
	a = ap.ArgumentParser()
	a.add_argument("-i", "--input_folder", nargs = '+')
	a.add_argument("-oj", "--output_json")
	a.add_argument("-oc", "--output_csv")

	args = a.parse_args()

	main(args.input_folder, output_json = args.output_json)