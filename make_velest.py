"""
I too, enjoy reinventing the wheel

PURPOSE
-------

Generate MOD, STA, and CNV file for use in VELEST.

INPUT
-----

STATION LOCATION FILE:

tab separated,
station_name | lon | lat | elv

earthquake event file:
a CSV file with the needed columns

model file:


"""
import os
import argparse
import pandas as pd
from utils import parse_station_info
import fortranformat as ff
import shutil
import json
import random


def main(job_name, n_bootstrap, **kwargs):
	paths = {
		"pbs_folder": "/home/zchoong001/cy1400/cy1400-eqt/pbs/runtime_scripts",
		"pbs_file_folder":"/home/zchoong001/cy1400/cy1400-eqt/pbs",
		"job_name": job_name,
	}
	# create all the needed folders, generate runtime scripts

	# then generate the work files

	# then generate the .pbs file

	for k in kwargs:
		paths[k] = kwargs[k]

def generate_runtime_scripts(n_bootstrap, paths):

	for n in range(n_bootstrap):

		target_folder = os.path.join(paths["pbs_folder"], paths["job_name"], str(n))
		target_file = os.path.join(target_folder,  "run.sh")

		with open(target_file, "w") as f:
			f.write("cd {}\n{} {}\n{} {}".format(
				target_folder,
				paths["ph2dt"],
				paths["ph2dt_inp"],
				paths["hypodd"], 
				paths["hypodd_inp"], 
			))

		os.chmod(target_file, 0o775)
def pbs_writer(n_nodes, job_name, paths, n_cores = 1, walltime_hours = 80):

	paths["pbs_folder"] = paths["pbs_file_folder"]
	output_pbs = os.path.join(paths["pbs_folder"], job_name +".pbs")

	project_code = 'eos_shjwei'

	with open(output_pbs, "w") as f:
		if n_nodes == 1:
			pass
		else:
			f.write("#PBS -J 0-{:d}\n".format(n_nodes - 1))

		f.write("#PBS -N {}\n#PBS -P {}\n#PBS -q q32\n#PBS -l select={}:ncpus={}:mpiprocs=32:mem=16gb -l walltime={}:00:00\n".format(job_name, project_code, n_nodes, n_cores, walltime_hours))
		f.write("#PBS -e log/pbs/{0}/error.log \n#PBS -o log/pbs/{0}/output.log\n".format(job_name))

		if n_nodes == 1:
			f.write("{1}/runtime_scripts/{0}/0/run.sh\n".format(job_name, paths["pbs_folder"]))
		else:
			f.write("{1}/runtime_scripts/{0}/${{PBS_ARRAY_INDEX}}/run.sh\n".format(job_name, paths["pbs_folder"]))

def generate_all(
	output_folder = "",
	output_root = "",
	json_file = "",
	station_file = "",
	velest_source = "",
	bootstrap_fraction = 0.1,
	mag_file = "",
	n_repeats = 3, 
	split = 1,
):


	# do the station file first since it's easiest
	station_info = parse_station_info(station_file)
	# phase_file = "real_postprocessing/rereal_all/all_rereal_events.pha"
	# mag_file = "imported_figures/all_rereal_mags.csv"

	for key in list(station_info.keys()):
		if key == "A10":
			_key = "TG03"
		else:
			_key = key
		if len(_key) == 3:
			station_info[_key + "Z"] = station_info.pop(key)

	# this is because VELEST is written with station names of 4 characters, so just append a Z at the back 

	# output_folder = "velest"	
	# output_root = "master_real_test"

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	
	if velest_source:
		try:
			shutil.copy(velest_source, output_folder)
		except:
			print("Unable to copy VELEST file over, skipping...")


	output_path = os.path.join(output_folder, output_root)
	with open(json_file, "r") as f:
		phase_json = json.load(f)

	event_ids = list(phase_json.keys())


	## FILTER

	for e in event_ids:
		if float(phase_json[e]["lon_guess"]) < 95.2 or float(phase_json[e]["lat_guess"]) < 4.4 or float(phase_json[e]["lat_guess"]) > 5.4:
			phase_json.pop(e)

	# n_events = len(event_ids)

	if split == 1:
		event_ids = [x for x in sorted(list(phase_json.keys())) if int(x) < 7000]
	elif split == 2:
		event_ids = [x for x in sorted(list(phase_json.keys())) if (int(x) >= 7000 and int(x) < 14000)]
	elif split == 3:
		event_ids = [x for x in sorted(list(phase_json.keys())) if (int(x) >= 14000)]
	#	n_events = int(bootstrap_fraction * len(event_ids))

	n_events = len(event_ids)

	outputs = {
		"station_file": output_path + ".sta",
		"event_file": output_path + ".events",
		"model_file": output_path + ".model",
		"control_file": os.path.join(output_folder, "velest.cmn"),
		"id_list": output_path + ".id"
	}

	params = {
		"station":output_root + ".sta",
		"event":output_root + ".events",
		"model":output_root + ".model",
		"output": output_root + ".output",
		"bootstrap_fraction": bootstrap_fraction,
		"station_corr": output_root + ".stacorr",
		"hypo_output": output_root + ".hypo",
		"residual": output_root + ".res",
		"n_events": n_events,
	}

	def write_station(station_info):
		icc = {}
		c = 0
		for station in station_info:
			if station != "TA19":
				icc[station] = c
				c += 1
		icc["TA19"] = len(station_info)

		h = ff.FortranRecordWriter('(a4,f7.4,a1,1x,f8.4,a1,1x,i4,1x,i1,1x,i3,1x,f5.2,2x,f5.2,3x,i1)')

		sta_str = "(a4,f7.4,a1,1x,f8.4,a1,1x,i4,1x,i1,1x,i3,1x,f5.2,2x,f5.2)\n"
		for station in station_info:

			_str = (h.write([station,station_info[station]["lat"],"N", station_info[station]["lon"], "E", int(station_info[station]["elv"]), 1, icc[station], 0, 0, 1]))

			sta_str += _str + "\n"
			# sta_str += "{}{:.5f}N {:.5f}E {} 1 {} 0.00 0.00 1\n".format(
			# 	station.ljust(4),
			# 	station_info[station]["lat"],
			# 	station_info[station]["lon"],
			# 	int(station_info[station]["elv"]),
			# 	icc[station]
			# )

		sta_str += "\n"

		return sta_str


	# need to determine the ICC number, which probably doesn't matter so much (?)

	# TA19 has the most detections, so it should have the highest ICC number
	# assigning the same ICC numbers: computational efficiency not that? important? since VELEST isn't that slow
	# i.e. can give TA19 the highest ICC number first

	# then do the model file

	def write_model():
		initial_p_model = [(-3, 5.2), (0, 5.2), (2.5, 5.35), (5, 5.5), (7.5, 5.75), (10, 6), (15, 6.3), (20, 6.6), (30, 7.6), (40, 8), (50, 8.1), (70, 8.2), (90, 8.2)]

		metadata = "test"
		mod_str = "{}\n{}        vel,depth,vdamp,phase (f5.2,5x,f7.2,2x,f7.3,3x,a1)\n".format(metadata, len(initial_p_model))

		h = ff.FortranRecordWriter('(f5.2,5x,f7.2,2x,f7.3,3x,a1)')

		vpvs = 1.73

		c = 1
		for i in initial_p_model:
			if c:
				# mod_str += "{:.2f}     {:.2f}  001.00   P-VELOCITY MODEL\n".format(i[1], i[0])
				temp_str = h.write([i[1], i[0], 1, "P"]) + "\n"
				temp_str = temp_str.replace("1.000", "001.00")
				mod_str += temp_str
				c = 0
			else:
				mod_str += h.write([i[1], i[0], 1.0]) + "\n"
		c = 1
		mod_str += "{}\n".format(len(initial_p_model))
		for i in initial_p_model:
			if c:
				temp_str = h.write([i[1]/1.73, i[0], 1, "S"]) + "\n"
				temp_str = temp_str.replace("1.000", "001.00")
				mod_str += temp_str
				c = 0
			else:
				mod_str += h.write([i[1]/1.73, i[0], 1.0]) + "\n"

		return mod_str


	def write_control_file(params):
		ctrl_str = ""

		# lat lons

		ctrl_str += "test\n4.8 96 1 0.000 0 0.00 0\n"
		ctrl_str += "{0} 0 0.0\n0 0\n100 0 0.0 0.20 5.00 0\n2 0.8 1.73 1\n0.01 0.01 0.01 1.0 0.01\n0 0 0 1 0\n1 1 1 0\n0 0 0 0 0 0 0\n0.010 {8} 1\n{1}\n{2}\n\n\n\n\n\n{3}\n\n{4}\n\n{5}\n{6}\n\n\n\n\n\n\n\n{7}".format(
			params["n_events"],
			params["model"],
			params["station"],
			params["event"],
			params["output"],
			params["hypo_output"],
			params["station_corr"],
			params["residual"],
			n_repeats,
		)
		print(ctrl_str)
		return ctrl_str


	def write_event(json_file):

		# record down lat and lons, then compute the centroid, and compute the distances from the centroid
		# plot a histogram
		# then decide whether you want to pre-filter or to filter on the fly
		# probably want to pre-filter the events you feed in

		# bootstrap = random.sample(event_ids, n_events)
		bootstrap = event_ids
		# event file....

		# just modify the first line

		# seems like the 6 phases per line is mandatory

		# (3i2.2,1x,2i2.2,1x,f5.2,1x,f7.4,a1,1x,f8.4,a1,f7.2,f7.2,i2...)
		h = ff.FortranRecordWriter('(3i2.2,1x,2i2.2,1x,f5.2,1x,f7.4,a1,1x,f8.4,a1,f7.2,f7.2,i2)')

		g = ff.FortranRecordWriter('(a4,a1,i1,f6.2)')
		out_str = ""
		
		start_flag = True

		for e in bootstrap:
			event_buffer = []
			data = phase_json[e]
			header_str = h.write([
				int(data["year"][2:4]),
				int(data["month"]),
				int(data["day"]),
				int(data["hour"]),
				int(data["min"]),
				float(data["sec"]),
				float(data["lat_guess"]),
				"N",
				float(data["lon_guess"]),
				"E",
				float(data["dep_guess"]),
				0.00,
				1
			])
			out_str += header_str + "\n"
			for sta in data["data"]:
				if len(sta) == 3:
					_sta = sta + "Z"
				else:
					_sta = sta

				if "P" in data["data"][sta]:
					event_buffer.append(
						g.write(
							[_sta, "P", 1, float(data["data"][sta]["P"])]))

				if "S" in data["data"][sta]:
					event_buffer.append(
						g.write(
							[_sta, "S", 1, float(data["data"][sta]["S"])]))

			cut_off = 150
			if len(event_buffer) > cut_off:
				event_buffer = event_buffer[:cut_off]

			c = 0
			_c = len(event_buffer)
			while len(event_buffer) > 0:
				c += 1
				out_str += event_buffer.pop()

				if c == 6:
					out_str += "\n"
					c = 0
			
			if (_c % 6):
				out_str += " " * 12 * (6 - (_c % 6))

			out_str += "\n"

			if out_str[-2:] != "\n\n":
				out_str += "\n"
		
		return out_str, bootstrap

	sta_str = write_station(station_info)
	mod_str = write_model()
	out_str, bootstrap_list = write_event(json_file)
	ctrl_str = write_control_file(params)

	with open(outputs["station_file"], "w") as f:
		f.write(sta_str)
	with open(outputs["model_file"], "w") as f:
		f.write(mod_str)
	with open(outputs["event_file"], "w") as f:
		f.write(out_str)
	with open(outputs["id_list"], "w") as f:
		f.write("\n".join(bootstrap_list))
	
	with open(outputs["control_file"], "w") as f:
		f.write(ctrl_str)
	

if __name__ == "__main__":

	ap = argparse.ArgumentParser()

	ap.add_argument("-o", "--output_folder")
	ap.add_argument("-n", "--file_root")
	ap.add_argument("-j", "--json_file", help = "phase data kept in json format")
	ap.add_argument("-sta", "--station_file", help = "source station file in sta lon lat format")
	ap.add_argument("-m", "--mag_file", default = "", help = "optional, writes mag = 0 if you leave this blank")
	ap.add_argument("-v", "--velest", help = "location of VELEST binary")
	ap.add_argument("-f", "--bootstrap_fraction", type = float, default = 0.9 )
	ap.add_argument("-nr", "--n_repeats", help = "no. of iterations", default = 3)
	ap.add_argument('-s', "--split")
	args = ap.parse_args()
	generate_all(output_folder = args.output_folder, output_root = args.file_root, json_file = args.json_file, station_file = args.station_file, mag_file = args.mag_file, velest_source = args.velest, bootstrap_fraction = args.bootstrap_fraction, n_repeats = args.n_repeats, split = args.split)

# python make_velest.py -o velest/test2/ -n test -j gridsearch/rereal_patch_negative.json -sta csi/new_station_info_elv.dat -v velest/velest -f 0.1