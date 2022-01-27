# goals:

# prepre sac --> hdf5 file, estimating how much space it'll take
# and allowing for station selection / time frame selection
# 
# 
# first choose station, then choose time frame
# 
# want to have tools to show uptime for the station


# which suggests having different scripts or just like

# multi_station -up -o save.png -sta TA01-TA19.txt
# to show graphically or sth -st

# multi_station -make -s input.txt -o save_folder

# multi_station -choose sac_folders -o input.txt



import matplotlib

import matplotlib.pyplot as plt

from subprocess import check_output
import argparse
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
import os

import json



#get_all_files("/home/eos_data/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/")


def get_all_files(sac_folders, output_file):
	# look inside /tgo/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/ 
	# for .SAC files

	df_list = []

	print(sac_folders)
	for sac_folder in sac_folders:

		all_files = [str(p) for p in Path(sac_folder).rglob("*SAC")]

		df = pd.DataFrame()

		df["filepath"] = all_files

		#print(df)

		for index, row in df.iterrows():
			_sta = row.filepath.split("/")[-2] # second last entry should be the station name

			# the sac files have their channel in front and not behind so... 

			# check if all 3 channels are available too?

			_file = row.filepath.split("/")[-1]

			_year = _file.split(".")[5]
			_jday = _file.split(".")[6]

			out = check_output(["saclst", "KZDATE", "KZTIME", "B", "E", "f", row.filepath])
			out = [x for x in out.decode('UTF-8').strip().split(" ") if x != ""]

			print(out)

			try:
				assert len(out) > 2
			except:
				continue

			df.at[index, 'station'] = _sta
			df.at[index, 'year'] = (_year) # it's saved as a string; so pandas probably inferred that it's an int
			df.at[index, 'jday'] = (_jday)
			df.at[index, 'start_time'] = _file.split(".")[7]

			df.at[index, "kzdate"] = out[1]
			df.at[index, "kztime"] = out[2]
			df.at[index, "B"] = out[3]
			df.at[index, "E"] = out[4]

			df.at[index, "sac_start_dt"] = datetime.datetime.strptime("{} {}".format(out[1], out[2]), "%Y/%m/%d %H:%M:%S.%f")
			df.at[index, "sac_end_dt"] = datetime.datetime.strptime("{} {}".format(out[1], out[2]), "%Y/%m/%d %H:%M:%S.%f") + datetime.timedelta(seconds = float(out[4]))


		df_list.append(df)


		# fullday doesn't give useful info because the file could start at 000000 and still be incomplete


	new_df = pd.concat(df_list)
	print(new_df)
	new_df.to_csv(output_file, index = False)

def generate_timestamps(input_csv, output_csv):
	df = pd.read_csv(input_csv)
	df["sac_start_dt"] = pd.to_datetime(df["sac_start_dt"])
	df["sac_end_dt"] = pd.to_datetime(df["sac_end_dt"])

	overlap = 0.3

	c_df = pd.DataFrame()

	for index, row in df.iterrows():

		df.at[index, "c"] = ".EHZ." in row.filepath 

	df = df[df["c"] == True]

	# do for all stations by default
	gdf = df.groupby(by = "station")

	c = 0

	of = pd.DataFrame() # output dataframe

	for sta, _df in gdf:


		# there seems to be an O(n^2) slow down which is probably because the dataframe is getting so long

		timestamp_set = []
		print(sta)
		
		for index, row in _df.iterrows():
			new_timestamp = (row.sac_start_dt, row.sac_end_dt, row.filepath)

			#print("new timestamp", new_timestamp)
			#print(timestamp_set)

			if len(timestamp_set) == 0:
				timestamp_set.append(new_timestamp)

			else:
				overlap_set = []
				# for ~ a few months of data with station-days, an O(n^2) search is acceptable
				for test_ts in timestamp_set:
					if new_timestamp[0] < test_ts[1] and new_timestamp[1] > test_ts[0]:
						overlap_set.append(test_ts) # check for overlap, collate set of overlaps

				timestamp_set.append(new_timestamp)
				
		timestamp_set = sorted(timestamp_set, key = lambda x: x[0])

		for i in timestamp_set:
			print(i)

		for _ts in timestamp_set:

			print(_ts)
			# generate timestamps for each date range into the output dataframe
			# start time of 1 min, station, filepath, sac_start_time

			n_cuts = ((_ts[1] - _ts[0]).total_seconds() - (overlap * 60))/((1 - overlap)*60)


			n_cuts = int(np.floor(n_cuts))

			for i in range(n_cuts):
				_ts_start = _ts[0] + datetime.timedelta(seconds = (i * (1 - overlap) * 60))

				_dt = (1 - overlap) * 60 * i

				of.at[c, "station"] = sta
				of.at[c, "timestamp_start"] = _ts_start 
				of.at[c, "time_from_file_start"] = _dt
				of.at[c, "filepath"] = _ts[2]

				c += 1


			
		print(of)

		of.to_csv("test.csv")

		break



def plot_all_uptime(selector_file, start_date, end_date, all_csv_path = "station/all_aceh_sac.csv"):

	# selector file: list of stations

	with open(selector_file, 'r') as f:
		station_list = f.read().split("\n")

	station_list = list(filter(lambda x: x != "", station_list))

	n_stations = len(station_list)

	_parse_char = "j"

	start_date = datetime.datetime.strptime(start_date, "%Y.%{}".format(_parse_char))
	end_date = datetime.datetime.strptime(end_date, "%Y.%{}".format(_parse_char))

	n_days = (end_date - start_date).days + 1

	#print(n_stations)
	#print(n_days)
	
	image = np.zeros((n_stations, n_days))
	#print(image.shape)

	df = pd.read_csv(all_csv_path)


	# for index, row in df.iterrows():
	# 	df.at[index, 'datetime'] = datetime.datetime.strptime("{}_{}".format(row.year, row.jday), "%Y_%j")

	# 	for _cha in ["EHE", "EHN", "EHZ"]:
	# 		if _cha in row.filepath:
	# 			df.at[index,'channel'] = _cha
	# 			
	
	if not 'dt' in df.columns:
		
		for index, row in df.iterrows():
			df.at[index, 'dt'] = datetime.datetime.strptime("{}.{}".format(row['year'], row['jday']), "%Y.%j")

	#print(df.datetime)


	for index, row in df.iterrows():

		if row.station in station_list and row['dt'] >= start_date and row['dt'] <= end_date:
			station_index = station_list.index(row.station)
			# print(row["dt"])
			# print(start_date)
			day_index = (row["dt"] - start_date).days

			image[station_index, day_index] = 1

			#print(station_index, day_index)

	print("##########################################\n")			
	for i in range(n_stations):	
		print(station_list[i], "{:.2f}".format(np.sum(image[i, :])/n_days))
	print("\n##########################################")

	#print()

	plt.figure(figsize=(18,12), dpi = 150)
	plt.yticks(np.arange(n_stations) + 0.5, list(station_list), fontsize = 8)
	plt.xticks(np.arange(n_days) + 0.5, np.arange(0, (n_days)), fontsize = 8)
	plt.xlabel("Days")
	plt.ylabel("Station name")
	plt.pcolormesh(image, edgecolors ='k', linewidth=2)
	plt.savefig("log/uptime/uptime_{}_{}-{}.png".format(datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d-%H%M%S"), datetime.datetime.strftime(start_date, "%Y.%j"), datetime.datetime.strftime(end_date, "%Y.%j")))



def select_files(selector_file,  all_csv_path = "station/all_aceh_sac.csv", output_file = "", patch = False):

	
	# start_date format = e.g. 2020_03 for month

	df = pd.read_csv(all_csv_path)

	# kinda inefficient bc 10^5 rows but it's fine bc it won't be used very often

	for index, row in df.iterrows():
		df.at[index, 'dt'] = datetime.datetime.strptime("{}.{}".format(int(row.year), int(row.jday)), "%Y.%j")

		df.at[index, "_uid"] = "{}-{}-{}-{}".format(row.station, row.year, row.jday, row.start_time)

		for _cha in ["EHE", "EHN", "EHZ"]:
			if _cha in row.filepath:
				df.at[index,'channel'] = _cha


	#station_list = []

	with open(selector_file, 'r') as f:
		station_list = f.read().split("\n")

	station_list = list(filter(lambda x: x != "", station_list))


	if patch:
		_df = df[(df["station"].isin(station_list)) & (df["start_time"] != "000000") & (df["start_time"].str[-2:] != "-1")]

		# -1 at the back: almost defn a duplicate
		# anything else: likely to be a partial day file

	else:
		_df = df[df["station"].isin(station_list)]

	_df.sort_values("jday", inplace = True)

	#_df.to_csv("station/test.csv")
	# want to check if it's complete, whether it's all fulldays, if any gaps
	# which should also show me the missing files


	# if len(_df.index) < expected_files:
	# 	print("some missing, can report on the no. of missing + flag to continue")

	# 	print("expected: ", expected_files, "actual: ", len(_df.index))
	# 	#plot_all_uptime(selector_file, _startdate, _enddate)

	# elif len(_df.index) > expected_files:
	# 	print("more files than expected which is odd, have to filter so that it's only 3")

	# 	print("This shouldn't happen")

	# 	#idk what to do if this happens actually

	# else:
	# 	print("all files present, no issues :)")

	if output_file:
		_df.to_csv(output_file, index = False)


def make_station_json(station_coords, station_list, output):

	station_json = {}

	with open(station_list, "r") as f:
		station_list = f.read().split("\n")[:-1]

	for _station in station_list:
		print(_station)
		station_json[_station] = {"network": "AC", "channels":["EHZ", "EHE", "EHN"]}


	with open(station_coords, "r") as f:
		coordinates = f.read().split("\n")
		
		coordinates = [y.strip() for x in coordinates if len(x) > 0 for y in x.strip().split("\t") if len(y) > 0 ]

	for station in station_json:
		print(station)
		i = coordinates.index(station)

		station_json[station]["coords"] = [float(coordinates[i + 2]), 100, float(coordinates[i+1])] # i set elevation to 100 because that's the average height in sumatra and i'm not given this information + it's not that important 

	with open(output, 'w') as f:
		json.dump(station_json, f)

def pbs_writer(n_nodes, output_csv, job_name, env_name, project_code, no_execute = False, yes_execute = False, use_gpu = False):

	output_pbs = os.path.join("/home/zchoong001/cy1400/cy1400-eqt/pbs", job_name +".pbs")

	with open(output_pbs, "w") as f:
		f.write("#PBS -J 0-{}\n".format(n_nodes - 1))
		if use_gpu:
			f.write("#PBS -N {}\n#PBS -P {}\n#PBS -q gpu8\n#PBS -l select={}:ncpus=1:mpiprocs=32:ngpus=1\n".format(job_name, project_code, n_nodes))
		elif no_execute and not use_gpu:
			f.write("#PBS -N {}\n#PBS -P {}\n#PBS -q q32\n#PBS -l select={}:ncpus=1:mpiprocs=32:mem=2gb -l walltime=1:00:00\n".format(job_name, project_code, n_nodes))
		
		elif (yes_execute or not no_execute) and not use_gpu:
			f.write("#PBS -N {}\n#PBS -P {}\n#PBS -q q32\n#PBS -l select={}:ncpus=1:mpiprocs=32:mem=16gb -l walltime=80:00:00\n".format(job_name, project_code, n_nodes))
		f.write("#PBS -e log/pbs/{0}/error.log \n#PBS -o log/pbs/{0}/output.log\n".format(job_name))
		if use_gpu:
			f.write("module load cuda/10.1\nexport HDF5_USE_FILE_LOCKING='FALSE'\n")
		f.write("module load python/3/intel/2020\nmodule load sac\ncd $PBS_O_WORKDIR\nnprocs=`cat $PBS_NODEFILE|wc -l`\ninputfile=/home/zchoong001/cy1400/cy1400-eqt/node_distributor.py\n")
		f.write("encoded_file={}\nmkdir -p log/pbs/{}\nsource activate {}\n".format(output_csv, job_name, env_name))

		if not yes_execute:
			f.write("python $inputfile -id $PBS_ARRAY_INDEX -decode $encoded_file\n")

		if not no_execute:
			f.write("/home/zchoong001/cy1400/cy1400-eqt/pbs/runtime_scripts/{0}/${{PBS_ARRAY_INDEX}}.sh >& log/pbs/{0}/$PBS_JOBID.log 2>&1\n".format(job_name))

def read_config(config_file_path):
	"""
	config_file_path should be an absolute file path for consistency
	"""
	
	options = {}
	with open(config_file_path, 'r') as f:
		for line in f:
			k,v = line.strip().split("=")
			
			options[k] = v
	
	print(options)
	return options


def encode_multirun(
	output_csv = "", 
	station_file = "", 
	n_multi = 20, 
	n_nodes = None, 
	job_name = "", 
	start_day = "", 
	end_day = "", 
	model_path = "", 
	hdf5_parent = "",
	detection_parent = "",
	write_hdf5 = False, 
	run_eqt = False, 
	plot_eqt = False, 
	merge_csv = False,
	recompute_snr = False,
	filter_csv = False,
	write_headers = False,
	pbs = None,
	sac_select = None,
	make_sac_csv = False,
	no_execute = False,
	yes_execute = False,
	snr_threshold = 8,
	config = "",
	patch = False,
	json_file = "",
	use_gpu = False,
	):

	# encode everything (sac to hdf5, prediction
	# node distributor will decode according/modify a main() function in one script to control what you want to do
	# 
	# also, since eqt assumes that you join all the hdf5 files together and mash them, but i'm keeping them in
	# station-named folders, so that allows me to open one node per station
	# it also means that i'll need to keep everything in an additional layer of folder 
	# it could be DDMMM_experiment/TA19/TA19/TA19.csv and TA19.hdf5
	# 
	# which sounds kind of stupid but it'll work fine
	
	# need to know how many nodes i'm using
	# plus other arguments 
	# could it be a json file so i can store other args?
	#
	# what about sac writing? Will you need that many nodes as well?
	#
	#
	# i think al lthe command line arguments could be put into this file so I can control what i want at a single point  
	
	#MAX_NODES = 20

	#n_multi = 20
	# assign one node to one station for now

	#sac_selector = "9jun_10station.csv" # idt this is needed 
	# station_file = "station/random10.txt" # this means that i'll have to check somewhere if the station has any data for that period...
	# might as well solve the problem at the source i.e. for each batch that you feed in (inside multi station ) check that all stations have more than 1 file

	# and if not they are automatically dropped / with some error message
	# or just throw an error? but that's kinda disruptive i wouldn't like it 
	# 
	if config:
		config_options = read_config(config)
	
	if job_name == "":
		job_name = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")

	if config:
		model_path = config_options["MODEL_PATH"]
		station_json = config_options["STATION_JSON"]
		if hdf5_parent == "":
			hdf5_parent = os.path.join("/scratch", (config_options["USERNAME"]), job_name)

		if detection_parent == "":
			detection_parent = os.path.join(config_options["PROJECT_ROOT"],"detections", job_name)

		if not output_csv:
			output_csv = os.path.join(config_options["PROJECT_ROOT"], "node_encode", job_name + ".csv")

		if not sac_select:
			sac_select = os.path.join(config_options["PROJECT_ROOT"], "station_time", job_name + ".csv")

		_folders = [
		os.path.join(config_options["PROJECT_ROOT"], "detections"), 
		os.path.join(config_options["PROJECT_ROOT"], "node_encode"), 
		os.path.join(config_options["PROJECT_ROOT"], "station_time"),
		os.path.join(config_options["PROJECT_ROOT"], "pbs", "runtime_scripts"),
		os.path.join(config_options["PROJECT_ROOT"], "log", "timing"),]

		for _f in _folders:
			if not os.path.exists(_f):
				try:
					os.makedirs(_f)
				except:
					pass

		env_name = config_options["ENV_NAME"]
		project_code = config_options["PROJECT_CODE"]
		

	else:
		if not model_path:
			model_path = "/home/zchoong001/cy1400/cy1400-eqt/EQTransformer/ModelsAndSampleData/EqT_model.h5"

		if not json_file:
			station_json = "/home/zchoong001/cy1400/cy1400-eqt/station/json/all_stations.json"

		else:
			station_json = json_file

		if hdf5_parent == "":
			hdf5_parent = os.path.join("/scratch/zchoong001", job_name)

		if detection_parent == "":
			detection_parent = os.path.join("/home/zchoong001/cy1400/cy1400-eqt/detections", job_name)

		if not output_csv:
			output_csv = os.path.join("/home/zchoong001/cy1400/cy1400-eqt/node_encode", job_name + ".csv")

		if not sac_select:
			sac_select = os.path.join("/home/zchoong001/cy1400/cy1400-eqt/station_time", job_name + ".csv")
		
		env_name = "tf2"
		project_code = "eos_shjwei"

	if make_sac_csv:
		select_files(station_file, output_file = sac_select, all_csv_path = make_sac_csv, patch = patch)

	df = pd.DataFrame(columns = ["id", "sta", "hdf5_folder", "prediction_output_folder", "merge_output_folder", "start_day", "end_day", "multi", "model_path"])

	with open(station_file, 'r') as f:
		station_list = f.read().split("\n")

	station_list = list(filter(lambda x: x != "", station_list))

	if not n_nodes:
		n_nodes = len(station_list)

	# if len(station_list) > 20:
	# 	raise ValueError("Does not support more than {} stations, please split.".format(MAX_NODES))

	for c, sta in enumerate(station_list):

		df.at[c,"id"] = c + 1 # count from 1 bc the array number starts from 1? like it's just easier

		df.at[c, "sta"] = sta

		df.at[c, "hdf5_folder"] = os.path.join(hdf5_parent,sta, sta)

		df.at[c, "prediction_output_folder"] = os.path.join(detection_parent, sta) # multiruns will have like multi_01 behind etc.
		df.at[c, "model_path"] =  model_path
		df.at[c, "merge_output_folder"] = os.path.join(detection_parent, "{}_merged".format(sta))

		df.at[c, "start_day"] = start_day
		df.at[c, "end_day"] = end_day

		df.at[c, "multi"] = n_multi
		df.at[c, "nodes"] = n_nodes
		df.at[c, "snr_threshold"] = snr_threshold

		df.at[c, "station_json"] = station_json
		if config:
			df.at[c, "project_root"] = config_options["PROJECT_ROOT"]

			df.at[c, "output_folder"] = os.path.join(config_options["PROJECT_ROOT"], "pbs", "runtime_scripts", job_name)
		
		else:

			df.at[c, "project_root"] = "/home/zchoong001/cy1400/cy1400-eqt/"

			df.at[c, "output_folder"] = "/home/zchoong001/cy1400/cy1400-eqt/pbs/runtime_scripts/{}".format(job_name)

		df.at[c, "job_name"] = job_name
		df.at[c, "write_hdf5"] = write_hdf5
		df.at[c, "run_eqt"] = run_eqt
		df.at[c, "plot_eqt"] = plot_eqt

		df.at[c, "merge_csv"] = merge_csv
		df.at[c, "filter_csv"] = filter_csv
		df.at[c, "recompute_snr"] = recompute_snr
		df.at[c, "write_headers"] = write_headers


		df.at[c, "sac_select"] = sac_select


	df.to_csv(output_csv, index = False)

	if pbs:
		pbs_writer(n_nodes, output_csv, job_name, env_name, project_code, no_execute = no_execute, yes_execute = yes_execute, use_gpu = use_gpu)


	# load station_list, see number of stations

	# behind hte scenes, i will split the stations into groups of 20

	# if no. of stations > n_nodes, then make a new job? or can just plan this separately



if __name__ == "__main__":

	# i'm going to make this environment so cluttered with command line arguments
	# even i won't know how to use it


	parser = argparse.ArgumentParser(description = "utils for preparing multistation hdf5 files, running eqt (future) and plotting sac files")

	parser.add_argument("--get", help = "name of actual target sac folder (month)", default = None, nargs = '+')
	parser.add_argument("-i", "--input", help = "input file")
	parser.add_argument("-o", "--output", help = "output file", default = "")


	parser.add_argument("-sf", "--selector", help = "txt file with linebreak separated station names, specifying stations of interest")


	parser.add_argument("-s", "--start_date", help = "underscore separated year with julian day e.g. 2020_085 for start date (inclusive)")
	parser.add_argument("-e", "--end_date", help = "underscore separated year with julian day e.g. 2020_108 for enddate (inclusive)")
	parser.add_argument("-m", "--month", help = "flag to use month. default is Julian day. e.g. 2020_03 to represent March", action = "store_true", default = False)
	parser.add_argument("-j", "--julian", help = "default is True, to use Julian day to specify start and end date", action = "store_true", default = True)


	parser.add_argument("-js", "--json", help = "file with the coordinates of all the stations")

	parser.add_argument("-pl", "--plot", help = "get uptime file for some start and end date", action = "store_true")

	parser.add_argument("-enc", "--encode", action="store_true", help = "flag for script to encode a csv file for multinode running on HPC array")

	parser.add_argument("-job", help = "unique string identifier for the job", default = "")

	parser.add_argument("-write_hdf5", action = "store_true", help = "flag to write from sac to hdf5 folder, default False")
	parser.add_argument("-run_eqt", action = "store_true", help = "flag to run eqt prediction and merge multiple predictions, default False")
	parser.add_argument("-merge_csv", action = "store_true", help = "flag to merge multiple csvs")
	parser.add_argument("-recompute_snr", action = "store_true", help = "flag to recompute snrs")


	parser.add_argument("-filter_csv", action = "store_true", help = "flag to filter csvs")
	parser.add_argument("-write_headers", action = "store_true", help = "flag to write sac headers")

	parser.add_argument("-plot_eqt", action = "store_true", help = "flag to plot 150s sac traces and png 3C plots, default False")

	parser.add_argument("-det_parent", help = "parent folder to keep detection output files", default = "")
	parser.add_argument("-hdf5_parent", help = "parent folder to keep hdf5 files", default = "")
	parser.add_argument("-model_path", help = "path to model", default = "")
	parser.add_argument("-n_multi", type = int, help = "no. of times to repeat prediction, default 20", default = 20)
	parser.add_argument("-n_nodes", type = int, help = "no. of HPC nodes to use", default = None)

	parser.add_argument('-p', "--patch", action = "store_true")


	parser.add_argument("-pbs", help = "flag to generate pbs script", default = False, action = "store_true")

	parser.add_argument("-msc","--make_sac_csv", help = "table of all SAC files in the target folder, filtered by the station list (-i)", default = False)

	parser.add_argument("-ss", "--sac_select", help = "string for .csv file in station time folder, generated by select_files() in multi_station.py", default = None)
	parser.add_argument("-nx", "--no_execute", action = "store_true", help = "pbs file will generate but not run", default = False)
	parser.add_argument("-yx", "--yes_execute", action = "store_true", help = "script has been generated, run script without calling node_distributor", default = False)


	parser.add_argument("-snr_threshold", type = int, help = "threshold number for S wave SNR", default = 8)
	parser.add_argument("-config", help = "path to config file from which directories are created")


	parser.add_argument("-gts", "--generate_timestamps", action = "store_true")
	parser.add_argument("-gpu", "--use_gpu", action = "store_true")

	args = parser.parse_args()

	if args.selector and not args.plot:
		select_files(args.selector, args.start_date, args.end_date, args.julian, args.month, args.input, args.output)

	elif args.generate_timestamps:
		generate_timestamps(args.input, args.output)

	elif args.get:
		get_all_files(args.get, args.output)
	elif args.json and not args.encode:
		make_station_json(args.json, args.input, args.output)

	elif args.plot:
		plot_all_uptime(args.selector, args.start_date, args.end_date, args.input)
	elif args.encode:
		encode_multirun(
			output_csv = args.output, 
			station_file = args.input, 
			job_name = args.job, 
			start_day = args.start_date, 
			end_day = args.end_date, 
			model_path = args.model_path, 
			hdf5_parent = args.hdf5_parent, 
			detection_parent = args.det_parent, 
			write_hdf5 = args.write_hdf5, 
			run_eqt = args.run_eqt, 
			plot_eqt = args.plot_eqt, 
			pbs = args.pbs, 
			n_nodes = args.n_nodes, 
			n_multi = args.n_multi, 
			sac_select = args.sac_select, 
			make_sac_csv = args.make_sac_csv, 
			merge_csv = args.merge_csv, 
			recompute_snr = args.recompute_snr, 
			filter_csv = args.filter_csv, 
			write_headers = args.write_headers, 
			no_execute = args.no_execute, 
			yes_execute = args.yes_execute,
			snr_threshold = args.snr_threshold, 
			config = args.config, 
			patch = args.patch, 
			json_file = args.json,
			use_gpu = args.use_gpu)


