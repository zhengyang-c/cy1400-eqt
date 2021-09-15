""" 
input: folder of csv files from a multi-run
output:

"""

import numpy as np
from pathlib import Path
import pandas as pd
import random
import matplotlib.pyplot as plt
import datetime

from utils import load_with_path_and_grade

from merge_csv import preprocess, merging_df, concat_df

def prec(A,B,Z):
	try:
		return ((A+B)/(A+B+Z))
	except:
		return 0

def load():
	source_folder = "/home/zy/cy1400-eqt/imported_figures/21mar_default_merge/csv_collection"

	csv_file = "/home/zy/cy1400-eqt/imported_figures/21mar_default_merge/21may_recomputedsnr_default.csv"
	# grade_file = "manual/21mar_default_multi_repicked.txt"


	output_file = "plot_data/1jun_montecarloABZ_21mardefaultmerge_SNRfilter.csv" # for plotting

	all_csv_files = [str(p) for p in Path(source_folder).rglob("*csv")]


	#truth_df = load_with_path_and_grade(csv_file, grade_folder)

	truth_df = pd.read_csv(csv_file)
	truth_df["new_p_snr_ampsq"] = 10 * np.log10(truth_df["new_p_snr_ampsq"])
	truth_df["new_s_snr_ampsq"] = 10 * np.log10(truth_df["new_s_snr_ampsq"])

	truth_df['event_dt'] = pd.to_datetime(truth_df.event_dt)

	for index, row in truth_df.iterrows():
		truth_df.at[index, "wf"] = "{}.{}".format(row.station, datetime.datetime.strftime(row.event_dt, "%Y.%j.%H%M%S"))

	print(list(truth_df))




	N_SIMULATIONS = 10

	#print(all_csv_files)

	#args = {"sta": "TA19", "grade_file": "manual/21mar_default_multi_repicked.txt"}

	#graded_traces, grades = load_from_grades(args["grade_file"])

	_data = []
	data = []


	for i in range(2,50,2): # naively trusting the csv file len(all_csv_files) + 

		n_file_data = []

		for j in range(N_SIMULATIONS):

			_data = [i] 
			print(i,j)
			random_list = random.sample(all_csv_files, i)
			
			#n_events = run_graded_simulation(random_list, args) 

			_events = run_graded_simulation(random_list)
			_events["event_dt"] = pd.to_datetime(_events.event_start_time)

			#print(list(_events))

			matched = (_events.merge(truth_df[["wf", "new_p_snr_ampsq", "new_s_snr_ampsq", "grade"]], on = "wf", how = "left"))

			# then check for those which did not match, using a threshold of 2

			for index, row in matched[matched['grade'].isnull()].iterrows():

				for _t in range(-2, 3):
					_test_wf = "{}.{}".format(row.station, datetime.datetime.strftime(row.event_dt + datetime.timedelta(seconds = _t) , "%Y.%j.%H%M%S"))

					if _test_wf in truth_df.wf.values:

						_true_index = (truth_df.index[truth_df.wf == _test_wf].tolist()[0])

						for j in ['grade', 'new_p_snr_ampsq', 'new_s_snr_ampsq']:

							matched.at[index, j] = truth_df.at[_true_index, j]

			# at this point, if it still doesn't match, then the time spread is v large and it's unlikely to be an actual event
			# hence, if grade is blank, we can filter it away

			ug = matched[matched.grade.isnull() == False]

			#print(ug)


			#ug = compare_grades(graded_traces, grades, _events) # ug for unknown grades bc lazy

			my_filter = (ug["agreement"] == i) & (ug["new_s_snr_ampsq"] > 8)

			
			_A = (len(ug[(ug["grade"] == "A") & my_filter].index))
			_B = (len(ug[(ug["grade"] == "B") & my_filter].index))
			_Z = (len(ug[(ug["grade"] == "Z") & my_filter].index))

			_data.extend([_A + _B, prec(_A,_B,_Z)])

			n_file_data.append(_data)

		data.append(n_file_data)

	mean = np.mean(data, axis = 1)
	std = np.std(data, axis = 1)

	print(mean, std)


	column_roots = ["n_runs","gd", "pr"]
	_df = pd.DataFrame(mean, columns = column_roots)
	_stddf = pd.DataFrame(std, columns = [x + "_std" for x in column_roots])

	_df[list(_stddf.columns)] = _stddf

	print(_df)
	_df.to_csv(output_file, index = False)



def run_graded_simulation(list_of_csv_paths):

	df = concat_df(list_of_csv_paths)
	df = preprocess(df)
	df_filtered = merging_df(df)

	filenames = []

	#print(df_filtered['event_datetime'])

	for index, row in df_filtered.iterrows():
		df_filtered.at[index, 'wf'] = "{}.{}".format(row.station, datetime.datetime.strftime(row['event_datetime'],"%Y.%j.%H%M%S"))


		#_timestamp = row['event_datetime'].strftime("%H%M%S")
		#_year = row['event_datetime'].strftime("%Y")
		#_day = row['event_datetime'].strftime("%j") # julian day

		#_file_name = "{}.{}.{}.{}".format(args["sta"], _year, _day, _timestamp)

		#filenames.append(_file_name)

	return df_filtered




def run_simulation(list_of_csv_paths):
	df = concat_df(list_of_csv_paths)
	df = preprocess(df)
	df_filtered = merging_df(df)



	return len(df_filtered.index)

load()