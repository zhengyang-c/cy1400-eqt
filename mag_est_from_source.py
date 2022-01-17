import datetime
import pandas as pd
import argparse
import obspy
from obspy.geodetics import gps2dist_azimuth
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

	patched_csv = "real_postprocessing/rereal/patch_merged_eqt_rereal.csv"
	dist_json = "real_postprocessing/rereal/rereal_station_dist.json"
	station_file = "new_station_info.dat"
	output_csv = "real_postprocessing/rereal/all_rereal_eqt_mags.csv"


	df = pd.read_csv(patched_csv)

	df['p_arrival_time'] = pd.to_datetime(df['p_arrival_time'])
	df['s_arrival_time'] = pd.to_datetime(df['s_arrival_time'])
	df['sac_start_dt'] = pd.to_datetime(df['sac_start_dt'])


	with open(dist_json, "r") as f:
		station_dist = json.load(f)

	station_info = parse_station_info(station_file)
	# load the main dataframe (patched) which is an output from cut_sac_from_timestamp.py

	# first go through the json to calculate station - event locations, of which there are a lot

	paz_wa = {'sensitivity': 2080, 'zeros': [0j,0j], 'gain': 1, 'poles': [-5.4978 - 5.6089j, -5.4978 + 5.6089j]}

	own_pz = {'zeros': [0j, 0j, 0j], 'poles': [-2.199000e+01 +2.243000e+01j, -2.199000e+01 -2.243000e+01j], 'gain':1.029447e+09 , 'sensitivity': 1} 

	for source_file, _df in df.groupby("source_file"):
		print(source_file)
		st = obspy.read(source_file)
		delta = st[0].stats.delta
		p_before = 0.5
		for index, row in _df.iterrows():
			stt = st.copy()

			stt.trim(obspy.UTCDateTime(row.p_arrival_time + datetime.timedelta(seconds = -5)), obspy.UTCDateTime(row.s_arrival_time + datetime.timedelta(seconds = 4)))

			stt.detrend("demean")
			stt.detrend("linear")

			stt.simulate(paz_remove = own_pz, paz_simulate = paz_wa)
			stt[0].filter(type = "bandpass", freqmin = 0.2, freqmax = 20.0, zerophase = True)
			stt[1].filter(type = "bandpass", freqmin = 0.2, freqmax = 20.0, zerophase = True)

			ch_e = stt[0].data
			ch_n = stt[1].data

			_id = str(int(row.ID)).zfill(6)
			p_after = (row.s_arrival_time - row.p_arrival_time).total_seconds() + 3

			ptime_id = 500 #round((row.p_arrival_time - row.sac_start_dt).total_seconds()/delta)
			start_id = ptime_id - round(p_before/delta)
			end_id = ptime_id + round(p_after/delta)

			datatre = ch_e[start_id:end_id]
			datatrn = ch_n[start_id:end_id]

			dist = station_dist[_id][row.station]

			amp = (np.max(datatre) + np.abs(np.min(datatre)) + np.max(datatrn) + np.abs(np.min(datatrn)))/4 * 1000 * 15000 
			# 15000 is for the nodes 
			# 1000 is from meter to millimeter (mm) see Hutton and Boore (1987)
			mag = math.log10(amp) + 1.110*math.log10(dist/100) + 0.00189*(dist-100) + 3.0

			df.at[index, "mag"] = mag

	
	df.to_csv(output_csv, index = False)


if __name__ == "__main__":
	
	main()
