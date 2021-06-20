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

import argparse
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
import os

import json



#get_all_files("/home/eos_data/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/")


def get_all_files(sac_folder, output_file):
	# look inside /tgo/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/ 
	# for .SAC files
	# 
	
	# how does SAC to miniSEED conversion work again
	# i think have a pandas dataframe, find the station. 
	# you want the path information for each of them
	
	folder_list = ["Deployed-2019-12-MSEED", # this is actually hardcoded
	"Deployed-2020-01-MSEED",
	"Deployed-2020-02-MSEED",
	"Deployed-2020-03-MSEED",
	"Deployed-2020-04-MSEED",
	"Deployed-2020-05-MSEED",
	"Deployed-2020-07-MSEED",]

	all_files = []

	for _f in folder_list:
		all_files.extend([str(p) for p in Path(os.path.join(sac_folder, _f)).rglob("*SAC")])


	#print(all_files)

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

		_datetime = datetime.datetime.strptime("{}.{}".format(_year,_jday), "%Y.%j")

		df.at[index, 'station'] = _sta
		df.at[index, 'year'] = (_year) # it's saved as a string; so pandas probably inferred that it's an int
		df.at[index, 'jday'] = (_jday)
		df.at[index, 'start_time'] = _file.split(".")[7]

		df.at[index, 'fullday'] = (_file.split(".")[7] == "000000")

		# fullday?
	# "station/all_aceh_sac.csv"
	df.to_csv(output_file, index = False)



def plot_all_uptime(selector_file, start_date, end_date, all_csv_path = "station/all_aceh_sac.csv"):

	# selector file: list of stations

	with open(selector_file, 'r') as f:
		station_list = f.read().split("\n")

	station_list = list(filter(lambda x: x != "", station_list))

	n_stations = len(station_list)

	_parse_char = "j"

	start_date = datetime.datetime.strptime(start_date, "%Y_%{}".format(_parse_char))
	end_date = datetime.datetime.strptime(end_date, "%Y_%{}".format(_parse_char))

	n_days = (end_date - start_date).days + 1
	
	image = np.zeros((n_stations, n_days))
	#print(image.shape)

	df = pd.read_csv(all_csv_path)


	# for index, row in df.iterrows():
	# 	df.at[index, 'datetime'] = datetime.datetime.strptime("{}_{}".format(row.year, row.jday), "%Y_%j")

	# 	for _cha in ["EHE", "EHN", "EHZ"]:
	# 		if _cha in row.filepath:
	# 			df.at[index,'channel'] = _cha
	df.dt = pd.to_datetime(df.dt, errors = 'coerce')

	#print(df.datetime)


	for index, row in df.iterrows():

		if row.station in station_list:
			station_index = station_list.index(row.station)
			# print(row["dt"])
			# print(start_date)
			day_index = (row["dt"] - start_date).days

			image[station_index, day_index] = 1

			print(station_index, day_index)


	#print()

	plt.figure(figsize=(18,12), dpi = 150)
	plt.yticks(np.arange(n_stations) + 0.5, list(station_list), fontsize = 8)
	plt.xticks(np.arange(n_days) + 0.5, np.arange(0, (n_days)), fontsize = 8)
	plt.xlabel("Days")
	plt.ylabel("Station name")
	plt.pcolormesh(image, edgecolors ='k', linewidth=2)
	plt.savefig("log/uptime/uptime_{}_{}-{}.png".format(datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d-%H%M%S"), datetime.datetime.strftime(start_date, "%Y_%j"), datetime.datetime.strftime(end_date, "%Y_%j")))



def select_files(selector_file, start_date, end_date, y_jul = True, y_mon = False, all_csv_path = "station/all_aceh_sac.csv", output_file = ""):

	
	# start_date format = e.g. 2020_03 for month

	if y_jul and y_mon:
		print("invalid options")
		return 0

	if y_jul:
		_parse_char = "j"
	elif y_mon:
		_parse_char = "m"


	_startdate, _enddate = start_date, end_date


	start_date = datetime.datetime.strptime(start_date, "%Y_%{}".format(_parse_char))
	end_date = datetime.datetime.strptime(end_date, "%Y_%{}".format(_parse_char))

	df = pd.read_csv(all_csv_path)

	# kinda inefficient bc 10^5 rows but it's fine bc it won't be used very often

	for index, row in df.iterrows():
		df.at[index, 'dt'] = datetime.datetime.strptime("{}_{}".format(row.year, row.jday), "%Y_%j")


		for _cha in ["EHE", "EHN", "EHZ"]:
			if _cha in row.filepath:
				df.at[index,'channel'] = _cha


	#station_list = []

	with open(selector_file, 'r') as f:
		station_list = f.read().split("\n")

	station_list = list(filter(lambda x: x != "", station_list))

	print(station_list)

	_df = df[df["station"].isin(station_list) & (df["fullday"]) & (df["dt"] >= start_date) & (df["dt"] <= end_date)]

	_df.sort_values("jday", inplace = True)


	#_df.to_csv("station/test.csv")


	# want to check if it's complete, whether it's all fulldays, if any gaps

	# which should also show me the missing files

	n_days = (end_date - start_date).days + 1
	n_stations = len(station_list)

	image = np.zeros((n_stations, n_days))


	expected_files = n_days * 3 * n_stations


	if len(_df.index) < expected_files:
		print("some missing, can report on the no. of missing + flag to continue")

		print("expected: ", expected_files, "actual: ", len(_df.index))


		plot_all_uptime(selector_file, _startdate, _enddate)
		

	elif len(_df.index) > expected_files:
		print("more files than expected which is odd, have to filter so that it's only 3")

		print("This shouldn't happen")

		#idk what to do if this happens actually


	else:
		print("all files present, no issues :)")


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

		station_json[station]["coords"] = [100, float(coordinates[i + 1]), float(coordinates[i+2])] # i set elevation to 100 because that's the average height in sumatra and i'm not given this information + it's not that important 

	with open(output, 'w') as f:
		json.dump(station_json, f)

def pbs_writer(n_nodes, output_csv, job_name, no_execute = False):

	output_pbs = os.path.join("/home/zchoong001/cy1400/cy1400-eqt/pbs", job_name +".pbs")

	with open(output_pbs, "w") as f:
		f.write("#PBS -J 0-{}\n".format(n_nodes - 1))
		f.write("#PBS -N EQT_DISTRIBUTED_ZCHOONG001\n#PBS -P eos_shjwei\n#PBS -q q32\n#PBS -l select=1:ncpus=1:mpiprocs=32\n")
		f.write("#PBS -e log/pbs/{0}/${{PBS_JOBID}}_${{PBS_ARRAY}}.err \n#PBS -o log/pbs/{0}/${{PBS_JOBID_error}}_${{PBS_ARRAY_INDEX}}.out\n".format(job_name, datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")))
		f.write("module load python/3/intel/2020\nmodule load sac\ncd $PBS_O_WORKDIR\nnprocs=`cat $PBS_NODEFILE|wc -l`\ninputfile=node_distributor.py\n")
		f.write("encoded_file={}\nmkdir -p log/pbs/{}\nsource activate tf2\n".format(output_csv, job_name))
		f.write("python $inputfile -id $PBS_ARRAY_INDEX -decode $encoded_file\n")

		if not no_execute:
			f.write("./pbs/runtime_scripts/{0}/${{PBS_ARRAY_INDEX}}.sh >& log/pbs/{0}/$PBS_JOBID.log 2>&1".format(job_name))

def encode_multirun(
	output_csv = "", 
	station_file = "", 
	n_multi = 20, 
	n_nodes = 20, 
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
	snr_threshold = 8,
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
	
	if job_name == "":
		job_name = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")

	if model_path == "":
		model_path = "/home/zchoong001/cy1400/cy1400-eqt/EQTransformer/ModelsAndSampleData/EqT_model.h5"

	#job_name = "10jun_10station_2020.150-151" #should be descriptive


	station_json = "/home/zchoong001/cy1400/cy1400-eqt/station/json/all_stations.json"

	if hdf5_parent == "":
		hdf5_parent = os.path.join("/scratch/zchoong001", job_name)

	if detection_parent == "":
		detection_parent = os.path.join("/home/zchoong001/cy1400/cy1400-eqt/detections", job_name)

	#output_csv = os.path.join("node_encode", job_name)

	if make_sac_csv:
		select_files(station_file, start_day, end_day, output_file = sac_select)

	#metadata_log = "/home/zchoong001/cy1400/cy1400-eqt/log/metadata/"

	df = pd.DataFrame(columns = ["id", "sta", "hdf5_folder", "prediction_output_folder", "merge_output_folder", "start_day", "end_day", "multi", "model_path"])

	with open(station_file, 'r') as f:
		station_list = f.read().split("\n")

	station_list = list(filter(lambda x: x != "", station_list))

	if len(station_list) > 20:
		raise ValueError("Does not support more than {} stations, please split.".format(MAX_NODES))

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
		pbs_writer(n_nodes, output_csv, job_name, no_execute = no_execute)


	# load station_list, see number of stations

	# behind hte scenes, i will split the stations into groups of 20

	# if no. of stations > n_nodes, then make a new job? or can just plan this separately



if __name__ == "__main__":

	# i'm going to make this environment so cluttered with command line arguments
	# even i won't know how to use it


	parser = argparse.ArgumentParser(description = "utils for preparing multistation hdf5 files, running eqt (future) and plotting sac files")

	parser.add_argument("--get", help = "name of parent SAC folder. get all SAC files available in a data folder, print to csv", default = None)
	parser.add_argument("-i", "--input", help = "input file")
	parser.add_argument("-o", "--output", help = "output file")


	parser.add_argument("-sf", "--selector", help = "txt file with linebreak separated station names, specifying stations of interest")


	parser.add_argument("-s", "--start_date", help = "underscore separated year with julian day e.g. 2020_085 for start date (inclusive)")
	parser.add_argument("-e", "--end_date", help = "underscore separated year with julian day e.g. 2020_108 for enddate (inclusive)")
	parser.add_argument("-m", "--month", help = "flag to use month. default is Julian day. e.g. 2020_03 to represent March", action = "store_true", default = False)
	parser.add_argument("-j", "--julian", help = "default is True, to use Julian day to specify start and end date", action = "store_true", default = True)


	parser.add_argument("-js", "--json", help = "file with the coordinates of all the stations")

	parser.add_argument("-p", "--plot", help = "get uptime file for some start and end date", action = "store_true")

	parser.add_argument("-encode", action="store_true", help = "flag for script to encode a csv file for multinode running on HPC array")

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
	parser.add_argument("-n_multi", type = int, help = "no. of time sto repeat prediction, default 20", default = 20)
	parser.add_argument("-n_nodes", type = int, help = "no. of HPC nodes to use, max is 20", default = 20)


	parser.add_argument("-pbs", help = "flag to generate pbs script", default = False, action = "store_true")
	parser.add_argument("-make_sac_csv", help = "flag to make the job csv", action = "store_true", default = False)

	parser.add_argument("-sac_select", help = "string for .csv file in station time folder, generated by select_files() in multi_station.py", default = None)
	parser.add_argument("-no_execute", action = "store_true", help = "pbs file will generate but not run", default = False)

	parser.add_argument("-snr_threshold", type = int, help = "threshold number for S wave SNR", default = 8)

	args = parser.parse_args()

	if args.selector and not args.plot:
		select_files(args.selector, args.start_date, args.end_date, args.julian, args.month, args.input, args.output)
	elif args.get:
		get_all_files(args.get, args.output)
	elif args.json:
		make_station_json(args.json, args.input, args.output)

	elif args.plot:
		plot_all_uptime(args.selector, args.startd_ate, args.end_date, args.input)
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
			snr_threshold = args.snr_threshold)


