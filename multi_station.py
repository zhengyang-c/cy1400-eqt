# goals:

# prepre sac --> hdf5 file, estimating how much space it'll take
# and allowing for station selection / time frame selection
# 
# 
# first choose station, then choose time frame
# 
# want to have tools to show uptime for the station


# which suggests having different scripts or just like

# multi_station -up -o save.png -sta TA01-TA19.txt
# to show graphically or sth -st

# multi_station -make -s input.txt -o save_folder

# multi_station -choose sac_folders -o input.txt



import argparse
from pathlib import Path
import pandas as pd
import numpy as np

def get_uptime(sac_folder):
	# look inside /tgo/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/ 
	# for .SAC files
	# 
	
	# how does SAC to miniSEED conversion work again
	# i think have a pandas dataframe, find the station. 
	# you want the path information for each of them
	
	all_files = [str(p) for p in Path(sac_folder).rglob("*SAC")]

	df = pd.DataFrame()

	df["filepath"] = all_files

	print(df)

get_uptime("/tgo/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/ ")

