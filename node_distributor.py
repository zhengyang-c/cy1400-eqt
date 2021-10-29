# goal: use gekko arrays to distribute tasks

# prepare csv files so upon receiving an ID each script can do a lookup and get the files they need

# this could be a bash script but reading from csv in bash is just... i don't want to do that

import argparse
import pandas as pd
import os
import time

# accept argument
# load encoded file
# look up requirement arguments
# call python functions
# 
def main(uid, encoded_csv):

	md = pd.read_csv(encoded_csv) # md for metadata bc lazy

	#output_folder = "/home/zchoong001/cy1400/cy1400-eqt/pbs/runtime_scripts/{}".format(md.at[uid, "job_name"])
	output_folder = md.at[uid, "output_folder"]


	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	output_bash = os.path.join(output_folder, "{}.sh".format(uid))

	write_str = "#!/bin/bash\n"

	log_file_name = os.path.join(md.at[uid, "project_root"], "log", "timing", md.at[uid, "job_name"], md.at[uid, "sta"]+".txt")

	if not os.path.exists(os.path.join(md.at[uid, "project_root"], "log", "timing", md.at[uid, "job_name"])):
		os.makedirs(os.path.join(md.at[uid, "project_root"], "log", "timing", md.at[uid, "job_name"]))

	if md.at[uid, "write_hdf5"]:

		# csv path, output folder, station_json

		print("preproc with {},{},{}".format(md.at[uid, "sac_select"], md.at[uid, "hdf5_folder"],  md.at[uid, "station_json"]))

		#
		# remember to remove the partial day file after i'm done rip
		#
		# -partial_day_file /home/zchoong001/cy1400/cy1400-eqt/all_aceh_sac_2020uptime_1jul.csv 
		write_str += "#write hdf5\npython {} {} {} {} {} -t {}\n".format(
			os.path.join(md.at[uid, "project_root"], "sac_to_hdf5.py"),
			md.at[uid, "sac_select"], 
			md.at[uid, "sta"], 
			md.at[uid, "hdf5_folder"], 
			md.at[uid, "station_json"],
			log_file_name)


	# i kind of like the modularity so i'll make each script its own argument

	if md.at[uid, "run_eqt"]:

		#run_eqt.run(md.at[uid, "hdf5_folder"], md.at[uid, "model_path"], md.at[uid, "prediction_output_folder"], multi = md.at[uid, "multi"])

		print("run with {}, {}, {}".format(md.at[uid, "hdf5_folder"], md.at[uid, "model_path"], md.at[uid, "prediction_output_folder"], md.at[uid, "multi"]))

		write_str += "#run eqt\nfor ((f=0;f<{1};f++))\ndo\n\techo $f\n\tpython {0} {2} {3} {4}/multi_$f -t {5}\ndone\n".format(
			os.path.join(md.at[uid, "project_root"], "run_eqt.py"),
			md.at[uid, "multi"], 
			md.at[uid, "hdf5_folder"], 
			md.at[uid, "model_path"], 
			md.at[uid, "prediction_output_folder"],
			log_file_name)

	if md.at[uid, "merge_csv"]:


		write_str += "#merge csv\npython {} {} {} merge -csv\n".format(
			os.path.join(md.at[uid, "project_root"], "merge_csv.py"),
			md.at[uid, "prediction_output_folder"], 
			md.at[uid, "merge_output_folder"],)

	if md.at[uid, "recompute_snr"]:

		write_str += "#recompute snr\npython {} {} {} {} {} {} -t {}\n".format(
			#os.path.join(md.at[uid, "project_root", "recompute_snr.py"]),
			os.path.join(md.at[uid, "project_root"], "recompute_snr.py"),
			md.at[uid, "sac_select"], 
			os.path.join(md.at[uid, "merge_output_folder"], "merge_filtered.csv"), 
			os.path.join(md.at[uid, "merge_output_folder"], "merge_filtered_snr.csv"),
			md.at[uid, "sta"],
			md.at[uid, "hdf5_folder"],
			log_file_name)

	if md.at[uid, "filter_csv"]:

		write_str += "#filter csv\npython {} {} {} {} {}\n".format(
			os.path.join(md.at[uid, "project_root"], "filter_csv.py"),
			os.path.join(md.at[uid, "merge_output_folder"], "merge_filtered_snr.csv"), 
			os.path.join(md.at[uid, "merge_output_folder"], "merge_filtered_snr_customfilter.csv"), 
			md.at[uid, "snr_threshold"], 
			md.at[uid, "multi"])

		# recompute snr

		# some filtering script

	if md.at[uid, "plot_eqt"]:

		# sac writing and plotting 
		write_str += "#plot eqt \npython {} {} {} -t {}\n".format(
			os.path.join(md.at[uid, "project_root"], "plot_eqt.py"),
			md.at[uid, "sac_select"], 
			os.path.join(md.at[uid, "merge_output_folder"], "merge_filtered_snr_customfilter.csv"),
			log_file_name)

	if md.at[uid, "write_headers"]:
		write_str += "#write headers\npython {} {} -t {}\n".format(
			os.path.join(md.at[uid, "project_root"], "header_writer.py"),
			os.path.join(md.at[uid, "merge_output_folder"], "merge_filtered_snr_customfilter.csv"),
			log_file_name)

		# header writing 

		# writerino

	with open(output_bash, 'w') as f:
		f.write(write_str)
		
	os.chmod(output_bash, 0o775)

	time.sleep(1)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument("-id", type = int, help = "id to access the rows in the `encoded' csv file")
	parser.add_argument("-decode", help = "path to `encoded' csv file")

	args = parser.parse_args()

	main(args.id, args.decode)
