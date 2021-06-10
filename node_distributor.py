# goal: use gekko arrays to distribute tasks

# prepare csv files so upon receiving an ID each script can do a lookup and get the files they need

# this could be a bash script but reading from csv in bash is just... i don't want to do that

import argparse
import pandas as pd
import os
from pathlib import Path


# accept argument
# load encoded file
# look up requirement arguments
# call python functions
# 
def main(uid, encoded_csv):

	md = pd.read_csv(encoded_csv) # md for metadata bc lazy

	print(md.at[uid, "sta"])

	# if write hdf5

	
	

	# if prediction
	# run prediction with multi

	# also run merge and recompute snr

	# if plot

	


if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument("-id", type = int, help = "id to access the rows in the `encoded' csv file")
	parser.add_argument("-decode", help = "path to `encoded' csv file")

	args = parser.parse_args()

	main(args.id, args.decode)
