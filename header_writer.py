import os
import pandas as pd
import glob
import argparse
import subprocess
import time
import datetime
import obspy

def header_writer(csv_file):

	try:
		df = pd.read_csv(csv_file)
	except FileNotFoundError:
		print("header_writer: file not found")
		return 0

	df['event_start_time'] = pd.to_datetime(df['event_start_time'])
	df['p_arrival_time'] = pd.to_datetime(df['p_arrival_time'])
	df['s_arrival_time'] = pd.to_datetime(df['s_arrival_time'])
	df['event_end_time'] = pd.to_datetime(df['event_end_time'])


	# hdf = pd.read_csv(os.path.join(hdf5_folder,"{}.csv".format(station)))
	# hdf.rename(columns = {"trace_name": "file_name"}, inplace = True)

	# df = df.merge(hdf, on = "file_name")


	csv_dir = "/".join(csv_file.split("/")[:-1])

	output_file = os.path.join(csv_dir, "write_headers.sh")
	plot_file = os.path.join(csv_dir, "plot.sh")

	with open(output_file, 'w') as f:
		f.write("#!/bin/sh\n")

		for index, row in df.iterrows():

			year_day = datetime.datetime.strftime(row.event_start_time, "%Y.%j")
			try: # for backwards compatibility 
				sac_start_time = obspy.UTCDateTime(row["sac_start_time"])

				start_of_day = sac_start_time.datetime
			except:
				start_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.min)

			timestamp = datetime.datetime.strftime(row.event_start_time, '%H%M%S')

			if not row.p_arrival_time: # NaN
				p_diff = "-12345"

			else:
				p_diff = (row.p_arrival_time - start_of_day).total_seconds()

			if not row.s_arrival_time:
				s_diff = "-12345"

			else:
				s_diff = (row.s_arrival_time - start_of_day).total_seconds()

			if not row.event_end_time:
				end_diff = "-12345"

			else: 
				end_diff = (row.event_end_time - start_of_day).total_seconds()


			f.write("printf \"r {}\\nch A {:.2f}\\nch T0 {:.2f}\\nch F {:.2f}\\nwh\\nq\\n\" | sac\n".format(
				os.path.join(csv_dir, 'sac_picks', "*{}.{}*SAC").format(year_day, timestamp),
				p_diff,
				s_diff,
				end_diff
				))

	time.sleep(1)
	os.chmod(output_file, 0o775)

	time.sleep(1)
	subprocess.call(["{}".format(output_file)])	
	time.sleep(1)
	subprocess.call(["{}".format(plot_file)])




if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("csv_file") # csv
	parser.add_argument('-t', '--time', type = str, help = "file path to append to")


	start_time = datetime.datetime.now()
	args = parser.parse_args()


	header_writer(args.csv_file)

	end_time = datetime.datetime.now()

	time_taken = (end_time - start_time).total_seconds()

	if args.time:
		with open(args.time, "a+") as f:
			f.write("header_writer,{},{}\n".format(datetime.datetime.strftime(start_time, "%Y%m%d %H%M%S"),time_taken))
