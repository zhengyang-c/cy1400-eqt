import pandas as pd
import numpy as np
import subprocess
import argparse
from utils import load_graded_from_file_structure



def pick_agreement(filtered_csv_file, graded_sac_folder, output_file, plot_file):
	# load raw csv file
	# just loading takes like 6 seconds fyi it's a large file
	# and i'm doing this quite naively
	# 
	
	#filtered_csv_file = "imported_figures/21mar_default_merge/21mar_default_filtered.csv"
	#graded_sac_folder = "imported_figures/21mar_default_merge/sac_picks/"

	#output_file = "plot_data/5may_agreement_hist.txt"
	#plot_file = "plots/5may_agreement_hist.pdf"

	#df_raw = load_from_file_structure(graded_sac_folder, raw_csv_file) # finally a one liner load
	df = load_graded_from_file_structure(graded_sac_folder, filtered_csv_file) 

	

	bins = np.arange(0,51,1) 
	#55 because total no. of runs is 50 but honestly that should be included somewhere in metadata hm
	# and 50 + 5 binsize for end indexing is 55
	
	write_data = []


	for _grade in ["A", "B", "Z"]:

		hist, _bins = np.histogram(df[df.grade == _grade].agreement, bins = bins) 

		# normalised because.... should be absolute number tbh

		write_data.extend([hist, (_bins[1:] + _bins[:-1])/2]) # wow u can do this?

	outputdf = pd.DataFrame(np.column_stack(write_data), columns = ["A", "A_bins", "B", "B_bins", "Z", "Z_bins"])
	outputdf.to_csv(output_file, index = False)

	process = subprocess.Popen(["gnuplot", "-c", "plot_agreementhist.gn", output_file, plot_file])



	# for agreement distribution, can just use filtered csv file
	# for finding the statistics of the pick time / probabilities, this will need 

	"""
	research question: are good events with high SNR more likely to have higher agreement i.e. more runs that detect this

	want to find: agreement distribution for A, B, Z (three categories is a bit unwieldy)

	want to plot SNR as a function of agreement for (A,B,Z). 

	"""

parser = argparse.ArgumentParser()

parser.add_argument('filter', type = str, help = "filtered csv file (from merge_csv)")
parser.add_argument('folder', type = str, help = "graded folder with A, B and Z inside")
parser.add_argument('output', type = str, help = "filepath to txt file for plotting")
parser.add_argument('plot', type = str, help = "filepath to pdf plot")

#parser.add_argument('manual_picks', type = str, help = "Path to txt file of manual picks (this should not require any processing)")

#parser.add_argument('csv_output', type = str, help = "Path to new csv file with all noise removed")
args = parser.parse_args()

pick_agreement(args.filter, args.folder, args.output, args.plot)
