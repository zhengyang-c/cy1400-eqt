import os
import pandas as pd
import glob
import argparse
import subprocess
import time

def header_writer(csv_file):

	try:
		df = pd.read_csv(csv_file)
	except FileNotFoundError:
		print("header_writer: file not found")
		return 0

	sta = df.at[0, "station"]

	df['event_start_time'] = pd.to_datetime(df['p_arrival_time'])
	df['p_arrival_time'] = pd.to_datetime(df['p_arrival_time'])
	df['s_arrival_time'] = pd.to_datetime(df['s_arrival_time'])
	df['event_end_time'] = pd.to_datetime(df['event_end_time'])

	csv_dir = "/".join(csv_file.split("/")[:-1])

	output_file = os.path.join(csv_dir, "write_headers.sh")

	with open(output_file, 'w') as f:
		f.write("#!/bin/sh\n")

		for index, row in df.iterrows():

			year_day = datetime.datetime.strftime(row.event_start_time, "%Y.%j")
			start_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.min)

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
				end_diff = (row.event_end_Time - start_of_day).total_seconds()


			f.write("printf \"r {}\\nch A {}\\nch T0 {}\\nch F {}\\nwh\\nq\\n".format(
				os.path.join(csv_dir, 'sac_picks', "*{}*SAC").format(year_day),
				p_diff,
				s_diff,
				end_diff
				))

	time.sleep(1)
	os.chmod(output_file, 0o775)

	time.sleep(1)
	subprocess.call(["{}".format(output_file)])	




if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("csv_file") # csv

	args = parser.parse_args()


	header_writer(args.csv_file)