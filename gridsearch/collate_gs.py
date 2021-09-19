import json
from pathlib import Path
import numpy as np
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def check_json(search_folder, output_csv):

	# want to know how many done / failed (well formed json)

	# want to collate a CSV file with most of the JSON parameters

	search_folder = "gridsearch/7jul_gsr_afterREAL_deeperredo"

	pd_columns = ["ID", "evla_gs", "evlo_gs", "evdp_gs", "origin_time", "misfit_gs", "misfit_combined", "cell_size", "cell_height", "evla_c", "evlo_c", ]
	df = pd.DataFrame(columns = pd_columns)

	all_json_files = [str(p) for p in Path(search_folder).rglob("*.json")]

	output_csv = "gridsearch/7jul_gsr_17sep_all.csv"

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
	df.to_csv(output_csv, index = False)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("search_folder")
	parser.add_argument("output_csv")

	args = parser.parse_args()

	check_json(args.search_folder, args.output_csv)