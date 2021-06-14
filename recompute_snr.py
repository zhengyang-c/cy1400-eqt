import obspy # need to activate local conda env
import argparse
import pandas as pd
import numpy as np
import os
import datetime
from pathlib import Path
#from utils import load_with_path_and_grade
import matplotlib.pyplot as plt
import subprocess


def load_with_path_and_grade(csv_file, source_folder):
	sac_pathname = [str(path) for path in Path(source_folder).rglob('*.png')]

	sac_tracename = [x.split("/")[-1].split(".png")[0] for x in sac_pathname]

	folder_df = pd.DataFrame(np.column_stack([sac_pathname, sac_tracename]), columns = ["pathname", "wf"])

	for index, row in folder_df.iterrows():
		folder_df.at[index, 'grade'] = row.pathname.split("/")[-2]

	# load the csv file, make a new column for file name, do pd.merge to match the two of the


	csv_df = pd.read_csv(csv_file)
	csv_df['event_dt'] = pd.to_datetime(csv_df.event_start_time)


	for index, row in csv_df.iterrows():
		csv_df.at[index, 'wf'] = "{}.{}".format(row.station, datetime.datetime.strftime(row.event_dt, "%Y.%j.%H%M%S"))

	#print(csv_df)

	new_df = csv_df.merge(folder_df, on = "wf")

	return new_df

def recompute_from_sac_source(sac_select, detection_csv, output_csv):

	# load sac_select

	sac_df = pd.read_csv(sac_select)

	det_df = pd.read_csv(detection_csv)

	det_df.event_start_time = pd.to_datetime(det_df.event_start_time)

	# this is such a pain

	# divide the detections by days detection by day, then uh 
	# read the file for that day 
	# it's similar to plot_csv. iterate through the rows in the csv. do a look up from the sac_df using station and day to filter, 
	# then use wildcard to load if it's a new day / first day
	# 
	#
	
	prev_year_day = ""
	
	for index, row in det_df.iterrows():
		sta = row.station

		event_dt = row.event_start_time

		year = datetime.datetime.strftime(event_dt, "%Y")
		jday = datetime.datetime.strftime(event_dt, "%j")

		year_day = year + "."+ jday

		if index == 0:

			print(year_day)
			print(sac_df)

			# first row, load 

			_df = (sac_df[(sac_df.station == sta) & (sac_df.year == year) & (sac_df.jday == jday)])
			_df.reset_index(inplace = True)

			print(_df)

			print(_df.at[0, "filepath"])

		else:

			if year_day == prev_year_day:
				pass
			else:
				_df = (sac_df[(sac_df.station == sta) & (sac_df.year == year) & (sac_df.jday == jday)])
				_df.reset_index(inplace = True)

				print(_df)

				print(_df.at[0, "filepath"])

		if index > 5:
			break

		prev_year_day = year_day




def recompute_from_cut_sac(source_folder, csv_file, save_csv):

	#source_folder = "imported_figures/21mar_default_merge/sac_picks"
	#csv_file = "imported_figures/21mar_default_merge/21mar_default_filtered.csv"
	#save_csv = "imported_figures/21mar_default_merge/21may_recomputedsnr_default.csv"
	#output_file = "plot_data/21may_recomputedsnr_21mardefault_p-snr.csv"
	#plot_file = "plots/21may_recomputedsnr_21mardefault_p-snr.pdf"

	df = load_with_path_and_grade(csv_file, source_folder)

	df['p_arrival_time'] = pd.to_datetime(df['p_arrival_time'])
	df['s_arrival_time'] = pd.to_datetime(df['s_arrival_time'])

	#print(df)

	#print(df['pathname'])

	for index, row in df.iterrows():

		st = obspy.read(row.pathname[:-4] + "*C")
		st.filter('bandpass', freqmin = 1.0, freqmax = 45, corners = 2, zerophase = True)
		st.resample(100.0)		
		

		_tracestart = st[0].stats.starttime

		# get the p arrival, get s arrival
		# get timing difference, convert to sample number
		# slice samples to compute snr 
		# 
		
		p_arrival_sample = int((obspy.UTCDateTime(row.p_arrival_time) - _tracestart) * 100)

		s_arrival_sample = int((obspy.UTCDateTime(row.s_arrival_time) - _tracestart) * 100)

		window = 100 # 1 second

		p_snr = (np.percentile(st[2].data[p_arrival_sample : p_arrival_sample + 100], 95) / np.percentile(st[2].data[p_arrival_sample - 100: p_arrival_sample], 95))


		horizontal_S = np.concatenate((st[0].data[s_arrival_sample : s_arrival_sample + 100], (st[1].data[s_arrival_sample : s_arrival_sample + 100])))
		horizontal_N = np.concatenate((st[0].data[s_arrival_sample - 100 : s_arrival_sample], (st[1].data[s_arrival_sample - 100 : s_arrival_sample])))

		s_snr = (np.percentile(horizontal_S, 95) / np.percentile(horizontal_N, 95))**2

		df.at[index, 'new_p_snr_percentileratio'] = p_snr
		df.at[index, 'new_s_snr_percentileratio'] = s_snr

		p_snr_2 = np.sum(st[2].data[p_arrival_sample : p_arrival_sample + 100]**2) / np.sum(st[2].data[p_arrival_sample - 100: p_arrival_sample]**2)

		s_snr_2 = np.sum(horizontal_S**2)/np.sum(horizontal_N**2)

		df.at[index, 'new_p_snr_ampsq'] = p_snr_2
		df.at[index, 'new_s_snr_ampsq'] = s_snr_2

	df.to_csv(save_csv, index = False)

	# df = pd.read_csv("imported_figures/21mar_default_merge/21may_recomputedsnr_default.csv")

	# bins = np.arange(0, 200, 5)
	# write_data = []

	# for _grade in ["A", "B", "Z"]:

	# 	hist, _bins = np.histogram(df[df.grade == _grade].new_p_snr.values, bins = bins) 

	# 	# normalised because.... should be absolute number tbh

	# 	write_data.extend([hist, (_bins[1:] + _bins[:-1])/2]) # wow u can do this?

	# outputdf = pd.DataFrame(np.column_stack(write_data), columns = ["A", "A_bins", "B", "B_bins", "Z", "Z_bins"])
	# outputdf.to_csv(output_file, index = False)

	# process = subprocess.Popen(["gnuplot", "-c", "plotter/snrhist.gn", output_file, plot_file])

	# alternatively, load the sac files in obspy and use the sac traces hmmm

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	#parser.add_argument('source_folder', help = "sac_picks folder, from the eqt plotter")

	parser.add_argument('sac_csv', help = "csv with all the file paths")
	parser.add_argument('csv_file', help = "csv file generated by eqt")	
	parser.add_argument('save_csv', help = "new csv file with recomputed snrs")
	

	args = parser.parse_args()

	recompute_from_sac_source(args.sac_csv, args.csv_file, args.save_csv)
	#main(args.source_folder, args.csv_file, args.save_csv)



# /home/zchoong001/cy1400/cy1400-eqt/detections/single_day_test/TA19_outputs/X_prediction_results.csv
# /home/zchoong001/cy1400/cy1400-eqt/station_time/TA19_085.txt
