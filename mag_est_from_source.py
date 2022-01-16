import pandas as pd
import argparse
from obspy import read
from obspy.geodetics import gps2dist_azimuth
import os
import glob
import time
import subprocess
import math
import numpy as np
import json
from utils  import parse_station_info

# need to know event distance 

def dx(X1, X2):
	"""
	
	takes in two coordinate tuples (lon, lat), (lon, lat) returning their distance in kilometres
	gps2dist_azimuth also returns the azimuth but i guess i don't need that yet
	it also returns distances in metres so i just divide by 1000

	the order doesn't matter
	
	:param      X1:   The x 1
	:type       X1:   { type_description }
	:param      X2:   The x 2
	:type       X2:   { type_description }

	"""

	#print(X1, X2)
	return gps2dist_azimuth(X1[1], X1[0], X2[1], X2[0])[0] / 1000

def station_event_distances():

	patched_csv = "real_postprocessing/rereal/patch_merged_eqt_rereal.csv"
	event_csv = "real_postprocessing/rereal/all_rereal_events.csv"
	output_json = "real_postprocessing/rereal/rereal_station_dist.json"
	station_file = "new_station_info.dat"

	station_info = parse_station_info(station_file)

	event_df = pd.read_csv(event_csv)

	df = pd.read_csv(patched_csv)

	output_info = {}

	for id, _df in df.groupby('ID'):
		
		_id = str(int(id)).zfill(6)

		if _id not in output_info:
			output_info[_id] = {}

		for index, row in _df.iterrows():
			stla, stlo = station_info[row.station]["lat"], station_info[row.station]["lon"]

			evla, evlo = event_df[event_df["ID"] == id]["LAT"].iloc[0], event_df[event_df["ID"] == id]["LON"].iloc[0]

			dist = dx((stlo, stla), (evlo, evla))

			output_info[_id][row.station] = dist


	with open(output_json, "w") as f:
		json.dump(output_info, f, indent = 4)






def main():

	# load the main dataframe (patched) which is an output from cut_sac_from_timestamp.py

	# first go through the json to calculate station - event locations, of which there are a lot

	# or do a one-off computation



	# group by 'source_file'
	# for each day, load the source file in obspy



	# 

	pass


if __name__ == "__main__":
	station_event_distances()
