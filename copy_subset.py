# given some filtered csv, 
# and given some picks which are already graded
# 
# copy them into A/B/Z folders into a new folder
# 


import shutil
from pathlib import Path
import pandas as pd
import os
import numpy as np
import argparse
import glob
import datetime

from utils import load_with_path_and_grade

def main():

	csv_file = "imported_figures/21mar_default_merge/21may_recomputedsnr_default.csv"
	source_folder = "imported_figures/21mar_default_merge/sac_picks"
	output_folder = "imported_figures/21mar_default_merge/agreement50"
	output_csv = "imported_figures/21mar_default_merge/agreement50.csv"



	# need to match the csv timestamp to the actual file

	#new_df = load_with_path_and_grade(csv_file, source_folder)
	new_df = pd.read_csv(csv_file)

	#print(new_df)


	# filter

	new_df = new_df[new_df.agreement == 50]

	print(new_df)

	new_df.to_csv(output_csv)

	folders = [output_folder, os.path.join(output_folder, "A"), os.path.join(output_folder, "B"), os.path.join(output_folder, "Z"), ]

	for _f in folders:
		if not os.path.exists(_f):
			os.makedirs(_f)



	for index, row in new_df.iterrows():

		start_path = row["pathname"][:-4] + "*"
		end_path = os.path.join(output_folder, row["grade"])

		for file in glob.glob(start_path):
			shutil.copy(file, end_path)

	# write new file locations 

	# cp path * --> output_folder/grade/ 

	# copying routine


main()

