import argparse
import itertools
import os
from subprocess import check_output
import shutil


def generate_job(job_name):

	# will have to construct the function call from scratch

	# REAL is called for every year/month/day

	# expected input: run REAL on file list

	# the default params are by definition opioniated
	default_params = {
		"lat_centre": 4.75,
		# -R
		"gridsearch_horizontal_range_deg": 1 ,
		"gridsearch_vertical_range_km": 60,
		"gridsearch_horizontal_cellsize_deg" : 0.05,
		"gridsearch_vertical_cellsize_km" : 2,

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

	## copy the REAL 

	paths = {
		"binary_path": "/home/zchoong001/cy1400/cy1400-eqt/REAL/testbench/blank/REAL/REAL", # use absolute path for this
		"station_file_path": "/home/zchoong001/cy1400/cy1400-eqt/detections/febmar21/blank/Data/station_new.dat",
		"tt_table_path": "/home/zchoong001/cy1400/cy1400-eqt/detections/febmar21/blank/REAL/tt_db/ttdb.txt",
		"pick_dir_path": "/home/zchoong001/cy1400/cy1400-eqt/REAL/7jul_redojan/Pick" ,
		"day_list_path": "/home/zchoong001/cy1400/cy1400-eqt/REAL/testbench/filelist.txt",
		"pbs_folder": "/home/zchoong001/cy1400/cy1400-eqt/pbs/runtime_scripts"
	}

	print(paths)

	

	# decide how many parameters to test

	# first do run time, then vary parameters for no. of events

	# since this requires multi processing, i suspect that i can make a .pbs file and then submit the job
	# which is quite a bit of effort but will probably be worth it since it's so reusable

	# this dictionary will be an N x M matrix (basically) 
	# which will generate N x M different test folders in total, hence
	# exhausting the possible permutations

	# this implies that i could have to qsub N x M jobs

	vary_params = {
		"gridsearch_horizontal_cellsize_deg": [0.05, 0.1, 0.2],
		#"gridsearch_horizontal_range_deg": [1, 1.5, 2],
	}

	# my own config:
	#################
	params = default_params
	params["gridsearch_vertical_cellsize_km"] = 5

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
	#
	#
	#

	if not os.path.exists(os.path.join(paths["pbs_folder"], job_name)):
		os.makedirs(os.path.join(paths["pbs_folder"], job_name))

	for expt_info in job_info_list:
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

		for c, d in enumerate(day_dict_list):
			real_call = (call_REAL(_params, paths, d))

			script_job_writer(job_name, c, real_call, paths)

		
		pbs_string = pbs_writer(len(day_dict_list), job_name)

		print(pbs_string)


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


def pbs_writer(n_nodes, job_name,  n_cores = 4):

	output_pbs = os.path.join("/home/zchoong001/cy1400/cy1400-eqt/pbs", job_name +".pbs")

	project_code = 'eos_shjwei'

	with open(output_pbs, "w") as f:
		f.write("#PBS -J 0-{}\n".format(n_nodes - 1))
		f.write("#PBS -N {}\n#PBS -P {}\n#PBS -q q32\n#PBS -l select={}:ncpus={}:mpiprocs=32:mem=16gb -l walltime=80:00:00\n".format(job_name, project_code, n_nodes, n_cores))
		f.write("#PBS -e log/pbs/{0}/error.log \n#PBS -o log/pbs/{0}/output.log\n".format(job_name))

		f.write("cd /home/zchoong001/cy1400/cy1400-eqt/pbs/runtime_scripts/{0}/${{PBS_ARRAY_INDEX}}\n")
		f.write("./${{PBS_ARRAY_INDEX}}.sh\n")


def script_job_writer(job_name, index, real_call, paths):
	output_script = os.path.join(paths["pbs_folder"], job_name, str(index), "{}.sh".format(index))

	if not os.path.exists(os.path.join(paths["pbs_folder"], job_name, index)):
		os.makedirs(os.path.join(paths["pbs_folder"], job_name, index))

	with open(output_script, "a") as f:
		# cp REAL binary into this folder
		# think it just depends on the directory it's calling from? 
		# f.write("cp {} .\n".format(paths["binary_path"]))
		f.write("{} >> log_{}.txt".format(real_call, index))
		# call REAL


def call_REAL(params, paths, date_info):
	call_string = ""

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
			call_string += "{:.2f}/".format(params[k])

		
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

	call_string += " {} {} {}".format(
		paths["station_file_path"], 
		os.path.join(paths["pick_dir_path"], date_info["date_str"] ),
		paths["tt_table_path"]
		)
	return call_string

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("job_name")

	args = ap.parse_args()
	generate_job(args.job_name)

