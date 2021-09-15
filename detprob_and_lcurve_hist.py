# read csv and plot histogram of probabilities, or just
# generate a file for gnuplot to use?
# so i have to calculate bin centres

# input file: the .csv file for which to plot probabilities
# txt_file: manual picks
# output_file: plot file to feed into gnuplot 
# 
# also generates another csv file for the l curve (tells us what detection threshold to use??)
# 
# TODO:
# command line pass arguments into the two gnuplot files so it's more automated and less aids to use
# 


import argparse

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	parser.add_argument('csv_file', type = str, help = "path to csv file. from EqT, this is X_prediction_results.csv")

	parser.add_argument('manual_file', type = str, help = "Text file with [trace name],[manual grading]")

	parser.add_argument('output_root', type = str, help = "Output file root to produce two csv files")

	parser.add_argument('plot_root', type = str, help = "Path root to the plots e.g. plots/26apr_detail")

	args = parser.parse_args()

import matplotlib
matplotlib.use('TkAgg')
import pandas as pd
import numpy as np
import os
import json
import subprocess
import sys
import datetime

import matplotlib.pyplot as plt

def csv_filter(csv_path, list_of_timestamps):
	# if the event is in the manual grading list, keep it i.e. we only want the intersection
	# of the grades and the data in the EQT output csv file
	# 

	df = pd.read_csv(csv_path)

	df["event_ts"] = pd.to_datetime(df["event_start_time"])


	for index, row in df.iterrows():
		df.at[index, "keep"] = "{}.{}".format(row["station"], datetime.datetime.strftime(row["event_ts"], "%Y.%j.%H%M%S")) in list_of_timestamps
		df.at[index, "ts_str"] = datetime.datetime.strftime(row["event_ts"], "%Y.%j.%H%M%S")

	df = df[df.keep == True]

	return df

def match_gradings(df, grade_tracename, grades):
	"""
	Given a txt file in manual (giving the grades for each trace as identified in its file name),
	and a data file, match each grade to the waveform in the pd df
	
	:param      df:               filtered pandas dataframe
	:type       df:               { type_description }
	:param      grade_tracename:  A list of grades and tracenames, taken from the manual folder
	:type       grade_tracename:  { type_description }
	:param      grades:           The grades
	:type       grades:           { type_description }
	"""

	for c, tn in enumerate(grade_tracename):
		tn = ".".join(tn.split(".")[1:])
		_dfindex = df[df.ts_str == tn].index.values[0]

		df.at[_dfindex, "grade"] = grades[c].upper()

	return df


def centre_bin(bins):
	return (bins[1:] + bins[:-1])/2

def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

def plot(csv_file, manual_file, output_root, plot_root):

	#df = csv_filter(csv_file, )

	manual_gradings = []
	manual_files = []
	with open(manual_file, "r") as f:
		for line in f:
			try:
				manual_files.append((line.split(",")[0].strip()))
				manual_gradings.append((line.split(",")[1].strip()))
			except:
				pass
	

	df = csv_filter(csv_file, manual_files	)
	
	df = match_gradings(df, manual_files, manual_gradings)

	# want to plot:
	# what is the overall histogram
	# what is the histogram for A signals
	# # what is the histogram for B signals
	# # what is the histogram for Z signals
	# 
	
	# overall:

	#print(list(df[df.grade == "A"].detection_probability))

	# output to a gnuplot format


	bins = np.arange(0,1.1,0.1)

	
	A_hist, _ = np.histogram(df[df.grade == "A"].detection_probability, bins = bins)
	B_hist, _ = np.histogram(df[df.grade == "B"].detection_probability, bins = bins)
	Z_hist, _ = np.histogram(df[df.grade == "Z"].detection_probability, bins = bins)


	# want to find: precision as a function of detection probability threshold

	integral_bins = np.arange(0,1, 0.05)
	integral_precision = []
	integral_good = []

	for _threshold in integral_bins:
		#good = len(df[(df.grade == "A") |  (df.grade == "B")])
		good_count = 0
		total_count = 0
		for index, row in df.iterrows():
			if row["detection_probability"] >= _threshold:
				total_count += 1
				if row["grade"] == "A" or row["grade"] == "B":
					good_count += 1
		try:
			integral_precision.append(good_count / total_count)
		except:
			integral_precision.append(0)

		integral_good.append(good_count)



	lcurve_root = output_root + "_lcurve.csv"
	lcurve_plot_root = plot_root + "_lcurve.pdf"
	l_curve = pd.DataFrame(np.column_stack([integral_bins, integral_precision, integral_good]), columns = ["bin", "precision", "good"])
	l_curve.to_csv(lcurve_root, index = False)

	process = subprocess.Popen(["gnuplot", "-c", "plot_lcurve_hist.gn", lcurve_root, lcurve_plot_root])

	# gnuplot -e "plot_file=\'{}\';output_file=\'{}\'" plot_lcurve_hist.gn



	output_df = pd.DataFrame(np.column_stack([centre_bin(bins), A_hist, B_hist, Z_hist]), columns = ["bin_centre", "A", "B","Z"])

	detprob_root = output_root + "_detprob.csv"
	detprob_plot_root = plot_root + "_detprob.pdf"

	output_df.to_csv(detprob_root, index = False)

	process = subprocess.Popen(["gnuplot", "-c", "plot_detprob_hist.gn", detprob_root, detprob_plot_root])
	# plot in gnuplot:

	


	"""p = []
	for i in _p:
		if i != i:
			p.append(0) 
		else:
			p.append(i)

	#print(p)

	event_times = list(df["event_start_time"])


	#print(event_times)
	def plotter(pr_list):

		z = list(zip(event_times, pr_list))
		z = sorted(z, key = lambda x: x[1], reverse = True)

		hist, bin_edges = np.histogram(pr_list, bins = np.linspace(0, 1, 11))

		#print(hist, bin_edges)

		bin_centres = np.array([bin_edges[i] + bin_edges[i + 1] for i in range(len(bin_edges) - 1)])/2

		integral = [sum(hist[0:i]) for i in range(1, 11)]

		#integral.insert(0, 0)

		integral = np.array(integral)/sum(hist)



		times, ps = list(zip(*z)) # what is this

		times, ps = list(times), list(ps)

		new_times = []
		for _thing in times:
			try:
				new_times.append(datetime.strptime(_thing, "%Y-%m-%d %H:%M:%S"))
			except:
				new_times.append(datetime.strptime(_thing, "%Y-%m-%d %H:%M:%S.%f"))
		
		with open("manual/28feb_review_withnoise.txt", "w") as f:
			for thing in [datetime.strftime(x, "%H%M%S") for x in new_times]:
				pass
				#f.write("{}\n".format(thing))

		with open("manual/28feb_review_withnoise_check.txt", "w") as f:
			for c, thing in enumerate([datetime.strftime(x, "%H%M%S") for x in new_times]):
				pass
				#f.write("{}\t{}\n".format(thing, ps[c]))
		
		good_probabilities = []
		for c, x in enumerate(manual_gradings):
			if x.upper() == "A" or x.upper() == "B":
				good_probabilities.append(ps[c])
		print(good_probabilities)

		_hist, _bin = np.histogram(good_probabilities, bins = np.linspace(0, 1, 11))


		with open(output_file, 'w') as f:
			for i in range(len(hist)):
				f.write("{:.2}\t{}\t{}\t{}\n".format(bin_centres[i], hist[i], integral[i], _hist[i]))

	if p_type == "d":
		plotter(_d)
	elif p_type == "p":
		plotter(p)
	else:
		print("no valid option, quitting...")

"""


#plot("imported_figures/21mar_default_merge/21mar_default_filtered.csv", "manual/21mar_default_multi_repicked.txt", "plot_data/21mar_default_test.csv")
plot(args.csv_file, args.manual_file, args.output_root, args.plot_root)