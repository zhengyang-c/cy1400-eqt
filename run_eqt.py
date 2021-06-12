from EQTransformer.core.predictor import predictor
import argparse
import os
import datetime
import multiprocessing
from multiprocessing.pool import ThreadPool

def run(hdf_folder, model_path, output_folder, multi = 1, start = 1):
	'''
	hdf_folder is ${mseed_folder}_processed_hdfs
	# '''

	

	# def wrapper(args):
	# 	predictor(input_dir = args["hdf_folder"], input_model = args["model_path"], output_dir=args["output_folder"], detection_threshold=0.3, P_threshold=0.1, S_threshold=0.1, plot_mode='time', output_probabilities = False, number_of_cpus = args["n_cpus"])

	# if n_cpus != multiprocessing.cpu_count():
	n_cpus = multiprocessing.cpu_count() # taken from mousavi stead

	# if multi > 1:

	# 	arglist = []

	# 	for i in range(multi):

	# 		args = {"hdf_folder": hdf_folder, "model_path": model_path, "output_folder": output_folder + "_{}".format(i), "n_cpus": n_cpus, "multi": multi}

	# 		print(args["output_folder"])

	# 		arglist.append(args)


	# 	with ThreadPool(n_cpus) as p:
	# 		p.map(wrapper, arglist) 
	# else:
	
	for c in range(start, multi + 1):
		_output = os.path.join(output_folder, "multi_{:02d}".format(c))
		predictor(input_dir = hdf_folder, input_model = model_path, output_dir=_output, detection_threshold=0.3, P_threshold=0.1, S_threshold=0.1, plot_mode='time', output_probabilities = False, number_of_cpus = n_cpus, number_of_plots = 0)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument('hdf_folder')
	parser.add_argument('model_path')
	parser.add_argument('output_folder')
	parser.add_argument('-s', '--start', type = int, default = 1, help = "start number")
	parser.add_argument('-m', '--multirun', type = int, default = 1, help = "how many repeats")
	#parser.add_argument('-n', '--n_cpus', type = int, default = 1)
	parser.add_argument('-t', '--time', type = str, help = "file path to append to")

	#parser.add_argument('json_output', help = "this is an intermediate file needed by EqT")

	#parser.add_argument('output_folder')

	args = parser.parse_args()

	start_time = datetime.datetime.now()
	run(args.hdf_folder, args.model_path, args.output_folder, args.multirun, start = args.start)
	

	end_time = datetime.datetime.now()

	time_taken = (end_time - start_time).total_seconds()

	if args.time:
		with open(args.time, "a") as f:
			f.write("run_eqt.py,{},{},{},{}\n".format(args.hdf_folder,datetime.datetime.strftime(start_time, "%Y%m%d %H%M%S"),time_taken, args.output_folder))


