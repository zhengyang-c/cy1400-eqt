"""
goals
1. parse the hypo file, into a json format (not difficult)
2. parse the output file, 

use `parse_full_output` to get different models and their associated RMS
plot distribution of outputs, plot model and colour the best model
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd
import argparse as ap
import fortranformat as ff
from pathlib import Path
import os

def main(search_folder, output_csv, do_after = True, output_json = ""):

	velest_hypo = {}

	# hypo_file = "velest/test2/test.hypo"
	# output_file = "velest/test2/test.output"
	# id_file = "velest/test2/test.id"
	
	file_list = os.listdir(search_folder)
	output_location_file = os.path.join(search_folder, [x for x in file_list if ".hypo" in x][0])
	input_location_file = os.path.join(search_folder, [x for x in file_list if ".events" in x][0])
	id_file = os.path.join(search_folder, [x for x in file_list if ".id" in x][0])

	df = pd.DataFrame()

	def parse_header(x):
		
		metadata = {
			"year":int(x[0:2].strip()),
			"month":int(x[2:4].strip()),
			"day":int(x[4:6].strip()),
			"hour":int(x[7:9].strip()),
			"minute":int(x[9:11].strip()),
			"second":float(x[12:17].strip()),
			"lat":float(x[18:25].strip()),
			"lon":float(x[27:35].strip()),
			"depth":float(x[36:43].strip()),
			"mag": float(x[44:50].strip()),
		}

		# catch for input hypo files
		try:
			metadata["un1"] = float(x[50:57].strip())
			metadata["res"] =  float(x[58:67].strip())
		except:
			pass

		return metadata

	def parse_phases(x):

		_phases = []

		while len(x) > 12:
			_slice = x[:12]
			if len(_slice.strip()) == 0:
				break
			_sta = _slice[0:4]
			_phase = _slice[4]
			_dt = _slice[8:12]
			_phases.append((_sta, _phase, float(_dt.strip())))
			x = x[12:]

		return _phases


	with open(id_file, "r") as f:
		id_list = f.read()
		id_list = [x for x in id_list.split("\n") if len(x) > 0]

	
	header_switch = True
	start = True
	event_counter = 0
	phase_buffer = []

	if do_after:
		hypo_file = output_location_file 
	else:
		hypo_file = input_location_file 

	with open(hypo_file, "r") as f:
		for line in f:
			if len(line) < 2 and not start:
				print(event_counter)
				print(len(id_list))
				header_switch = True
				# do stuff here to save events
				target_event = id_list[event_counter]
				velest_hypo[target_event] = header
				velest_hypo[target_event]["data"] = phase_buffer
				
				print(event_counter)
				phase_buffer = []
				event_counter += 1
				continue
			if header_switch: 
				header = parse_header(line)
				header_switch = False
				continue
			if not header_switch:
				phase_buffer.extend(parse_phases(line))

			start = False


	# mess around with the phase_buffer

	for event in velest_hypo:
		phase_list = velest_hypo[event]["data"]

		inject = {}

		for p in phase_list:
			# station, phase, time
			print(p)
			if p[0] not in inject:
				inject[p[0]] = {
					p[1]: p[2]
				}
			else:
				inject[p[0]][p[1]] = p[2]

		velest_hypo[event]["data"] = inject

	for c, event in enumerate(velest_hypo):
		df.at[c, "ID"] = int(event)
		df.at[c,"LAT"] = velest_hypo[event]["lat"]
		df.at[c,"LON"] = velest_hypo[event]["lon"]
		df.at[c,"DEPTH"] = velest_hypo[event]["depth"]

		# the origin time information is kinda.. optional... and not needed

	df.to_csv(output_csv, index = False)

	
	if output_json:
		with open(output_json, "w") as f:
			json.dump(velest_hypo, f, indent = 4)

def parse_full_output(file_path):

	# file_path = "imported_figures/all_rereal_1/all_rereal.output"

	with open(file_path, "r") as f:
		data_dump = [x for x in f.read().split("\n") if len(x)]

	def get_vel_model(data_dump):

		# find instances of "Velocity model"

		target_indices = [x for x in range(len(data_dump)) if "Velocity model" in data_dump[x]]
		for x in target_indices:
			print(data_dump[x])

		# the target will be to start looking from the last two indices 

		df = pd.DataFrame()

		def parser(s_i, h):
			s_i += 1
			while 1:
				if "Calculation" in data_dump[s_i]:
					break
				_data = [x for x in data_dump[s_i].split(" ") if len(x)]

				df.at[float(_data[2]), h] = float(_data[0])

				s_i += 1
		parser(target_indices[-2], "v_p")
		parser(target_indices[-1], "v_s")

		df.index.name = "depth"
		df = df.reset_index(level=0)
		print(df)
		return df
	
	# read_state: -1, not begin yet
	# read_state: 1, header file
	# read_state: 2, event line
	# read_state: 3, not the first station


	def parse_one_phase(x, i_c):

		d = {
			"station":x[0].replace("Z", ""),
			"phase":x[1].upper(),
			"weight": float(x[2]),
			"residual": float(x[3]),
			"traveltime": float(x[4]),
			"delta": float(x[5]),
			"v_ID": i_c,
		}

		return d

	def update_df(df, phase_info):
		target_index = len(df)
		for h in phase_info:
			df.at[target_index, h] = phase_info[h]
		return df

	def get_station_residuals(data_dump):
		s_i = [x for x in range(len(data_dump)) if "~~~ output final station residuals" in data_dump[x]][0]
		s = -1
		i_c = 0 # internal index counter, to sync with the id list 

		p_df = pd.DataFrame()

		while True:
			print(data_dump[s_i])
			"""
			some event lines have negative residuals s.t. there is no space separating the residual and the weight
			this means that i should use fortran formatter or something (?)

			"""			
			if "sta ph" in data_dump[s_i]:
				if s == -1:
					s = 2
				elif s == 2:
					s = -1
			elif s == 2:
				if 'Station residuals' in data_dump[s_i]:
					s = -1
					print("stop reading")
					i_c += 1
				else:
					print("do read stuff")
					_data = [x for x in data_dump[s_i].split(" ") if len(x)]

					p_df = update_df(p_df, parse_one_phase(_data[0:6], i_c))
					if (len(_data)) == 12:
						p_df = update_df(p_df, parse_one_phase(_data[6:12], i_c))

				# do read stuff
				pass
			elif "station statistics" in data_dump[s_i]:
				break
			else:
				pass
			s_i += 1
		
		print(p_df)
		# p_df.to_csv("csi/velest_test.csv", index = False)

	def get_overall_residual(data_dump):
		target_indices = []
		for c, line in enumerate(data_dump):
			if "RMS RESIDUAL" in  line:
				target_indices.append(c)
		
		target_line = data_dump[target_indices[-1]]

		residual = float(target_line.split("=")[-1].strip())
		return residual
	
	def get_iterations(data_dump):
		target_indices = []
		for c, line in enumerate(data_dump):
			if "ITERATION no" in line:
				target_indices.append(c)
		
		n_iter = [x.strip() for x in data_dump[target_indices[-1]].split(" ")][-1]

		return n_iter


	vel_df = get_vel_model(data_dump)
	res = get_overall_residual(data_dump)
	n_iter = get_iterations(data_dump)


	return vel_df, res, n_iter
	# get_station_residuals(data_dump)


def collect_input_models(search_folder, output_csv):
	target_files = [str(p) for p in Path(search_folder).rglob("*.model")]

	df_list = []

	for file in target_files:
		df = pd.DataFrame()

		p_flag = False
		s_flag = False

		with open(file, "r") as f:
			data = f.read().split("\n")

		data = [[y for y in x.split(" ") if len(y)] for x in data]

		for x in data:
			if "P" in x:
				p_flag = True
			elif "S" in x:
				p_flag = False
				s_flag = True

			if p_flag:
				try:
					df.at[float(x[1]), "v_p"] = float(x[0])
					df.at[float(x[1]), "source"] = file
				except:
					pass
			if s_flag:
				try:
					df.at[float(x[1]), "v_s"] = float(x[0])
				except:
					pass
			
		df_list.append(df)

	odf = pd.concat(df_list)
	odf.index.name = "depth"

	odf.to_csv(output_csv)



def collect_output_models(search_folder, output_csv):
	# search_folder = "imported_figures/velest_test_output"
	target_files = [str(p) for p in Path(search_folder).rglob("*.output")]

	models = []
	sources = []
	rms = [] 	

	for x in target_files:
		with open(x, 'r') as f:
			try:
				_model, _rms, _n_iter = parse_full_output(x)
				_model["source"] = x
				_model["rms"] = _rms
				_model["n_iter"] = _n_iter
				models.append(_model)
				sources.append(x)
				rms.append(_rms)
			except:
				continue

	best = np.argmin(rms)
	print("best residual: {}".format(rms[best]))
	print("best source: {}".format(sources[best]))

	df = pd.concat(models)

	df.to_csv(output_csv, index = False)

	# for y in models:
	# 	_x, _y = get_xy(y)
	# 	plt.plot(_x, _y, color = "lightgrey", linestyle = "solid")

	# _x, _y = get_xy(models[best])
	
	# plt.plot(_x, _y, color = "red", linestyle = "solid")

	# plt.tick_params(axis='x', which='both', labeltop='on', labelbottom='on')
	# plt.legend()
	# plt.xlabel("P velocity [km/s]")
	# plt.ylabel("Depth [km]")
	# plt.ylim(0,40)
	# plt.gca().invert_yaxis()

	# plt.show()

	# plot everything

	# then plot the best one again in a different colour


	
# ignore the residuals for now, velocity model is more useful for interpretation later (?)
# besides the velocity model is suspect because of some of the residuals


if __name__ == "__main__":
	a = ap.ArgumentParser()
	a.add_argument("search_folder")
	a.add_argument("output_file")
	a.add_argument("-bef", "--before", action = "store_true")
	a.add_argument("-aft", "--after", action = "store_true")
	a.add_argument("--output_phases", help = "Path to output json file")
	a.add_argument("-im", "--input_model", action = "store_true")
	a.add_argument("-om", "--output_model", action = "store_true")

	args = a.parse_args()

	if args.before ^ args.after:
		main(args.search_folder, args.output_file, do_after = args.after, output_json = args.output_phases)
	elif args.input_model ^ args.output_model:
		if args.input_model:
			collect_input_models(args.search_folder, args.output_file)
		else:
			collect_output_models(args.search_folder, args.output_file)