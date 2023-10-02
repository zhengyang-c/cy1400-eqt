import argparse
import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
from utils import theoretical_misfit

import json

def find_median_sp(t_m, a_m):

	sps = []

	for sta in t_m:

		_spt = t_m[sta]['tt_S'] - t_m[sta]['tt_P']
		try:
			_spa = float(a_m[sta]['S']) - float(a_m[sta]['P'])
		except:
			continue

		sps.append(np.abs(_spa - _spt))

	return np.median(sps)


def main(real_csv, real_json, tt_path, station_info, output_path):

	df = pd.read_csv(real_csv)
	id_list = df["ID"].tolist()

	with open(real_json, "r") as f:
		all_station_info = json.load(f)

	with open(tt_path, "rb") as f:
		tt = np.load(f)

	all_sp_deltas = []
	
	for id in id_list:
		_pid = str(id).zfill(6)

		t_m = theoretical_misfit(tt, all_station_info[_pid]['data'], id, df, station_info)

		observed_times = (all_station_info[_pid]["data"])

		target_index = df.index[df['ID'] == id].tolist()[0]
		sps = find_median_sp(t_m, observed_times)

		df.at[target_index, "sp_misfit"] = sps

		all_sp_deltas.append(sps)

	plt.hist(all_sp_deltas)
	plt.show()

	df.to_csv(output_path, index = False)

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("real_csv")
	ap.add_argument("real_json")
	ap.add_argument("tt_path")
	ap.add_argument("station_info")
	ap.add_argument("output_path")
	args = ap.parse_args()
	main(args.real_csv, args.real_json, args.tt_path, args.station_info, args.output_path) 