import time
import numpy as np
import argparse
import itertools
import os
from subprocess import check_output
import shutil


def generate_job(job_name,
real_path = "",
station_file_path = "",
tt_path = "",
pick_dir_path = "",
day_list_path = "",
pbs_folder = "",
output_folder = "",
do_parallel = False,
n_workers = 0,
):

	# will have to construct the function call from scratch

	# REAL is called for every year/month/day

	# expected input: run REAL on file list

	# the default params are by definition opioniated

	if not n_workers:
		n_workers = 16

	default_params = {
		"lat_centre": 4.75,
		# -R
		"gridsearch_horizontal_range_deg": 2 ,
		"gridsearch_vertical_range_km": 60,
		"gridsearch_horizontal_cellsize_deg" : 0.01,
		"gridsearch_vertical_cellsize_km" : 5,

		"minimum_event_time_gap_seconds" : 3,

		"station_gap_deg":300,
		"station-event_greatcircle_dist_deg": 2,
		# by default, the station location recording the initiating phase is used 
		"gridsearch_centre_lat": None, 
		"gridsearch_centre_lon": None,

		# -G optional, not needed if homogenous model is assumed
		"traveltime_horizontal_range_deg": 2.4, 
		"traveltime_vertical_range_km": 35,
		"traveltime_horizontal_cellsize_deg": 0.02,
		"traveltime_vertical_cellsize_km": 1,
		
		# -V

		"average_p_velocity_kms": 6.2,
		"average_s_velocity_kms": 3.3,

		# optional if stations are at 0 elevation
		"consider_station_elevation": 0, 
		"shallow_p_velocity_kms": None,
		"shallow_s_velocity_kms": None,
	

		# -S
		"n_p_picks": 3,
		"n_s_picks": 3,
		"n_total_picks": 6, # e.g. you could specify 0/0/4 for any combination of P and S
		"n_both_ps_picks": 3,
		"stdev_residual_threshold_seconds": 0.5,
		# use in case P picks are mixed up with S. set to 0 to turn off
		"p-s_minimum_separation_seconds": 0, 

		# higher --> larger error window for possible p arrival i.e. velocity model more uncertain
		# trade off with grid size. 
		"arrival_time_window_scaling": 1.5,
		
		#drt: scaling factor for arrival uncertainty error due to discretisation of space 
		# removes associated picks drt * P_window from initiating pick pool

		# i.e. how many initiating P picks to remove? like the time window for that
		# no strong need to fudge with this too much

		"remove_initiating_picks_window_scaling":0.5,

		# nxd, still don't understand, probably some magic number for remove impossible events that are too far from the stations
		# GCarc0
		# cold try varying this probably
		"distance_scaling": 0.5,
		"std_tolerance_factor": 4,
		# used for synthetic resolution analysis
		"ires": 0,
		

	}
	paths = {}

	# default options because i am very lazy
	# also rewrite with something less stupid in the future

	if not real_path:
		paths["binary_path"] = "/home/zchoong001/cy1400/cy1400-eqt/REAL/bin/REAL"
	else:
		paths["binary_path"] = real_path
	if not station_file_path:
		paths["station_file_path"] = "/home/zchoong001/cy1400/cy1400-eqt/detections/febmar21/blank/Data/station_new.dat" 
	else:
		paths["station_file_path"] = station_file_path
	if not tt_path:
		paths["tt_table_path"] = "/home/zchoong001/cy1400/cy1400-eqt/detections/febmar21/blank/REAL/tt_db/ttdb.txt"
	else:
		paths["tt_table_path"] = tt_path
	if not pick_dir_path:
		paths["pick_dir_path"]	 = "/home/zchoong001/cy1400/cy1400-eqt/REAL/all_redo/Pick"
	else:
		paths["pick_dir_path"] = pick_dir_path
	if not day_list_path:
		paths["day_list_path"] = "/home/zchoong001/cy1400/cy1400-eqt/REAL/all_redo/filelist.txt"
	else:
		paths["day_list_path"] = day_list_path
	if not pbs_folder:
		paths["pbs_folder"] = "/home/zchoong001/cy1400/cy1400-eqt/pbs"
	else:
		paths["pbs_folder"] = pbs_folder
	if not output_folder:
		paths["output_folder"] = "/home/zchoong001/cy1400/cy1400-eqt/pbs/log"
	else:
		paths["output_folder"] = output_folder

	print(paths)

	

	# decide how many parameters to test

	# first do run time, then vary parameters for no. of events

	# since this requires multi processing, i suspect that i can make a .pbs file and then submit the job
	# which is quite a bit of effort but will probably be worth it since it's so reusable

	# this dictionary will be an N x M matrix (basically) 
	# which will generate N x M different test folders in total, hence
	# exhausting the possible permutations

	# this implies that i could have to qsub N x M jobs

	### CHANGE HERE
	params = default_params
	params["gridsearch_vertical_cellsize_km"] = 5
	params["gridsearch_horizontal_range_deg"] = 1
	params["gridsearch_horizontal_cellsize_deg"] = 0.05

	if not do_parallel:

		vary_params = {
			"gridsearch_horizontal_cellsize_deg": [0.05],
		}

		# my own config:
		#################

		## generate all the test bench folders
		
		job_info_list = []

		for v in itertools.product(*[vary_params[k] for k in vary_params]):
			print(v)

			change_key_list = list(vary_params.keys())

			_job_dict = {}
			for c, k in enumerate(change_key_list):
				_job_dict[k] = v[c]

			job_info_list.append(_job_dict)

		# save the job info dictionaries as json files later

		# each job will handle multiple days in a linear sequence i.e. put many different REAL calls in a sequence
		# in principle you could parallelise everything but eh 

		if not os.path.exists(os.path.join(paths["pbs_folder"], job_name)):
			os.makedirs(os.path.join(paths["pbs_folder"], job_name))

		for c, expt_info in enumerate(job_info_list):
			_params = default_params

			for k in expt_info:
				_params[k] = expt_info[k]

			print(expt_info)
			# _date_info = {
			# 	"year":"2020",
			# 	"month":"01",
			# 	"day":"02",
			# 	"date_str":"20200102",
			# }

			day_dict_list = generate_ymd(paths["day_list_path"])

			real_calls = []

			for d in (day_dict_list):
				real_call = (call_REAL(_params, paths, d, job_name, c))
				real_calls.append(real_call)

			script_job_writer(job_name, c, real_calls, paths)
			
			pbs_string = pbs_writer(len(job_info_list), job_name, paths)

	else:

		day_dict_list = generate_ymd(paths["day_list_path"])
		real_calls = []

		for d in day_dict_list:
			real_call = (call_REAL(params, paths, d, job_name, index = -1))
			real_calls.append(real_call)

		def chunker_list(seq, size):
			return [seq[i::size] for i in range(size)]


		chunked = (chunker_list(real_calls, n_workers))
		for c, chunk in enumerate(chunked):
			if len(chunk) == 0:
				continue
			script_job_writer(job_name, c, chunk, paths)

		pbs_writer(len([x for x in chunked if len(x) != 0]), job_name, paths)


		# generate all REAL calls
		# then divide into diff jobs depending on some specified number of output files



		# i think GCarc0 is geographical distance in degrees from the initiating event to the station?
		# GCarc

		# then call REAL (skipping the perl script which uses YMD)

		# do all the file copying within the python script (i.e. replace the bash script)
		
		# to construct the test bench you'll have to reproduce the folder structure (?) if you're just doing one day, it doesn't really matter

		# but then for test bench you do obviouly want to find the number of events in the whole catalogue i.e. need to reproduce folder structure somehow

def generate_ymd(day_list_path):

	file_list = []

	with open(day_list_path, "r") as f:
		for line in f:
			file_list.append(line.strip())

	file_dict_list = []

	for day in file_list:
		_dict = {
			"date_str": day,
			"year": day[0:4],
			"month": day[4:6],
			"day": day[-2:],
		}

		file_dict_list.append(_dict)

	return file_dict_list


def pbs_writer(n_nodes, job_name, paths, n_cores = 1):
	output_pbs = os.path.join(paths["pbs_folder"], job_name +".pbs")

	project_code = 'eos_shjwei'

	with open(output_pbs, "w") as f:
		if n_nodes == 1:
			pass
		else:
			f.write("#PBS -J 0-{}\n".format(n_nodes - 1))
		f.write("#PBS -N {}\n#PBS -P {}\n#PBS -q q32\n#PBS -l select={}:ncpus={}:mpiprocs=32:mem=16gb -l walltime=80:00:00\n".format(job_name, project_code, n_nodes, n_cores))
		f.write("#PBS -e log/pbs/{0}/error.log \n#PBS -o log/pbs/{0}/output.log\n".format(job_name))

		if n_nodes == 1:
			f.write("{1}/runtime_scripts/{0}/0/run.sh\n".format(job_name, paths["pbs_folder"]))
		else:
			f.write("{1}/runtime_scripts/{0}/${{PBS_ARRAY_INDEX}}/run.sh\n".format(job_name, paths["pbs_folder"]))


def script_job_writer(job_name, index, real_calls, paths):
	output_script = os.path.join(paths["pbs_folder"], "runtime_scripts", job_name, str(index), "run.sh".format(index))

	print(output_script)

	if not os.path.exists(os.path.join(paths["pbs_folder"], "runtime_scripts", job_name, str(index))):
		os.makedirs(os.path.join(paths["pbs_folder"], "runtime_scripts", job_name, str(index)))

	# need to create a folder for every day ......... god

	# or... is there another way to use python to save in between

	write_str = "OMP_NUM_THREADS=32\ncd {}/runtime_scripts/{}/{}\n".format(paths["pbs_folder"], job_name, index)

	for real_call in real_calls:

	# cp REAL binary into this folder
	# think it just depends on the directory it's calling from? 
	# f.write("cp {} .\n".format(paths["binary_path"]))
		write_str += "({}) &>> log_{}.txt 2>&1\n".format(real_call, index)
	# call REAL

	with open(output_script, "w") as f:
		f.write(write_str)

	time.sleep(1)
	os.chmod(output_script, 0o775)


def call_REAL(params, paths, date_info, job_name, index = 0):
	call_string = "time "

	call_string += paths["binary_path"]

	call_string += " -D{}/{}/{}/{:.3f}".format(
		date_info["year"],
		date_info["month"],
		date_info["day"],
		params["lat_centre"],
	)

	call_string += " -R"
	for k in ["gridsearch_horizontal_range_deg", "gridsearch_vertical_range_km", "gridsearch_horizontal_cellsize_deg", "gridsearch_vertical_cellsize_km",]:
		if (k == "gridsearch_centre_lon" or k == "gridsearch_centre_lat") and not params["gridsearch_centre_lon"]:
			call_string = call_string[:-1]
			break
		else:
			call_string += "{:.3f}/".format(params[k])

		
	call_string += " -G"
	for k in ["traveltime_horizontal_range_deg", "traveltime_vertical_range_km", "traveltime_horizontal_cellsize_deg", "traveltime_vertical_cellsize_km"]:
		call_string += "{:.2f}/".format(params[k])
	
	call_string += " -V"
	for k in ["average_p_velocity_kms", "average_s_velocity_kms", "consider_station_elevation", "shallow_p_velocity_kms", "shallow_s_velocity_kms"]:
		if not params["consider_station_elevation"] and k == "consider_station_elevation":

			call_string = call_string[:-1]
			break
		else:
			call_string += "{:.2f}/".format(params[k])

	call_string += " -S{:n}/{:n}/{:n}/{:n}/{}/{}/{}/{}/{}/{}/{}".format(
		params["n_p_picks"],
		params["n_s_picks"],
		params["n_total_picks"],
		params["n_both_ps_picks"],
		params["stdev_residual_threshold_seconds"],
		params["p-s_minimum_separation_seconds"],
		params["arrival_time_window_scaling"],
		params["remove_initiating_picks_window_scaling"],
		params["distance_scaling"],
		params["std_tolerance_factor"],
		params["ires"],
	)

	if index == -1:
		output_dir = os.path.join(paths["output_folder"], job_name, date_info["date_str"])
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

	else:
		output_dir = os.path.join(paths["output_folder"], job_name, str(index), date_info["date_str"])
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

	call_string += " {} {} {} {}".format(
		paths["station_file_path"], 
		os.path.join(paths["pick_dir_path"], date_info["date_str"] ),
		paths["tt_table_path"],
		output_dir,
		)
	return call_string

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("job_name")

	ap.add_argument("-r", "--real", help = "Path to REAL binary")
	ap.add_argument("-sfp", "--station_file_path",)
	ap.add_argument("-tt", "--tt_path")
	ap.add_argument("-pd", "--pick_dir_path")
	ap.add_argument("-dlp", "--day_list_path")
	ap.add_argument("-pbs", "--pbs_folder")
	ap.add_argument("-nw", "--n_workers", default = 0, type = int)
	ap.add_argument("-o", "--output_folder")
	ap.add_argument("-p", "--parallel", help = "Split file list across multiple jobs, without varying any parameters", action = "store_true")

	args = ap.parse_args()
	generate_job(args.job_name, 
	real_path = args.real, 
	station_file_path = args.station_file_path,
	tt_path = args.tt_path,
	pick_dir_path = args.pick_dir_path,
	day_list_path = args.day_list_path,
	pbs_folder = args.pbs_folder,
	output_folder = args.output_folder,
	do_parallel = args.parallel,
	n_workers = args.n_workers,
	)

