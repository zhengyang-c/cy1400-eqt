import json
from pathlib import Path
import numpy as np
import argparse
import pandas as pd

def check_json():

	# want to know how many done / failed (well formed json)

	# want to collate a CSV file with most of the JSON parameters

	search_folder = "gridsearch/7jul_gsr_afterREAL"

	pd_columns = ["ID", "evla_gs", "evlo_gs", "evdp_gs", "origin_time", "misfit_gs", "misfit_combined", "cell_size", "cell_height"]
	df = pd.DataFrame(columns = pd_columns)

	all_json_files = [str(p) for p in Path(search_folder).rglob("*.json")]

	output_csv = "gridsearch/7jul_gsonly_13sep.csv"



	for c, json_file in enumerate(all_json_files):

		e_md = {}

		header_map = {"evla_gs": "best_y", "evlo_gs": "best_x", "evdp_gs":"best_z", "origin_time":"ref_timestamp", "misfit_gs": "sigma_ml", "cell_size": "cell_size", "cell_height": "cell_height"}

		with open(json_file, 'r') as f:
			e_md = json.load(f)

		if "ID" not in e_md:
			e_id = json_file.split("/")[-1][:6] # not future proof but just fix next time lol
		else:
			e_id = e_md["ID"]

		df.at[c, "ID"] = e_id

		for h in header_map:
			df.at[c, h] = e_md[header_map[h]]
	df.to_csv(output_csv, index = False)
	
def patch_gs():

	source_csv = "imported_figures/7jul_gsonly_13sep.csv"

	df = pd.read_csv(source_csv)

	#all_expected = [x for x in range(2639)]

	output_str = "ID,\n"
	check = df["ID"].tolist()

	for x in range(2639): # should make it dependent on the input list..... next time
		if x not in check:
			output_str += str(x) +"\n"

	with open("imported_figures/gs_13sep_patch.csv", 'w') as f:
		f.write(output_str)

def check_misfits():
	# want to know distribution of misfits but kinda hard if not on an event by event basis?

	# this is a secondary thing don't need to be done now
	pass

#check_json()
patch_gs()