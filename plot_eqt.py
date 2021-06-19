import argparse
import pandas as pd
import obspy
from obspy import read
import glob
import os
import datetime

import matplotlib.pyplot as plt

from pathlib import Path


def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

def plot(sac_csv, csv_file):

	sac_df = pd.read_csv(sac_csv)

	df = pd.read_csv(csv_file)		

	csv_dir = "/".join(csv_file.split("/")[:-1])

	save_dir = "sac_picks"

	if not os.path.exists(os.path.join(csv_dir, save_dir)):
		os.makedirs(os.path.join(csv_dir, save_dir))
		

	df['event_start_time'] = pd.to_datetime(df['event_start_time'])

	prev_year_day = ""
	for index, row in df.iterrows():

		sta = row.station.strip()
		event_dt = row.event_start_time

		year = (datetime.datetime.strftime(event_dt, "%Y"))
		jday = (datetime.datetime.strftime(event_dt, "%j"))

		pick_year_day = year + "."+ jday # need string representation

		#year, jday = int(year), int(jday) # the julian is saved as integer so need to convert (085 vs 85)


		_df = (sac_df[(sac_df.station == sta) & (sac_df.year == (year)) & (sac_df.jday == (jday))])
		_df.reset_index(inplace = True)

		# load routine
		sac_source  = os.path.join("/".join(_df.at[0, "filepath"].split("/")[:-1]), "*{}*.SAC".format(pick_year_day))

		if c == 0 or not prev_year_day == pick_year_day:
			st = read(os.path.join(sac_source)) 

			st.filter('bandpass', freqmin = 1.0, freqmax = 45, corners = 2, zerophase = True)
			st.resample(100.0)		
			st.detrend('demean')


			# bp filter and demean and resample

		# else, it's already loaded, can start trimming

		_st = st.copy()

		start_UTC_time = _st[0].stats.starttime
		delta_t = obspy.UTCDateTime(event_dt) - start_UTC_time
		_st.trim(start_UTC_time + delta_t - 30, start_UTC_time + delta_t + 120)



		# write SAC file 
		for tr in _st:
			if not os.path.exists(os.path.join(csv_dir, save_dir, "{}.{}.{}.{}.{}.SAC".format(sta, year, _day, event_dt.strftime("%H%M%S"), tr.stats.channel))):

				tr.write(os.path.join(csv_dir, save_dir, "{}.{}.{}.{}.{}.SAC".format(sta, _year, _day, event_dt.strftime("%H%M%S"),  tr.stats.channel),), format = "SAC")

		# trim a bit more then plot ?
		_st.trim(start_UTC_time + delta_t - 10, start_UTC_time + delta_t + 50)
		png_file = "{}.{}.{}.{}.png".format(sta, _year, _day, event_dt.strftime("%H%M%S"))
		if not os.path.exists(os.path.join(csv_dir, save_dir, png_file)):
			_st.plot(outfile = os.path.join(csv_dir, save_dir, png_file), size = (800, 600))


		prev_year_day = pick_year_day

if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument('sac_csv', help = "csv file with all the source SAC files")
	#parser.add_argument('sta')
	parser.add_argument('output_folder', help = "the merged folder in which to create new folder and write plots to")
	parser.add_argument('-t', '--time', type = str, help = "file path to append to")

	args = parser.parse_args()



	start_time = datetime.datetime.now()

	plot(args.sac_csv, args.output_folder)

	end_time = datetime.datetime.now()

	time_taken = (end_time - start_time).total_seconds()

	if args.time:
		with open(args.time, "a") as f:
			f.write("plot_eqt,{} days,{},{}\n".format(args.input_folder, datetime.datetime.strftime(start_time, "%Y%m%d %H%M%S"),time_taken))



