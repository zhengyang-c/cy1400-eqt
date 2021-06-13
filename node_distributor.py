# goal: use gekko arrays to distribute tasks

# prepare csv files so upon receiving an ID each script can do a lookup and get the files they need

# this could be a bash script but reading from csv in bash is just... i don't want to do that

import argparse
import pandas as pd
import os

# accept argument
# load encoded file
# look up requirement arguments
# call python functions
# 
def main(uid, encoded_csv):

	md = pd.read_csv(encoded_csv) # md for metadata bc lazy

	output_folder = "/home/zchoong001/cy1400/cy1400-eqt/pbs/runtime_scripts/{}".format(md.at[uid, "job_name"])

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	output_folder = os.path.join(output_folder, "{}.sh".format(uid))

	write_str = ""

	if md.at[uid, "write_hdf5"]:

		# csv path, output folder, station_json

		print("preproc with {},{},{}".format(md.at[uid, "sac_select"], md.at[uid, "hdf5_folder"],  md.at[uid, "station_json"]))

		write_str += "#write hdf5\npython /home/zchoong001/cy1400/cy1400-eqt/sac_to_hdf5.py {} {} {}\n".format(md.at[uid, "sac_select"], md.at[uid, "hdf5_folder"], md.at[uid, "station_json"])



	if md.at[uid, "run_eqt"]:

		#run_eqt.run(md.at[uid, "hdf5_folder"], md.at[uid, "model_path"], md.at[uid, "prediction_output_folder"], multi = md.at[uid, "multi"])

		print("run with {}, {}, {}".format(md.at[uid, "hdf5_folder"], md.at[uid, "model_path"], md.at[uid, "prediction_output_folder"], md.at[uid, "multi"]))

		write_str += "#run eqt\nfor ((f=0;f<{};f++))\ndo\n\techo $f\n\tpython /home/zchoong001/cy1400/cy1400-eqt/run_eqt.py {} {} {}\ndone\n".format(md.at[uid, "multi"], md.at[uid, "hdf5_folder"], md.at[uid, "model_path"], md.at[uid, "prediction_output_folder"])


		#merge_csv(md.at[uid, "sta"], md.at[uid, "prediction_output_folder"], md.at[uid, "merge_output_folder"], "merge", csv_or_not = True)

		#print("merge with {}, {}, {}, {}".format(md.at[uid, "sta"], md.at[uid, "prediction_output_folder"], md.at[uid, "merge_output_folder"]))

		# recompute snr 



		# some filtering script



	if md.at[uid, "plot_eqt"]:

		# sac writing and plotting 
		pass

		# header writing 

	with open(output_bash, 'w') as f:
		f.write(write_str)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument("-id", type = int, help = "id to access the rows in the `encoded' csv file")
	parser.add_argument("-decode", help = "path to `encoded' csv file")

	args = parser.parse_args()

	main(args.id, args.decode)
