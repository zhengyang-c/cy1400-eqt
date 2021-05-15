import h5py
import pandas as pd
import numpy as np
from pathlib import Path


# input:
# folder with hdf5 files to merge (put them together), assuming that the file root of the .csv and .hdf5 are the same
# new path root (for .csv and .hdf5)

# output:
# merged hdf5 file and .csv file at the new path root 

def main():
	headers = ['p_arrival_sample', 's_arrival_sample', 'snr_db', 'coda_end_sample', 'trace_category', 'trace_start_time', 'receiver_type', 'network_code', 'receiver_latitude', 'receiver_longitude', 'receiver_elevation_m', 'receiver_code', 'trace_name']

	output_root = ""
	output_hdf5 = output_root + ".hdf5"
	output_csv = output_root + ".csv"

	#hf = h5py.File(output_hdf5, 'w')
	#grp = hf.create_group("data")

	input_dir = "/home/zchoong001/cy1400/cy1400-eqt/training_files/may14_compiled"

	# get list of roots 

	files = [".".join(str(x).split(".")[:-1]) for x in Path(input_dir).glob("*csv")]

	print(files)

	for file in files:
		# merge hdf5 first since it's harder
		temp_hf = h5py.File(file + ".hdf5", "r")

		for row in temp_hf['data']:
			print(evi)


	# merge csv

	# merge the hdf5 with the newly created one




	# just use try / except to handle empty headers

main()
