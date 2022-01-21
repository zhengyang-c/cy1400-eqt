import datetime
import pandas as pd
import argparse
import obspy
from obspy.geodetics import gps2dist_azimuth
import math
import numpy as np
import json
from utils  import parse_station_info
import os
import glob
import multiprocessing as mp
from itertools import repeat
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

def station_event_distances(station_file, event_csv, patched_csv, output_json):

	# patched_csv = "real_postprocessing/rereal/patch_merged_eqt_rereal.csv"
	# event_csv = "real_postprocessing/rereal/all_rereal_events.csv"
	# output_json = "real_postprocessing/rereal/rereal_station_dist.json"
	# station_file = "new_station_info.dat"
	# station_file = "new_station_info.dat"
	# # output_csv = "real_postprocessing/rereal/all_rereal_eqt_mags.csv"

	# event_csv = "real_postprocessing/julaug20/julaug_real_cat.csv"

	# patched_csv = "real_postprocessing/julaug20/julaug20_eqt_patched.csv"
	# output_json = "real_postprocessing/julaug20/julaug20_station_dist.json"


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

			evla, evlo, evdp = event_df[event_df["ID"] == id]["LAT"].iloc[0], event_df[event_df["ID"] == id]["LON"].iloc[0], event_df[event_df["ID"]==id]["DEPTH"].iloc[0]

			dist = dx((stlo, stla), (evlo, evla))

			dist = np.sqrt(dist**2 + evdp**2)

			output_info[_id][row.station] = dist


	with open(output_json, "w") as f:
		json.dump(output_info, f, indent = 4)

def worker(df_info, station_dist):
	source_file = df_info[0]	
	_df = df_info[1]

	paz_wa = {'sensitivity': 2080, 'zeros': [0j,0j], 'gain': 1, 'poles': [-5.4978 - 5.6089j, -5.4978 + 5.6089j]}

	own_pz = {'zeros': [0j, 0j, 0j], 'poles': [-2.199000e+01 +2.243000e+01j, -2.199000e+01 -2.243000e+01j], 'gain':1.029447e+09 , 'sensitivity': 1} 
	print(source_file)

	output_indices = []
	output_mags = []

	try:

		if len(glob.glob(source_file)):
			st = obspy.read(source_file)
			delta = st[0].stats.delta
			p_before = 0.5
		else:
			# load remap

			station_remap = {"A02": "A54", "A10": "TG03", "GE01": "GN01", "GE16": "GN16", "GE10": "GN10", "GE07":"GN07", "AS09":"AN09", "GE13":"GN13", "TA02":"TN02", "MA01": "MN01", "GE15":"GN16", "GM05":"GM55"}

			rev_map = {v:k for k,v in station_remap.items()}

			# get station from sourcefile, try changing station. if it fails, then raise Exception 

			for k in rev_map:
				if k in source_file:
					source_file = source_file.replace(k, rev_map[k])
					break
			if not len(glob.glob(source_file)):
				print("new source file", source_file)
				raise ValueError

			st = obspy.read(source_file)
			delta = st[0].stats.delta
			p_before = 0.5

	except:
		return (None, None)
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

		ptime_id = round(5/delta) #round((row.p_arrival_time - row.sac_start_dt).total_seconds()/delta)
		start_id = ptime_id - round(p_before/delta)
		end_id = ptime_id + round(p_after/delta)

		datatre = ch_e[start_id:end_id]
		datatrn = ch_n[start_id:end_id]

		dist = station_dist[_id][row.station]

		amp = (np.max(datatre) + np.abs(np.min(datatre)) + np.max(datatrn) + np.abs(np.min(datatrn)))/4 * 1000 * 15000 
		# 15000 is for the nodes 
		# 1000 is from meter to millimeter (mm) see Hutton and Boore (1987)
		mag = math.log10(amp) + 1.110*math.log10(dist/100) + 0.00189*(dist-100) + 3.0

		output_indices.append(index)
		output_mags.append(mag)
		
		print(index, mag)

	return (output_indices, output_mags)

def main(station_file, patched_csv, dist_json, output_csv, om = "", oe = ""):

	# patched_csv = "real_postprocessing/rereal/patch_merged_eqt_rereal.csv"
	# dist_json = "real_postprocessing/rereal/rereal_station_dist.json"
	# station_file = "new_station_info.dat"
	# # output_csv = "real_postprocessing/rereal/all_rereal_eqt_mags.csv"

	# patched_csv = "real_postprocessing/julaug20/julaug20_eqt_patched.csv"
	# dist_json = "real_postprocessing/julaug20/julaug20_station_dist.json"
	# output_csv = "real_postprocessing/julaug20/mags_test.csv"

	df = pd.read_csv(patched_csv)

	df = df[(df["ID"] < 4125) & (df["ID"] > 4099)]

	df['p_arrival_time'] = pd.to_datetime(df['p_arrival_time'])
	df['s_arrival_time'] = pd.to_datetime(df['s_arrival_time'])

	with open(dist_json, "r") as f:
		station_dist = json.load(f)

	# load the main dataframe (patched) which is an output from cut_sac_from_timestamp.py

	# first go through the json to calculate station - event locations, of which there are a lot

	# stt is the stream data


	with mp.Pool(mp.cpu_count()) as p:
		groupby = df.groupby("source_file")
		groups = [(group, groupby.get_group(group)) for group in groupby.groups] 

		indices, mags = zip(*p.starmap(worker, zip(groups, repeat(station_dist))))

		print(indices, mags)
	
	for i in range(len(indices)):
		if indices[i]:
			# not None
			for j in range(len(indices[i])):
				df.at[indices[i][j], "m_l"] = mags[i][j]
	
	df.to_csv(output_csv, index = False)


if __name__ == "__main__":
	
	ap = argparse.ArgumentParser()

	ap.add_argument("station_file")
	ap.add_argument("dist_json")
	ap.add_argument("-e", "--event_csv")
	ap.add_argument("-o", "--output_csv")
	ap.add_argument("-omag", "--output_mags")
	ap.add_argument("-oerr", "--output_errors")
	ap.add_argument("-p", "--patched_eqt")
	ap.add_argument("-cd", "--calc_dist", action = "store_true")
	ap.add_argument("-cm", "--calc_mag", action = "store_true")

	args = ap.parse_args()

	if args.calc_dist:
		station_event_distances(args.station_file, args.event_csv, args.patched_eqt, args.dist_json)
	elif args.calc_mag:
		main(args.station_file, args.patched_eqt, args.dist_json, args.output_csv, om = args.output_mags, oe = args.output_errors)
	else:
		raise ValueError("Specify -cd or -cm")
#def station_event_distances(station_file, event_csv, patched_csv, output_json)):
#def main(station_file, patched_csv, dist_json, output_csv):