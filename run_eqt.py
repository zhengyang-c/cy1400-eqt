from EQTransformer.core.predictor import predictor
import argparse
import os

def run(hdf_folder, model_path, output_folder, n_cpus):
	'''
	hdf_folder is ${mseed_folder}_processed_hdfs
	'''

	predictor(input_dir = hdf_folder, input_model = model_path, output_dir=output_folder, detection_threshold=0.3, P_threshold=0.1, S_threshold=0.1, plot_mode='time_frequency', output_probabilities = True, number_of_cpus = 32)


parser = argparse.ArgumentParser()

parser.add_argument('hdf_folder')
parser.add_argument('model_path')
parser.add_argument('output_folder')
parser.add_argument('-n', '--n_cpus', type = int, default = 1)

#parser.add_argument('json_output', help = "this is an intermediate file needed by EqT")

#parser.add_argument('output_folder')

args = parser.parse_args()


run(args.hdf_folder, args.model_path, args.output_folder, args.n_cpus)