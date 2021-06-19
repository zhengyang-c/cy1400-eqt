import argparse
import pandas as pd

import glob
import os
import datetime
import subprocess
import matplotlib.pyplot as plt

import time

from pathlib import Path


def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")


def sac_plotter(sac_csv, csv_file):

	# output_file is the bashscript to be kept inside the merged folder
	# it is generated and when run it will do all the necessary cutting 

	try:
		sac_df = pd.read_csv(sac_csv)
		df = pd.read_csv(csv_file)	
	except FileNotFoundError:
		print("plot eqt: no files found")	
		return 0

	#print(sac_df)

	csv_dir = "/".join(csv_file.split("/")[:-1])

	save_dir = "sac_picks"

	if not os.path.exists(os.path.join(csv_dir, save_dir)):
		os.makedirs(os.path.join(csv_dir, save_dir))
		

	df['event_start_time'] = pd.to_datetime(df['event_start_time'])


	with open(os.path.join(csv_dir, "cut_and_plot.sh"), "w") as f:

		for index, row in df.iterrows():

			sta = row.station

			event_dt = row.event_start_time

			year = (datetime.datetime.strftime(event_dt, "%Y"))
			jday = (datetime.datetime.strftime(event_dt, "%j"))

			pick_year_day = year + "."+ jday # need string representation

			#year, jday = int(year), int(jday) # the julian is saved as integer so need to convert (085 vs 85)

			_df = (sac_df[(sac_df.station == sta) & (sac_df.year == int(year)) & (sac_df.jday == int(jday))])
			_df.reset_index(inplace = True)

			# load routine
			sac_source  = os.path.join("/".join(_df.at[0, "filepath"].split("/")[:-1]), "*{}*.SAC".format(pick_year_day))

			timestamp = (datetime.datetime.strftime(event_dt, "%H%M%S"))

			event_id = "{}.{}.{}.{}".format(sta, year, jday, timestamp)

			f1 = os.path.join(csv_dir, save_dir, event_id + ".EHE.SAC")
			f2 = os.path.join(csv_dir, save_dir, event_id + ".EHN.SAC")
			f3 = os.path.join(csv_dir, save_dir, event_id + ".EHZ.SAC")

			png_id = event_id + ".png"

			start_of_day = datetime.datetime.combine(datetime.datetime.strptime(pick_year_day, "%Y.%j"), datetime.time.min)
			start_time = (event_dt - start_of_day).total_seconds() - 30
			end_time = (event_dt - start_of_day).total_seconds() + 120


			#printf "cut $start_time $end_time\nr $fp/*$sac_id*SAC\nwrite SAC $f1 $f2 $f3\nq\n"
			#printf "sgf DIRECTORY /home/zchoong001/cy1400/cy1400-eqt/temp OVERWRITE ON\nqdp off\nr $f1 $f2 $f3\nbp p 2 n 4 c 1 45\nq\n"
			#
			# one printf to cut sac file, another to plot
			# 
			
			write_str = ""

			write_str += "printf \"cut {:.2f} {:.2f}\\nr {}\\nwrite SAC {} {} {}\\nq\\n\" | sac\n".format(start_time, end_time, sac_source, f1, f2, f3)
			
			write_str += "printf \"sgf DIRECTORY /home/zchoong001/cy1400/cy1400-eqt/temp OVERWRITE ON\\nqdp off\\nr {} {} {}\\nbp p 2 n 4 c 1 45\\nq\\n\" | sac\n".format(f1,f2,f3)

			f.write(write_str)

	# call subprocess

	os.chmod(os.path.join(csv_dir, "cut_and_plot.sh"), 0o775)
	subprocess.Popen(["{}".format(os.path.join(csv_dir, "cut_and_plot.sh"))])			

def plot(sac_csv, csv_file):

	import obspy
	from obspy import read
	try:
		sac_df = pd.read_csv(sac_csv)

		df = pd.read_csv(csv_file)	
	except FileNotFoundError:
		print("plot eqt: no files found")	
		return 0

	#print(sac_df)

	csv_dir = "/".join(csv_file.split("/")[:-1])

	save_dir = "sac_picks"

	if not os.path.exists(os.path.join(csv_dir, save_dir)):
		os.makedirs(os.path.join(csv_dir, save_dir))
		

	df['event_start_time'] = pd.to_datetime(df['event_start_time'])

	prev_year_day = ""
	for index, row in df.iterrows():

		sta = row.station

		#print(sta)
		#print(sac_df[sac_df.station == sta])
		event_dt = row.event_start_time

		year = (datetime.datetime.strftime(event_dt, "%Y"))
		jday = (datetime.datetime.strftime(event_dt, "%j"))

		pick_year_day = year + "."+ jday # need string representation

		#year, jday = int(year), int(jday) # the julian is saved as integer so need to convert (085 vs 85)


		_df = (sac_df[(sac_df.station == sta) & (sac_df.year == int(year)) & (sac_df.jday == int(jday))])
		_df.reset_index(inplace = True)

		# load routine
		sac_source  = os.path.join("/".join(_df.at[0, "filepath"].split("/")[:-1]), "*{}*.SAC".format(pick_year_day))

		if prev_year_day == "" or not prev_year_day == pick_year_day:
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
			if not os.path.exists(os.path.join(csv_dir, save_dir, "{}.{}.{}.{}.{}.SAC".format(sta, year, jday, event_dt.strftime("%H%M%S"), tr.stats.channel))):

				tr.write(os.path.join(csv_dir, save_dir, "{}.{}.{}.{}.{}.SAC".format(sta, year, jday, event_dt.strftime("%H%M%S"),  tr.stats.channel),), format = "SAC")

		# trim a bit more then plot ?
		_st.trim(start_UTC_time + delta_t - 10, start_UTC_time + delta_t + 50)
		png_file = "{}.{}.{}.{}.png".format(sta, year, jday, event_dt.strftime("%H%M%S"))
		if not os.path.exists(os.path.join(csv_dir, save_dir, png_file)):
			_st.plot(outfile = os.path.join(csv_dir, save_dir, png_file), size = (800, 600))


		prev_year_day = pick_year_day

if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument('sac_csv', help = "csv file with all the source SAC files")
	parser.add_argument('csv_file', help = "filtered csv file generated by EQT")
	#parser.add_argument('-t', '--time', type = str, help = "file path to append to")

	args = parser.parse_args()


	sac_plotter(args.sac_csv, args.csv_file)
	# start_time = datetime.datetime.now()

	# plot(args.sac_csv, args.output_folder)

	# end_time = datetime.datetime.now()

	# time_taken = (end_time - start_time).total_seconds()

	# if args.time:
	# 	with open(args.time, "a") as f:
	# 		f.write("plot_eqt,{} days,{},{}\n".format(args.input_folder, datetime.datetime.strftime(start_time, "%Y%m%d %H%M%S"),time_taken))



