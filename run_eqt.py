from EQTransformer.core.predictor import predictor
import argparse
import os
import datetime

def run(hdf_folder, model_path, output_folder, n_cpus):
	'''
	hdf_folder is ${mseed_folder}_processed_hdfs
	'''

	predictor(input_dir = hdf_folder, input_model = model_path, output_dir=output_folder, detection_threshold=0.3, P_threshold=0.1, S_threshold=0.1, plot_mode='time', output_probabilities = False, number_of_cpus = n_cpus)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument('hdf_folder')
	parser.add_argument('model_path')
	parser.add_argument('output_folder')
	parser.add_argument('-n', '--n_cpus', type = int, default = 1)
	parser.add_argument('-t', '--time', type = str, help = "file path to append to to")

	#parser.add_argument('json_output', help = "this is an intermediate file needed by EqT")

	#parser.add_argument('output_folder')

	args = parser.parse_args()

	start_time = datetime.datetime.now()
	run(args.hdf_folder, args.model_path, args.output_folder, args.n_cpus)
	

	end_time = datetime.datetime.now()

	time_taken = (end_time - start_time).total_seconds()

	if args.time:
		with open(args.time, "a") as f:
			f.write("run_eqt.py,{},{},{}\n".format(args.hdf_folder,datetime.datetime.strftime(start_time, "%Y%m%d %H%M%S"),time_taken))


