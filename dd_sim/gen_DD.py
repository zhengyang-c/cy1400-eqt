import argparse
import os
import json
import numpy as np
import pandas as pd
import random
import fortranformat as ff
import datetime
import shutil

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

def main(job_name, n_bootstrap, bootstrap_fraction = 0.9, json_file = "", vpvs_ratio = 1.73, vel_model = "", dd_obsct = 20):

	if json_file == "":
		input_json_phase_file = "/home/zchoong001/cy1400/cy1400-eqt/real_postprocessing/rereal/patch_all_rereal_events.json"
	else:
		input_json_phase_file = json_file

	source_station_file = "/home/zchoong001/cy1400/cy1400-eqt/real_postprocessing/rereal/station.dat"

	remap_file = "../4aug_station_remap.txt"

	paths = {
		"pbs_folder": "/home/zchoong001/cy1400/cy1400-eqt/pbs/runtime_scripts",
		"pbs_file_folder":"/home/zchoong001/cy1400/cy1400-eqt/pbs",
		"hypodd":"/home/zchoong001/HYPODD/src/hypoDD/hypoDD",
		"ph2dt":"/home/zchoong001/HYPODD/src/ph2dt/ph2dt",
		"job_name": job_name,
		"ph2dt_inp": "ph2dt.inp",
		"hypodd_inp": "hypoDD.inp",
		"input_station_file": "station.dat",
		"phase_file_name": "phase.dat",
	}

	with open(input_json_phase_file, "r") as f:
		phases = json.load(f)

	# check_mapping(phases, remap_file)

	generate_folder_structure(n_bootstrap, paths)
	generate_runtime_scripts(n_bootstrap, paths)
	generate_runtime_files(n_bootstrap, paths, phases, source_station_file, bootstrap_fraction = bootstrap_fraction, vpvs_ratio=1.73, vel_model = vel_model, dd_obsct = dd_obsct)

	pbs_writer(n_bootstrap, job_name, paths, walltime_hours=5)


def generate_runtime_files(n_bootstrap, paths, phases, station_file, bootstrap_fraction = 0.9, vpvs_ratio = 1.73, vel_model = "", dd_obsct = 20):

	for n in range(n_bootstrap):
		target_folder = os.path.join(paths["pbs_folder"], paths["job_name"])
		target_file_ph = os.path.join(target_folder, str(n), paths["ph2dt_inp"])
		target_file_dd = os.path.join(target_folder, str(n), paths["hypodd_inp"])
		target_file_pha = os.path.join(target_folder, str(n), paths["phase_file_name"])
		target_file_sta = os.path.join(target_folder, str(n), paths["input_station_file"])


		generate_ph2dt_inp(
			paths["input_station_file"],
			paths["phase_file_name"],
			target_file_ph)

		generate_dd_inp(paths["input_station_file"], target_file_dd, vpvs_ratio = vpvs_ratio, vel_model = vel_model, dd_obsct = dd_obsct)

		generate_phase_file(phases, bootstrap_fraction, target_file_pha)

		shutil.copy(station_file, target_file_sta)

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


def generate_folder_structure(n_bootstrap, paths):
	target_folder = os.path.join(paths["pbs_folder"], paths["job_name"])

	if not os.path.exists(target_folder):
		os.makedirs(target_folder)
	for n in range(n_bootstrap):
		if not os.path.exists(os.path.join(target_folder, str(n))):
			os.makedirs(os.path.join(target_folder, str(n)))


def create_map(input_file):
	station_map = {}
	_data = []
	with open(input_file, 'r') as f:
		for c, line in enumerate(f):
			if line[0] == "#":
				_year, _month = line[1:].strip().split(" ") # this would fail in an input error 
				y_m = "{}_{}".format(_year, _month) # year month	
				station_map[y_m] = {}
			else:
				try:
					k, v = [x.strip() for x in line.split(":")] # only two values (1:2)
					station_map[y_m][k] = v
				except:
					print("Might be EOF, not parsing: {}".format(line))
	return station_map

def check_mapping(phase_dict, remap_file):

	station_map = create_map(remap_file)
	event_list = list(phase_dict.keys())

	for event in event_list:

		if ":" not in phase_dict[event]["timestamp"]:
			try:
				ts = datetime.datetime.strptime(phase_dict[event]["timestamp"], "%Y-%m-%d-%H-%M-%S.%f")
			except:
				ts = datetime.datetime.strptime(phase_dict[event]["timestamp"], "%Y-%m-%d-%H-%M-%S")
		else:
			try:
				ts = datetime.datetime.strptime(phase_dict[event]["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
			except:
				ts = datetime.datetime.strptime(phase_dict[event]["timestamp"], "%Y-%m-%d %H:%M:%S")
		y_m = datetime.datetime.strftime(ts, "%Y_%m")

		if not y_m in station_map:
			continue

		for station in list(phase_dict[event]["data"].keys()):
			if station in station_map[y_m]:
				assert False
				# new_station = station_map[y_m][station]
				# phase_dict[event]["data"][new_station] = phase_dict[event]["data"].pop(station)



def generate_phase_file(phase_json, bootstrap_factor, output_file):

	event_ids = list(phase_json.keys())
	if bootstrap_factor == 1.0:
		bootstrap = event_ids
	else:
		n_events = int( bootstrap_factor * len(event_ids))

		bootstrap = random.sample(event_ids, n_events )
		print(len(bootstrap))

	output_str = ""

	for e in bootstrap:
		data = phase_json[e]
		g = ff.FortranRecordWriter('("# ",i4,1x,i2.2,1x,i2.2,1x,i2.2,1x,i2.2,1x,f6.3,1x,f7.4,1x,f8.4,1x,f7.3,1x," 0.00 0 0 0",1x,a11)')
		header_str = (g.write([
			int(data["year"]),
			int(data["month"]),
			int(data["day"]),
			int(data["hour"]),
			int(data["min"]),
			float(data["sec"]),
			float(data["lat_guess"]),
			float(data["lon_guess"]),
			float(data["dep_guess"]),
			e
		]))

		output_str += header_str + "\n"

		for sta in data["data"]:
			p = ff.FortranRecordWriter('(A4,1x,f7.3,1x,i1,1x,a1)')
			if "P" in data["data"][sta]:
				output_str += (p.write([sta, float(data["data"][sta]["P"]), 1, "P"])) + "\n"
			if "S" in data["data"][sta]:
				output_str += (p.write([sta, float(data["data"][sta]["S"]), 1, "S"])) + "\n"


	with open(output_file, "w") as f:
		f.write(output_str)


	# use fortran formatter?

def generate_ph2dt_inp(station_file, phase_file, output_file, args = None):
	if not args:
		args = {
			"MINWGHT":0,
			"MAXDIST":300,
			"MAXSEP":10,
			"MAXNGH":40,
			"MINLNK":8,
			"MINOBS":8,
			"MAXOBS":40,
		}
	
	output_str = "{}\n{}\n{} {} {} {} {} {} {}".format(station_file, phase_file,*list(args.values())
	)

	with open(output_file, "w") as f:
		f.write(output_str)

	print(output_str)
	


def generate_dd_inp(station_file, output_file, vpvs_ratio = 1.73, vel_model = "", dd_obsct = 20, args = None):

	if not args:
		args = {
			"OBSCT": dd_obsct,
			"NITER": 4,
			"WEIGHT": "4 -9 -9 -9 -9 1 1 -9 -9 20\n4 -9 -9 -9 -9 1 1 5 10 20\n",
			"DAMP": 20,
			"NLAY":9,
			"RATIO": vpvs_ratio,
			"TOP": [0.0, 5.0, 10.0, 20.0, 30.0,40.0,50.0,70.0,90.0],
			"VEL": [5.2, 5.5, 6.0, 6.6, 7.6, 8.0, 8.1, 8.2, 8.2],
		}

	if vel_model:
		df = pd.read_csv(vel_model) 
		df = df.iloc[1:, :] # exclude the top negative layer
		top = df["depth"].tolist()
		vel = df["v_p"].tolist()

		args["VEL"] = vel
		args["TOP"] = top
		args["NLAY"] = len(top)


	output_str = "\ndt.ct\nevent.sel\n{}\nhypoDD.loc\nhypoDD.reloc\nhypoDD.sta\nhypoDD.res\nhypoDD.src\n2 3 200\n0 {}\n2 2 2\n{}{} {}\n{}{}0\n".format(
		station_file,
		args["OBSCT"],
		args["WEIGHT"],
		args["NLAY"],
		args["RATIO"],
		" ".join(["{:.2f}".format(x) for x in args["TOP"]]) + "\n", 
		" ".join(["{:.2f}".format(x) for x in args["VEL"]]) + "\n", 
	)

	print(output_str)
	with open(output_file, "w") as f:
		f.write(output_str)



"""
1. check station mappings (reuse code)
2. load phase.dat into a dictionary, or just load the generated json
3. obtain a representation of the ph2dt.inp and hypoDD.inp files s.t. you can tune for the no. of events


3. generate N output folders with 90% of the events, selected randomly
4. run this on gekko so it doesn't take two billion years + add multiprocessing (?) generate PBS? quite a lot of machinery required
5. but given that this structure will be reused it's probably worth doing


"""

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("job_name")
	ap.add_argument("n_bootstrap", type = int)
	ap.add_argument("-f", "--bootstrap_fraction", type = float, default = 0.9)
	ap.add_argument("-j", "--json_file")
	ap.add_argument("-v", "--vel_model", help = "Path to velocity model file")
	ap.add_argument("-vpvs", "--vpvs_ratio", type = float)
	ap.add_argument("-obsct", "--obsct", type = int, help = "set obsct directly", default = 20)

	args = ap.parse_args()

	main(args.job_name, args.n_bootstrap, bootstrap_fraction = args.bootstrap_fraction, json_file = args.json_file, vel_model = args.vel_model, vpvs_ratio = args.vpvs_ratio, dd_obsct = args.obsct)