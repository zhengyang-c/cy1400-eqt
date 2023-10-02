import datetime
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
			if _id not in data:
				data[_id] = []
			try:
				data[_id].append([float(row.LON), float(row.LAT), float(row.DEPTH)])
			except:
				print(row.LAT, row.LON, row.DEPTH)

	with open(output_json, "w") as f:
		json.dump(data, f, indent = 4)



def process_data(input_json, output_csv):
	from obspy.geodetics.base import gps2dist_azimuth

	with open(input_json, "r") as f:
		data = json.load(f)

	# for each ID, # if there's only 1 point, then skip, otherwise find the average

	df_list = []

	for id in data:
		if len(data[id]) == 1:
			continue

		print(id)

		# get average of lon and lat

		locs = pd.DataFrame.from_records(data[id], columns = ['lon', 'lat', 'dep'])

		mean_lon, mean_lat, mean_dep = locs['lon'].mean(), locs['lat'].mean(), locs['dep'].mean()

		for index, row in locs.iterrows():

			r, az, _ = gps2dist_azimuth(mean_lat, mean_lon, row.lat, row.lon)
			r /= 1000
			theta = (90 - az) * np.pi / 180

			locs.at[index, 'ID'] = id
			locs.at[index, 'r'] = r  # in km
			locs.at[index, 'dx'] = r * np.cos(theta)
			locs.at[index, 'dy'] = r * np.sin(theta)
			locs.at[index, 'dz'] = row.dep - mean_dep 
		df_list.append(locs)

	df = pd.concat(df_list)

	df.to_csv(output_csv, index = False)

def json_event_hist(input_json, title = ""):
	if title == "":
		title = get_title() 

	with open(input_json, "r") as f:
		data = json.load(f)

	counts = []

	for x in data:
		counts.append(len(data[x]))

	print(counts.count(1))

	plt.hist(counts, bins = np.arange(0, 100,2), )
	plt.yscale("log")
	plt.xlabel("No. of realisations per event")
	plt.ylabel("No. of events")

	plt.title("{} - hypoDD realisations per event".format(title))
	plt.savefig("{}_eventhist.png".format(title), dpi = 300)


def get_title():
	return datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d-%H%M%S")

def plot_data(input_csv, title = "", no_plot = False):
	# first generate a 2d histogram, plot colour map and draw contour lines

	# then try fitting to gaussian_kde using scipy

	if title == "":
		title = get_title()

	df = pd.read_csv(input_csv)


	scales = [100, 10, 1, 0.1]

	c = 0

	fig, axs = plt.subplots(2,2)
	for i in range(2):
		for j in range(2):
			df1 = df[(df['dx'] < scales[c]) & (df['dx'] > -scales[c]) & (df['dy'] < scales[c]) & (df['dy'] > -scales[c])]
			dx1 = df1['dx'].tolist()
			dy1 = df1['dy'].tolist()
			p1 = axs[i,j].hexbin(dx1, dy1, cmap = 'plasma', bins = 'log')

			axs[i,j].set_xlabel("Longitude scatter from mean [km]")
			axs[i,j].set_ylabel("Latitude scatter from mean [km]")
			axs[i,j].set_title("Range: {:.2f} km".format(scales[c]))

			fig.colorbar(p1, ax = axs[i,j])
			c += 1

	fig.set_size_inches(18.5, 10.5)
	plt.suptitle("hypoDD scatter (log scale)")

	if not no_plot:
		plt.savefig("{}_log.png".format(title), dpi = 150)
		plt.clf()
	else:
		plt.show()

	c = 0

	fig, axs = plt.subplots(2,2)
	for i in range(2):
		for j in range(2):
			df1 = df[(df['dx'] < scales[c]) & (df['dx'] > -scales[c]) & (df['dy'] < scales[c]) & (df['dy'] > -scales[c])]
			dx1 = df1['dx'].tolist()
			dy1 = df1['dy'].tolist()
			p1 = axs[i,j].hexbin(dx1, dy1, cmap = 'plasma', )

			axs[i,j].set_xlabel("Longitude scatter from mean [km]")
			axs[i,j].set_ylabel("Latitude scatter from mean [km]")
			axs[i,j].set_title("Range: {:.2f} km".format(scales[c]))

			fig.colorbar(p1, ax = axs[i,j])
			c += 1

	fig.set_size_inches(18.5, 10.5)
	plt.suptitle("hypoDD scatter (lin scale)")

	if not no_plot:
		plt.savefig("{}_lin.png".format(title), dpi = 150)
		plt.clf()
	else:
		plt.show()


	dz = df[(df['dz'] < 30) & (df['dz'] > -30)]['dz'].tolist()
	plt.hist(dz, bins = np.arange(-30,30, 1))
	plt.xlabel("Difference in depth from mean depth [km]")
	plt.ylabel("log No. of realisations")
	plt.yscale('log')
	if not no_plot:
		plt.savefig("{}_vertical.png".format(title), dpi = 150)
		plt.clf()
	else:
		plt.show()


	_dz = np.abs(df['dz'].tolist())
	zx = np.sort(_dz)
	zy = np.array(range(len(_dz)))/len(_dz)

	plt.plot(zx, zy, 'k-')
	plt.xlabel("Depth uncertainty [km]")
	plt.xscale("log")
	plt.xlim(0.0001, 10)
	plt.axhline(y=0.95, color='r', linestyle='-')
	plt.ylabel("Cumulative fraction")

	for _c, _x in enumerate(zy):
		if _x > 0.95:
			print("Z 95% interval is at: {}". format(zy[_c]))
			break

	plt.axvline(x = zx[_c], color = 'r', linestyle = '-')

	if not no_plot:
		plt.savefig("{}_vertical_confidence.png".format(title), dpi = 150)
		plt.clf()
	else:
		plt.show()

	# for dd_100, there are only 24 events that have only 1 realisation which is a very small percentage and that's ok

	# estimate confidence intervals

	all_r = df['r'].tolist()
	rx = np.sort(all_r)
	ry = np.array(range(len(all_r))) / len(all_r)


	plt.plot(rx, ry, 'k-')
	plt.xlabel("Distance from origin [km]")
	plt.xscale("log")
	plt.xlim(0.0001, 10)
	plt.axhline(y=0.95, color='r', linestyle='-')
	plt.ylabel("Cumulative fraction")

	for _c, _x in enumerate(ry):
		if _x > 0.95:
			print("Horizontal 95% interval is at: {}". format(rx[_c]))
			break

	plt.axvline(x = rx[_c], color = 'r', linestyle = '-')

	if not no_plot:
		plt.savefig("{}_horizontal_confidence.png".format(title), dpi = 150)
		plt.clf()
	else:
		plt.show()


if __name__ == "__main__":
	a = ap.ArgumentParser()
	a.add_argument("-f", "--input_folder", nargs = '+')
	a.add_argument("-i", "--input_file")
	a.add_argument("-oj", "--output_json")
	a.add_argument("-oc", "--output_csv")

	a.add_argument("-t", "--title", default = "")

	a.add_argument("-np", "--no_plot", action = "store_true", help = "Flag to display plot instead of saving it")

	a.add_argument("-pc", "--process_to_csv", action = "store_true")
	a.add_argument("-pp", "--process_csv_and_plot", action = "store_true")

	a.add_argument("-pjh", "--plot_json_hist", action = "store_true")


	args = a.parse_args()

	if args.process_to_csv:
		process_data(args.input_file, args.output_csv)
	elif args.process_csv_and_plot:
		plot_data(args.input_file, args.title, args.no_plot)
	elif args.plot_json_hist:
		json_event_hist(args.input_file, args.title)
	else:
		main(args.input_folder, output_json = args.output_json)