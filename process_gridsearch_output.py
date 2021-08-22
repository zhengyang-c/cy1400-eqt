import pandas as pd
from pathlib import Path
import argparse
import numpy as np

"""
want to find:

1) distribution of minimum standard deviations (temporal)

this estimates the spatial uncertainty but also not really

2) spatial range: 
for some range of timing uncertainty, what's the area of that?


procedure:
----------
(1) get the folder of all the .npy files
(2) load each of them

 build a table (i.e. a csv file)
(3) get the minimum, get the DX
(4) lb_Corner is not saved....
"""

def main():
	search_folder = "gridsearch/5jul_afterREAL"
	search_term = "*.npy"

	df = pd.DataFrame()

	for c, p in enumerate(Path(search_folder).rglob(search_term)):
		file_name = str(p)

		pid = file_name.split("_")[0]

		with open(file_name, 'w') as f:
			grid = np.load(f)

		L2 = grid[:,:,:,0] # 0: get the standard deviation
		indices = np.where(L2 == L2.min())

		min_x = lb_corner[0] + indices[0][0] * args["DX"]
		min_y = lb_corner[1] + indices[1][0] * args["DX"]

		min_std = L2[indices[0][0], indices[1][0], indices[2][0]]

		df.at[c, 'min_std'] = min_std
		df.at[c, 'ID'] = pid
		df.at[c, 'DX'] = file_name.split("_")[1][2:]
		df.at[c, 'DZ'] = file_name.split("_")[2][2:]

	df.to_csv("log/23aug_5julafterREAL_gridsearch.csv",index = False)






if __name__ == "__main__":
	main()
