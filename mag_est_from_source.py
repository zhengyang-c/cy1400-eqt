import pandas as pd
import argparse
import obspy
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

	patched_csv = "real_postprocessing/rereal/test.csv"
	event_csv = "real_postprocessing/rereal/all_rereal_events.csv"
	dist_json = "real_postprocessing/rereal/rereal_station_dist.json"
	station_file = "new_station_info.dat"


	df = pd.read_csv(patched_csv)


	with open(dist_json, "r") as f:
		station_dist = json.load(f)

	station_info = parse_station_info(station_file)
	# load the main dataframe (patched) which is an output from cut_sac_from_timestamp.py

	# first go through the json to calculate station - event locations, of which there are a lot

	paz_wa = {'sensitivity': 2080, 'zeros': [0j,0j], 'gain': 1, 'poles': [-5.4978 - 5.6089j, -5.4978 + 5.6089j]}

	own_pz = {'zeros': [0j, 0j, 0j], 'poles': [-2.199000e+01 +2.243000e+01j, -2.199000e+01 -2.243000e+01j], 'gain':1.029447e+09 , 'sensitivity': 1} 

	for source_file, _df in df.groupby("source_file"):
		st = obspy.read(source_file)

		st.interpolate(sampling_rate = 100)
		st.detrend("demean")
		st.detrend("linear")

		st.simulate(paz_remove = own_pz, paz_simulate = paz_wa)

		ch_e = st[0].data
		ch_n = st[1].data

		print(ch_e.stats.channel)
		print(ch_n.stats.channel)

		ch_e.filter(type = "bandpass", freqmin = 0.2, freqmax = 20.0, zerophase = True)
		ch_n.filter(type = "bandpass", freqmin = 0.2, freqmax = 20.0, zerophase = True)

		for row, index in _df.iterrows():
			print(row.p_arrival_time)
			print(row.s_arrival_time)
			print(row.sac_start_dt)

		break

		# get P and S times: get EQT time by matching the ID, subtract from the sac start time that is included in the eqt dataframe



	# group by 'source_file'
	# for each day, load the source file in obspy



	# 

	pass


if __name__ == "__main__":
	main()
