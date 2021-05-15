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

	output_root = "training_files/aceh_27mar_EV/may15_test"
	output_hdf5 = output_root + ".hdf5"
	output_csv = output_root + ".csv"

	write_hf = h5py.File(output_hdf5, 'a')
	grp = write_hf.create_group("data")

	input_dir = "/home/zchoong001/cy1400/cy1400-eqt/training_files/aceh_27mar_EV"



	# get list of roots 

	files = [".".join(str(x).split(".")[:-1]) for x in Path(input_dir).glob("*csv")]

	print(files)

	for file in files:
		# merge hdf5 first since it's harder
		read_hf = h5py.File(file + ".hdf5", "r")

		print(len(read_hdf['data']))

		for row in read_hf['data']:
			
			x = read_hf.get('data/' + row)
			data = np.array(x)

			dsF = write_hf.create_dataset("data/"+row, data.shape, data = data, dtype = np.float32)

			for header in headers:
				dsF.attrs[header] = x.attrs[header]

			write_hf.flush()
			
		read_hf.close()




	# merge csv

	# merge the hdf5 with the newly created one




	# just use try / except to handle empty headers

main()
