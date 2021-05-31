# this exists in a pipeline

# compare_detection.py --> plot_compare.py

# the output of compare_detection.py goes into this

# input:
# input file: basically a log file as printed above, with one header row
# along with 4 columns, {$n, $timestamp.png, (1/0), (1/0) ... }


# output:
#
#
#


import glob
import os
import argparse
import numpy as np
import datetime
import dateutil.parser
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import random

# histogram http://www.gnuplotting.org/calculating-histograms/

def main(input_file):


	print(input_file)

	# input_folders: an ORDERED LIST of where the SAC files are 

	global_list = []
	headers = []

	with open(input_file, 'r') as f:
		for c, line in enumerate(f):
			if c == 0:
				headers = line.strip().split("\t")
				continue
			global_list.append(line.strip().split("\t"))
	#print(global_list)
	#print(headers)
	#print(len(global_list))

	# (1) collapse list to get no. of unique events where the events are within 3 seconds of each other 

	#print(global_list[0])

	collapsed_list = []
	only_timestamps = []

	for line in global_list:
		_timestamp = "{} {} {}".format(line[1].split(".")[1], line[1].split(".")[2], line[1].split(".")[3])
		#print(_timestamp)
		_timestamp = datetime.datetime.strptime( _timestamp, r"%Y %j %H%M%S")
		check_list = [_timestamp + datetime.timedelta(seconds=x) for x in [-2, -1, 0, 1, 2]]
		if all([x not in only_timestamps for x in check_list]):
			only_timestamps.append(_timestamp)
			collapsed_list.append(line)
		else: # use an OR to merge the 1s
			# just assume that the target is the latest one
			for item in range(len(collapsed_list[-1][2:])):
				collapsed_list[-1][2:][item] = int(collapsed_list[-1][2:][item]) | int(line[2:][item])

	print(len(only_timestamps))

	# (2) get no. of common events per detection (histogram)

	# find agreement:

	agreement = [sum([int(y) for y in x[2:]]) for x in collapsed_list]

	#print("no. of stations:", len(collapsed_list[2:]))

	plt.title("Histogram of event agreement across multiple runs")
	plt.hist(agreement, bins = np.arange(1, len(collapsed_list[0][2:])))
	plt.xlabel("No. of runs in agreement")
	plt.ylabel("No. of events")
	#plt.show()

	### CHANGE PLOT NAME ###

	plt.savefig("plots/", dpi = 300)

	### change plot name ###


	# (3) sample, picking N random columns where N is from 1 to no.(stations). find number of unique events 

	# sampling is only needed for like checking multiple runs with the same model

	# pick from the collapsed list

	# N_repeats = 25

	# statistics = []
	
	# indices = list(range(1, len(collapsed_list[-1][2:]) - 1) )
	# for n_pick in indices:
	# 	#print(n_pick)
	# 	_stat = []
	# 	for i in range(N_repeats):
	# 		sampled_indices = random.sample(list(range(len(collapsed_list[0][2:]))), n_pick)
	# 		# construct a new list, write a function eat that up
	# 		sample_list = []
	# 		for k in collapsed_list:
	# 			_sample_line = [k[1],]
	# 			for j in sampled_indices:
	# 				_sample_line.append(k[j + 2])
	# 			sample_list.append(_sample_line)
	# 		#print(sample_list[0])

	# 		# collapse the sample_list because some will be completely blank
	# 		collapsed_sample_list = []
	# 		for line in sample_list:
	# 			if any([x == "1" for x in line]):
	# 				collapsed_sample_list.append(line)
	# 		_stat.append(len(collapsed_sample_list))
	# 	statistics.append(_stat)
	# #print(len(statistics))
	# statistics = np.array(statistics)
	# #print(statistics[0])
	# means = np.mean(statistics, axis = 1)
	# stds = np.std(statistics, axis = 1)
	# #print(means[0])

	# out_file = "log/average_detections_per_rerun.log"

	# with open(out_file, "w") as f:
	# 	for z in range(len(means)):
	# 		f.write("{}\t{}\t{}\n".format(z+1, means[z], stds[z]))

# the following code is for writing out the SAC files for comparison
# but i stopped writing it cos there wasn't a point 

"""	for line in global_list:
		event = line[1].split(".")
		_sta = event[0]
		_year = (event[1])
		_jday = (event[2])
		_time = event[3]

		if not all(line[2:])

		event_time = obspy.UTCDateTime(year = _year, julday = _jday, hour = _time[:2], minute = _time[2:4], second = _time[-2:]) # is this needed lol

		delta_minus = 5 # very short cutting bc we're interested in the shape of the detection only 
		delta_plus = 10

		for _channel in ["EHZ", "EHE", "EHN"]:
			file_name = "AC.{}.00.{}.D.{}.*.000000.SAC*".format(_sta, _year, _day, _channel)
			st = read(file_name)
			# trim

			# plot


	# reading in the input file, STA.YEAR.DAY.TIMESTAMP.png
	# determine the day 

	# for each folder in input folders, (folder should immediately contain the SAC files)
	# if it's a new day, load the corresponding SAC file ()
	# if not a new day, don't load since this presumably takes time 
	
	# plot 3 channels vs 3 channels in a top down, maybe use a colour or something
	# to indicate which was the one that got detected
"""

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type = str)
#parser.add_argument('input_folder', type = str, nargs='*')

args = parser.parse_args()

main(args.input_file)

#../../EOS_SAC/TA19 and no_preproc/TA19
