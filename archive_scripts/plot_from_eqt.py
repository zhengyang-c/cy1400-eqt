import obspy
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import pandas
import os
import re

output_folder_name = "detections" # eqt output
data_parent_folder_name = "EOS_SAC" # what folder structure am i uh using 

folders = [x[0] for x in os.walk(data_parent_folder_name)]

# if the last few letters follow a specific regex pattern, then use that folder

folders = list(filter(lambda x: re.match(r"\D{2,3}\d{2,3}", x.split("/")[-1]), folders))

# presumably everything will be first converted from MSEED to SAC format (preprocessed)
# then back to MSEED for use in EqT
# and then plotting using the SAC file 

# for each folder, build a tuple of (EHE, EHZ, EHN) for every single day

all_files = []

for folder in folders:
	files = {}

	for _file in os.listdir(folder):
		net = _file.split(".")[0]
		sta = _file.split(".")[1]
		_ = _file.split(".")[2] #idk dude
		cha = _file.split(".")[3]
		_ = _file.split(".")[4]
		year = _file.split(".")[5]
		day = _file.split(".")[6]

		if day not in files:
			files[day] = [_file]
		elif day in files:
			files[day].append(_file)

	all_files.append((sta, files))
		

print(all_files)
