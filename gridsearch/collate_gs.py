import json
from pathlib import Path
import numpy as np
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def check_json(search_folder, output_csv, misfit_csv):

	# want to know how many done / failed (well formed json)

	# want to collate a CSV file with most of the JSON parameters

	#search_folder = "gridsearch/7jul_gsr_afterREAL_deeperredo"

	pd_columns = ["ID", "evla_gs", "evlo_gs", "evdp_gs", "origin_time", "misfit_gs", "misfit_combined", "cell_size", "cell_height", "evla_c", "evlo_c", ]
	df = pd.DataFrame(columns = pd_columns)

	mdf = pd.DataFrame(columns = ["ID", "station", "misfit", "phase"])

	_c = 0

	all_json_files = [str(p) for p in Path(search_folder).rglob("*.json")]

	#output_csv = "gridsearch/7jul_gsr_17sep_all.csv"

	for c, json_file in enumerate(all_json_files):

		print(json_file)

		e_md = {}

		header_map = {"evla_gs": "best_y", "evlo_gs": "best_x", "evdp_gs":"best_z", "origin_time":"ref_timestamp", "misfit_gs": "sigma_ml", "cell_size": "cell_size", "cell_height": "cell_height", "evla_c": "best_y_c", "evlo_c": "best_x_c"}

		with open(json_file, 'r') as f:
			e_md = json.load(f)

		if "ID" not in e_md:
			e_id = json_file.split("/")[-1][:6] # not future proof but just fix next time lol
		else:
			e_id = e_md["ID"]

		df.at[c, "ID"] = e_id

		for h in header_map:
			try:
				df.at[c, h] = e_md[header_map[h]]
			except:
				pass

		for _sta in e_md["station_misfit"]:
			if "P" in e_md["station_misfit"][_sta]:
				mdf.at[_c, "ID"] = e_id
				mdf.at[_c, "station"] = _sta
				mdf.at[_c, "misfit"] = e_md["station_misfit"][_sta]["P"]
				mdf.at[_c, "phase"] = "P"
				_c += 1

			if "S" in e_md["station_misfit"][_sta]:
				mdf.at[_c, "ID"] = e_id
				mdf.at[_c, "station"] = _sta
				mdf.at[_c, "misfit"] = e_md["station_misfit"][_sta]["S"]
				mdf.at[_c, "phase"] = "S"
				_c += 1

	df.to_csv(output_csv, index = False)
	mdf.to_csv(misfit_csv, index = False)

def patch_gs(source_csv, output_csv):

	df = pd.read_csv(source_csv)

	#all_expected = [x for x in range(2639)]

	output_str = "ID,\n"
	check = df["ID"].tolist()

	for x in range(2639): # should make it dependent on the input list..... next time
		if x not in check:
			output_str += str(x) +"\n"

	with open(output_csv, 'w') as f:
		f.write(output_str)

def collate_misfits(source_folder, output_csv):

	search_folder = source_folder
	all_jsons = [str(p) for p in Path(search_folder).glob("*json")]
	df = pd.DataFrame(columns = ["ID", "station", "misfit", "phase"])
	c = 0
	for _jsonfile in all_jsons:
		with open(_jsonfile, 'r') as f:
			_md = json.load(f)
		#print(_md)

		for _sta in _md["station_misfit"]:
			if "P" in _md["station_misfit"][_sta]:
				df.at[c, "ID"] = _jsonfile.split("/")[-1][:6]
				df.at[c, "station"] = _sta
				df.at[c, "misfit"] = _md["station_misfit"][_sta]["P"]
				df.at[c, "phase"] = "P"
				c += 1
			if "S" in _md["station_misfit"][_sta]:
				df.at[c, "ID"] = _jsonfile.split("/")[-1][:6]
				df.at[c, "station"] = _sta
				df.at[c, "misfit"] = _md["station_misfit"][_sta]["S"]
				df.at[c, "phase"] = "S"
				c += 1

	df.to_csv(output_csv)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-sf","--search_folder")
	parser.add_argument("-o", "--output_csv")
	parser.add_argument("-m", "--misfit_csv")
	parser.add_argument("-scsv", "--source_csv")
	parser.add_argument("-p", action = "store_true")
	parser.add_argument("-c", action = "store_true")

	args = parser.parse_args()

	if args.p:
		patch_gs(args.source_csv, args.output_csv)
	else:
		check_json(args.search_folder, args.output_csv, args.misfit_csv)