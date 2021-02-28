import h5py as h5
import numpy as np
import os
import math
import json
import pandas as pd
import argparse

def trim(output_name):

	#hdfs = ["EQTransformer/ModelsAndSampleData/100samples.hdf5"]
	#csv = ["EQTransformer/ModelsAndSampleData/100samples.csv"]

	hdfs = ["/home/zchoong001/Downloads/chunk1.hdf5",
	"/home/zchoong001/Downloads/chunk2.hdf5",]
	# "/mnt/e/2020/chunk2/chunk2.hdf5"

	n = [5000, 5000]

	csv_output_data = {
	"p_arrival_sample": [],
	"s_arrival_sample": [],
	"snr_db":[], 
	"coda_end_sample":[],
	"trace_category":[],
	"trace_name":[],
	}
	
	#output_name = "training_files/STEAD_1000_27feb_3"
	output_path = "{}.hdf5".format(output_name)
	csv_output_path = "{}.csv".format(output_name)
	_outhf = h5.File(output_path, "w")

	_outgrp = _outhf.create_group("data")

	#hf = h5py.File(output_path, 'w')
	#grp = hf.create_group("data")

	for c, _h in enumerate(hdfs):

		print("kill me")
		_loadhf = h5.File(_h, "r")

		keys = list(_loadhf["data"].keys())
		for _c, key in enumerate(keys):
			if _c >= n[c]:
				break

			print(key)
			_datum = np.array(_loadhf.get("data/"+key))
			_g = _outgrp.create_dataset(key, (6000,3), data = _datum)

			_p = _loadhf.get("data/"+key).attrs['p_arrival_sample']
			_s = _loadhf.get("data/"+key).attrs['s_arrival_sample']
			_snr = _loadhf.get("data/"+key).attrs['snr_db']
			_c = _loadhf.get("data/"+key).attrs['coda_end_sample']
			_trace = _loadhf.get("data/"+key).attrs['trace_category']

			csv_output_data["p_arrival_sample"].append(_p)
			csv_output_data["s_arrival_sample"].append(_s)
			csv_output_data["snr_db"].append(_snr)
			csv_output_data["coda_end_sample"].append(_c)
			csv_output_data["trace_category"].append(_trace)
			csv_output_data["trace_name"].append(key)
			

			_g.attrs['p_arrival_sample'] = _p
			_g.attrs['s_arrival_sample'] = _s
			_g.attrs['snr_db'] = _snr
			_g.attrs['coda_end_sample'] = _c
			_g.attrs['trace_category'] = _trace	


			#print(_p, _s, _snr, _c, _trace)
		_loadhf.close()

	_outhf.close()

	d_csv = pd.DataFrame.from_dict(csv_output_data)
	d_csv.to_csv(csv_output_path, index = False)

parser = argparse.ArgumentParser()
parser.add_argument('output_name', type = str)

args = parser.parse_args()

plot(args.output_name)
