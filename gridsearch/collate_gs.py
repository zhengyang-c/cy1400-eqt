import json
from pathlib import Path
import numpy as np
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def check_json():

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

def plot_hist():
	# want to know distribution of misfits but kinda hard if not on an event by event basis?

	# this is a secondary thing don't need to be done now
	# df = pd.read_csv("imported_figures/7jul_gsonly_13sep_all.csv")

	# depths = df["evdp_gs"].tolist()
	# misfits = df["misfit_gs"].tolist()

	# plt.hist(depths, bins = np.arange(0,41))
	# plt.show()
	
	# plt.yscale("log")
	# plt.hist(misfits, bins = np.arange(0,4,0.5))
	# plt.show()
	# 
	with open("imported_figures/jul7_phases_arrivaltimes.json") as f:
		phase_dict = json.load(f)

	#get distribution of no. of phases



	#df = pd.read_csv("gridsearch/13sep_gs_json/misfit_blacklist_7jul_13sep_1.0s.csv")

	# print(df)
	# c = 0
	# for event in phase_dict:
	# 	#print(event)
	# 	_df = df[df["ID"] == int(event)]

	# 	for sta in phase_dict[event]["data"].keys():
	# 		#print(sta)
	# 		_sdf = _df[_df["station"] == sta]

	# 		for index, row in _sdf.iterrows():
	# 			#print(row)
	# 			if row.phase in phase_dict[event]["data"][sta]:
	# 				#print("POP")
	# 				c += 1
	# 				phase_dict[event]["data"][sta].pop(row.phase)
	# 				phase_dict[event]["data"][sta].pop("station_"+row.phase)
	
	# c = 0
	# j = 0
	# df = pd.DataFrame(columns = ["ID", "phase", "station"])
	for e in phase_dict:
		for s in phase_dict[e]["data"]:

			if "S" in phase_dict[e]["data"][s]:
				phase_dict[e]["data"][s].pop("S")
				phase_dict[e]["data"][s].pop("station_S")


	# print(df)

	n_phases = []

	for e in phase_dict:
		n_phases.append(sum([len(phase_dict[e]["data"][sta].keys())/2 for sta in phase_dict[e]["data"]]))

	print(sum(n_phases))

	plt.hist(n_phases, bins = np.arange(0,np.max(n_phases)))
	plt.xlim(0,10)
	#plt.ylim(0,40)
	plt.show()

	# rearrange this into 

	# get new misfit distribution


	
# want to collate individual misfits by loading all the json files / collecting all the json files? so just zip them lol
#
def collate_misfits():

	search_folder = "gridsearch/13sep_gs_json/jsons"
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

	df.to_csv("gridsearch/13sep_gs_json/misfit_summary.csv")


def plot_misfits():

	df = pd.read_csv("gridsearch/13sep_gs_json/misfit_summary.csv")

	p_misfits = df[df["phase"] == "P"]["misfit"].tolist()
	s_misfits = df[df["phase"] == "S"]["misfit"].tolist()

	plt.xscale("log")
	plt.hist(p_misfits, bins = np.logspace(-3, 0.6), alpha = 0.5)	
	plt.hist(s_misfits, bins = np.logspace(-3, 0.6), alpha = 0.5)
	plt.show()


def generate_phase_exclude():
	# it'll be this massive json
	# organised by event --> station --> phase
	# i could just modify the existing phase.json
	# 
	
	#input_json = "real_postprocessing/remap_phase.json"

	# with open(input_json, 'r') as f:
	# 	phase_dict = json.load(f)

	df = pd.read_csv("gridsearch/13sep_gs_json/misfit_summary.csv")

	# p_misfits = df[df["phase"] == "P"]["misfit"].tolist()
	# s_misfits = df[df["phase"] == "S"]["misfit"].tolist()
	# 
	# 
	_df = df[df["misfit"] > 0.5]

	_df.to_csv("gridsearch/13sep_gs_json/misfit_blacklist_7jul_13sep_0.5s.csv", index = False)


	_df = df[df["misfit"] > 1.0]
	_df.to_csv("gridsearch/13sep_gs_json/misfit_blacklist_7jul_13sep_1.0s.csv", index = False)
	
	# just make an ignore list, load the csv file on the child worker side, 
	
	# loop through the df and edit the dictionary

	# then edit the searcher to ignore phases in the json given the flag

plot_hist()