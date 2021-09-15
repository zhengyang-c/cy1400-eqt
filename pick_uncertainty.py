import pandas as pd
import numpy as np
import os, datetime
from pathlib import Path
import subprocess
import argparse
import matplotlib.pyplot as plt


from utils import load_graded_from_file_structure

def find_mean_and_std(collected_datetimes):
	_delta_times = [(collected_datetimes[i] - collected_datetimes[0]).total_seconds() for i in range(len(collected_datetimes))]
	
	return (np.mean(_delta_times), np.std(_delta_times))

def test_filter():

	pass

	# load csv
	# use agreement as cut off
	# use the det prob as moving threshold and plot precision v no. of events

def pca():
	df = pd.read_csv("imported_figures/21mar_default_merge/8may_remerged_nofilter.csv")
	print(len(df))

	df.drop(columns = ["time_mean"])
	df = df[df["agreement"] != 1]

	A = len(df[df.grade == "A"])
	B = len(df[df.grade == "B"])
	Z = len(df[df.grade == "Z"])
	print(A,B,Z)
	print(df)
	print((A+B)/(A+B+Z))

	X = df.loc[:,['time_std', 'd_prob_mean', 'd_prob_std', "p_prob_mean", "p_prob_std", "s_prob_mean", "s_prob_std", "detection_probability", "snr_sum"]]


	X = X - X.mean()
	X = X/X.std()

	S = X.cov()
	R = X.corr()

	l, Q = np.linalg.eig(S)

	idx = l.argsort()[::-1]

	l = l[idx]
	Q = Q[:,idx]

	#print(l)
	print(idx)
	#print(Q)

	Yp = X @ Q

	print(sum(l[0:2])/sum(l))

	colors = {"A":'green', 'B':'green', 'Z': 'red'}
	colorlist = df["grade"].apply(lambda x: colors[x])

	Yp.plot.scatter(0,1, marker = ".", c = colorlist, xlabel = "time_std (rotated)", ylabel = "d_prob_mean (rotated)")
	plt.show()
	#
	
	time_std_filter = Yp[Yp[0] > 0.5].index
	
	dff = (df.loc[time_std_filter, :])



	Ap = len(dff[dff.grade == "A"])
	Bp = len(dff[dff.grade == "B"])
	Zp = len(dff[dff.grade == "Z"])
	print(Ap,Bp,Zp)
	print((Ap+Bp)/(Ap+Bp+Zp))

	

	#print(Yp)


# why not just write a general merge class that is iterable so you can do e.g. process every row
# but there's alr iterrows()
# then j make it an input output function and share the functionality with merge_csv.py


def uncertainty():
	# calculate a few things and save to a new file
	# calculates mean (timestamp), std, 
	# if there is only 1 event (agreement = 1), it is dropped (not sure if this is gd practice / should always filter in code and not in the raw dataset) but i don't want to do the computation every time just load and plot
	# 
	# 

	graded_sac_folder = "imported_figures/21mar_default_merge/sac_picks/"
	raw_csv_file = "imported_figures/21mar_default_merge/21mar_default_raw.csv" 
	filtered_csv_file = "imported_figures/21mar_default_merge/21mar_default_filtered.csv"
	plot_file = "plot_data/8may_default_21mar_filtered_stds.csv"
	output_root = "plots/8may_default_21mar"




	df = load_graded_from_file_structure(graded_sac_folder, raw_csv_file)

	df.loc[:, "p_arrival_time"] = pd.to_datetime(df["p_arrival_time"])
	df.loc[:, "s_arrival_time"] = pd.to_datetime(df["s_arrival_time"])

	# ehh


	# this should be using the P and S wave time.............
	# fml.....
	# nbd but still...
	# 
	# # then shunbian throw in the detection_probability uncertainty.....


	df.sort_values(by=['p_arrival_time'], inplace = True)


	df = df.reset_index(drop=True) # do not insert index into dataframe columns


	COINCIDENCE_TIME_RANGE = 2	
	
	_tempgroup = []

	statistics = pd.DataFrame()
	statistics['collected_p_dt'] = ""
	statistics['collected_p_dt'] = statistics['collected_p_dt'].astype('object')

	statistics['collected_s_dt'] = ""
	statistics['collected_s_dt'] = statistics['collected_s_dt'].astype('object')


	# collected_p_dt is for the gaussian computation thing 

	# i just think this is messy and reminds me of my excel vba adventures

	c = 0 # counter for statistics dataframe so it's less messy overall

	for index, row in df.iterrows():

		curr_time = row["p_arrival_time"]
		if index == 0:
			prev_time = curr_time
			_tempgroup.append(index)

		df.at[index, 'use_or_not'] = 0

		_dt = (curr_time - prev_time).total_seconds()
		#print(_dt, curr_time, prev_time)

		if not index == 0 or index == len(df.index) - 1:
			if _dt < COINCIDENCE_TIME_RANGE:				
				_tempgroup.append(index)

			else: # new event group, dump the previous temp_group
				for ti in _tempgroup:
					df.at[ti, 'agreement'] = len(_tempgroup)

				# maybe create a new list and append the mean and std inside 
				
				_collected_datetimes = [df.at[ti, 'p_arrival_time'] for ti in _tempgroup]

				_collected_s_arrival = [df.at[ti, 's_arrival_time'] for ti in _tempgroup]

				_collected_d_probs = [df.at[ti, 'detection_probability'] for ti in _tempgroup]
				_collected_p_probs = [df.at[ti, 'p_probability'] for ti in _tempgroup]
				_collected_s_probs = [df.at[ti, 's_probability'] for ti in _tempgroup]

				_p_mean, _p_std = find_mean_and_std(_collected_datetimes)

				_s_mean, _s_std = find_mean_and_std(_collected_s_arrival)

				_p_mean_dt = _collected_datetimes[0] + datetime.timedelta(seconds = _p_mean)
				_s_mean_dt = _collected_s_arrival[0] + datetime.timedelta(seconds = _p_mean)

				_collected_p_dt = [(x - _p_mean_dt).total_seconds() for x in _collected_datetimes]
				_collected_s_dt = [(x - _s_mean_dt).total_seconds() for x in _collected_s_arrival]


				df.at[_tempgroup[len(_tempgroup)//2], 'use_or_not'] = 1 # keep the middle of the pack

				statistics.loc[c, ["time_mean", "time_std"]] = [df.at[_tempgroup[0], 'p_arrival_time'] + datetime.timedelta(seconds = _p_mean), _p_std]
				statistics.loc[c, ["s_arrival_mean", "s_arrival_std"]] = [df.at[_tempgroup[0], 's_arrival_time'] + datetime.timedelta(seconds = _s_mean), _s_std]

				# the means are probably not so useful...but just leave them in 
				statistics.loc[c, ["d_prob_mean", "d_prob_std"]] = [np.mean(_collected_d_probs), np.std(_collected_d_probs)]
				statistics.loc[c, ["p_prob_mean", "p_prob_std"]] = [np.mean(_collected_p_probs), np.std(_collected_p_probs)]
				statistics.loc[c, ["s_prob_mean", "s_prob_std"]] = [np.mean(_collected_s_probs), np.std(_collected_s_probs)]

				statistics.at[c, "collected_p_dt"] = _collected_p_dt

				c += 1

				_tempgroup = [index]



		df.at[index, 'dt'] = _dt

		prev_time = curr_time

	

	# add the means / csv data to df_filtered
	# rmbr if std = -1, then ignore i.e. only 1 run picked it up, but that should be clear / filtered earlier
	# 
	
	# assumes that the merge is the same between o hhh yeah right 

	#print(len(all_means), len(all_stds))
	

	df_filtered = df[df['use_or_not'] == 1]
	df_filtered = df_filtered.reset_index(drop = True)

	#df_filtered.to_csv("imported_figures/21mar_default_merge/21mar_default_remerged.csv")

	statistics.loc[:, 'grade'] = df_filtered['grade']
	statistics.loc[:, 'agreement'] = df_filtered['agreement']
	statistics.loc[:, 'detection_probability'] = df_filtered['detection_probability']
	statistics.loc[:, 'snr_sum'] = df_filtered['p_snr'] + df_filtered['s_snr']


	statistics = statistics[statistics["agreement"] != 1]
	#statistics = statistics[statistics["agreement"] == 50]
	#
	#
	#
	#

	

	# collapse the A, B and Z collected_p_dt to plot the histogram (?) 



	A_dt_hist = []

	for index, row in statistics[(statistics.grade == "A") & (statistics.agreement != 1)].iterrows():
		A_dt_hist.extend(statistics.at[index, 'collected_p_dt'])

	B_dt_hist = []

	for index, row in statistics[(statistics.grade == "B") & (statistics.agreement != 1)].iterrows():
		B_dt_hist.extend(statistics.at[index, 'collected_p_dt'])

	Z_dt_hist = []

	for index, row in statistics[(statistics.grade == "Z") & (statistics.agreement != 1)].iterrows():
		Z_dt_hist.extend(statistics.at[index, 'collected_p_dt'])

	_dt_bins = np.arange(-2,2, 0.005)

	_lenA = len(A_dt_hist)
	_lenB = len(B_dt_hist)
	_lenZ = len(Z_dt_hist)

	A_dt_hist, _ = np.histogram(A_dt_hist, bins = _dt_bins)
	B_dt_hist, _ = np.histogram(B_dt_hist, bins = _dt_bins)
	Z_dt_hist, _ = np.histogram(Z_dt_hist, bins = _dt_bins)

	A_dt_hist = A_dt_hist.astype("float")/(_lenA)
	B_dt_hist = B_dt_hist.astype("float")/(_lenB)
	Z_dt_hist = Z_dt_hist.astype("float")/(_lenZ)

		

	#plt.hist(A_dt_hist, bins = np.arange(-0.1, 0.1, 0.005))
	#plt.show()
	
	#statistics.to_csv("imported_figures/21mar_default_merge/8may_remerged_nofilter.csv", index = False)

	# filter away agreement = 1 bc that gives std = 0

	# timing bins

	write_data = pd.DataFrame()

	t_bins = np.arange(0, 1, 0.005)
	prob_bins = np.arange(0, 0.5, 0.01) # these are probability stdevs

	for _grade in ["A", "B", "Z"]:
		_hist, _bins = np.histogram(statistics[statistics["grade"] == _grade].time_std.values, bins = t_bins) 
		_s_std_hist, _ = np.histogram(statistics[statistics["grade"] == _grade].s_arrival_std.values, bins = t_bins)

		_tempdf = pd.DataFrame(
			{"{}_p_arrival_std_hist".format(_grade): _hist, 
			"{}_p_arrival_std_bins".format(_grade):(_bins[1:] + _bins[:-1])/2,
			"{}_s_arrival_std_hist".format(_grade):_s_std_hist, 
			"{}_s_arrival_std_bins".format(_grade):(_bins[1:] + _bins[:-1])/2,}
			)

		write_data = pd.concat([write_data, _tempdf], axis = 1)
		#write_data.extend([_hist, (_bins[1:] + _bins[:-1])/2]) # wow u can do this?

		for _cat in ["d_prob_std", "p_prob_std", "s_prob_std"]:

			_hist, _bins = np.histogram(statistics[statistics["grade"] == _grade][_cat].values, bins = prob_bins) 

			_tempdf = pd.DataFrame(
			{"{}_{}_hist".format(_grade, _cat): _hist, 
			"{}_{}_bins".format(_grade, _cat):(_bins[1:] + _bins[:-1])/2}
			)

			write_data = pd.concat([write_data, _tempdf], axis = 1)
			#write_data.extend([_hist, (_bins[1:] + _bins[:-1])/2]) # wow u can do this?
			#write_headers.append("{}_{}_bins".format(_grade, _cat))
			#write_headers.append("{}_{}_hist".format(_grade, _cat))

	#print(write_data)

	hist_df = pd.DataFrame({"dt_bins":(_dt_bins[1:] + _dt_bins[:-1])/2, "A_dt_hist":A_dt_hist, "B_dt_hist":B_dt_hist, "Z_dt_hist":Z_dt_hist})
	write_data = pd.concat([write_data, hist_df], axis = 1)



	write_data.to_csv(plot_file, index = False)

	#process = subprocess.Popen(["gnuplot", "-c", "plot_indiv_pick_uncertainty.gn", plot_file, "plots/9may_ABZ_timing_uncertainty_defaultmulti21mar.pdf"])

	process = subprocess.Popen(["gnuplot", "-c", "plot_pick_stds.gn", plot_file, output_root ])

uncertainty()
