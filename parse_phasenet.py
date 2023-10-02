import numpy as np
import pandas as pd
import json
import argparse
import datetime
import pprint
pp = pprint.PrettyPrinter(indent=4)

# goal is to compare 


# i feel like
# writing a wrapper to make it easier to call phasenet

############################## the command ######################3
# python phasenet/predict.py --model model/190703-214543 --data_list test_data/sac.csv --data_dir test_data/sac --format=sac --result_fname NAME

def main(input_file, input_eqt_csv, output_eqt_csv):
	with open(input_file, "r") as f:
		_picks = json.load(f)

	# print(_picks)

	# each SAC trace could have 0, 1, or N number of picks
	# the pick index will depend on the sampling rate
	# 
	picks = {} # use this to store all the info
	for pick in _picks:
		if pick["id"] not in picks:
			picks[pick["id"]] = []

		_data = {}

		for h in ["timestamp", "prob", "type"]:
			_data[h] = pick[h]

		picks[pick["id"]].append(_data)

	df = pd.read_csv(input_eqt_csv)
	df["p_arrival_time"] = pd.to_datetime(df["p_arrival_time"])
	df["s_arrival_time"] = pd.to_datetime(df["s_arrival_time"])

	# interestingly the index information is included in the .csv file but NOT the json file
	# which isn't really an issue... it saves a lot of trouble

	THRESHOLD = 1
	df_list = []

	for t in list(picks.keys()):

		uid = t.split("/")[1] # Fyi this will break so easily

		_df = (df[df["datetime_str"] == uid])[["datetime_str", "p_arrival_time", "s_arrival_time"]]

		_df_idx = (_df.index[0])

		# print(_df.p_arrival_time)
		# print(_df.s_arrival_time)

		# get probable p arrival
		# get probable s arrival
		print(uid)

		for pick in picks[t]:
			# print(_df.iloc[0]["p_arrival_time"], _df.iloc[0]["s_arrival_time"])
			# print(datetime.datetime.fromisoformat(pick["timestamp"]))
			if pick["type"] == "p":
				p_delta = ((datetime.datetime.fromisoformat(pick["timestamp"]) - _df.iloc[0]["p_arrival_time"]).total_seconds())
				if np.abs(p_delta) > THRESHOLD:
					continue
				else:
					_df.at[_df_idx, "phasenet_repick_P_delta"] = p_delta
			else:
				s_delta = ((datetime.datetime.fromisoformat(pick["timestamp"]) - _df.iloc[0]["s_arrival_time"]).total_seconds())

				if np.abs(s_delta) > THRESHOLD:
					continue
				else:
					_df.at[_df_idx, "phasenet_repick_S_delta"] = s_delta
		df_list.append(_df)


	odf = pd.concat(df_list, ignore_index=True)
	odf.to_csv(output_eqt_csv, index = False)



		# the calculated times are wrong because the sampling frequency is... 250 hz instead of 100 hz
		# the csv file gives the correct indices but the json file has the wrong times so...
		# just resample to 100hz


	# ASSUMPTIONS:
	# - the pick near the actual EQT pick is likely correct i.e. this is just a repicking
	# - what if the p wave signal is fake? and the S wave signal is fake? not sure, have to ask
	# - wtk no. of picks, associated probabilities

	# need to match with the EQT... list...
	# just match with the EQT datetime string because that's the name of the file

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("input_json")
	ap.add_argument("input_eqt_csv")
	ap.add_argument("output_eqt_csv")
	args = ap.parse_args()
	main(args.input_json, args.input_eqt_csv, args.output_eqt_csv)