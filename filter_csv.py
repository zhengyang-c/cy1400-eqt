import pandas as pd
import argparse
import numpy as np
import os

def use_filter(input_file, output_file, s_snr_threshold, multi):

	if not os.path.exists(input_file):
		print("filter_csv: file not found")
		return 0

	df = pd.read_csv(input_file)

	df = df[(df['s_snr_ampsq_db'] > s_snr_threshold) & (df['agreement'] == multi)]

	df.to_csv(output_file, index = False)

	# filters:

	# s_snr_ampsq > 8
	# agreement = max (no. of runs)


	pass

if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	#parser.add_argument('source_folder', help = "sac_picks folder, from the eqt plotter")

	parser.add_argument('input_file', help = "csv after recompute_snr")
	parser.add_argument('output_file', help = "output csv with files to plot")	
	parser.add_argument('s_snr_threshold', help = "S arrival SNR threshold (db, computed using squared amplitudes with 1s windows", type = float)
	parser.add_argument('multi', help = "no. of repeats that were performed", type = float)
	

	args = parser.parse_args()
	use_filter()