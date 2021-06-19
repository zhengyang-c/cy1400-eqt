import obspy
from obspy import read
import os
import pandas as pd
import glob
from obspy import UTCDateTime
import argparse
import subprocess

# just call writerino from here...


def header_writer(csv_file, output_file):

	df = pd.read_csv(csv_file)

	sta = df.at[0, "station"]

	df['p_arrival_time'] = pd.to_datetime(df['p_arrival_time'])
	df['s_arrival_time'] = pd.to_datetime(df['s_arrival_time'])
	df['event_end_time'] = pd.to_datetime(df['event_end_time'])

	with open(output_file, 'w') as f:

		for index, row in df.iterrows():

			year_day = datetime.datetime.strftime(row.p_arrival_time, "%Y.%j")
			start_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.min)

			if not row.p_arrival_time: # NaN
				p_diff = "-12345"

			else:
				p_diff = (row.p_arrival_time - start_of_day).total_seconds()

			if not row.s_arrival_time:
				s_diff = "-12345"

			else:
				s_diff = (row.s_arrival_time - start_of_day).total_seconds()

			f.write("{},{},{},{}\n".format(row.station_lon, row.station_lat, p_diff, s_diff))



if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("csv_file") # csv
	parser.add_argument("output_file") # next to .csv

	args = parser.parse_args()


	header_writer(args.csv_file, args.output_file)