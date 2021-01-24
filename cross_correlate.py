import obspy
from obspy import read
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from scipy import signal
import json
import sys
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

# preferably run this on the thing because uh it's a lot of number crunching


# do TA01 picks
# so cross correlate all the signals

# folder: imported_figures\2020_085-113_TA01_sac_picks 
# SAC files in 

#sac_folder_name = r"imported_figures/2020_085-113_TA01_sac_picks"
sac_folder_name = "17_jan_detections/TA01_outputs/sac_picks"
all_files = {} # organised by station, and then by day


for _file in glob.glob("{}/*.SAC".format(sac_folder_name)):
	#print(_file)	
	sta = _file.split("/")[-1].split(".")[0]
	year = _file.split(".")[1]
	day = _file.split(".")[2]
	cha = _file.split(".")[3]
	time = _file.split(".")[4]
	_id = "{}.{}.{}".format(year, day, time)

	# add to dictionary

	if sta not in all_files:
		all_files[sta] = {}

	if _id not in all_files[sta]:
		all_files[sta][_id] = [cha]
	else:
		all_files[sta][_id].append(cha)


#print(json.dumps(all_files, indent = 4))

# total objects: (sets of 3 channels)
print(all_files)

# collapse the dictionary object to only the station names

def do_the_cross(all_files):
	sta_1 = ["TA{}".format(str(i).zfill(2)) for i in range(1,20)]
	sta_2 = ["TA{}".format(str(i).zfill(2)) for i in range(1,20)]

	output_file = "test_TA01-TA19.log" # to write the correlation coefficients and time lag

	# so basically for each station-station pair,
	# for every 



	for _sta1 in (sta_1):
		for _sta2 in (sta_2):
			if _sta1 == _sta2:
				continue
			_image = np.zeros((len(list(all_files[_sta1])), len(list(all_files[_sta2]))))
			for c1, _event1 in enumerate(all_files[_sta1]):
				_filename1_z = read(os.path.join(sac_folder_name, "{}.{}.{}.{}.{}.SAC".format(_sta1, _event1.split(".")[0], str(_event1.split(".")[1]).zfill(3), "EHZ", _event1.split(".")[2])))
				_filename1_n = read(os.path.join(sac_folder_name, "{}.{}.{}.{}.{}.SAC".format(_sta1, _event1.split(".")[0], str(_event1.split(".")[1]).zfill(3), "EHN", _event1.split(".")[2])))
				_filename1_e = read(os.path.join(sac_folder_name, "{}.{}.{}.{}.{}.SAC".format(_sta1, _event1.split(".")[0], str(_event1.split(".")[1]).zfill(3), "EHE", _event1.split(".")[2])))

				for c2, _event2 in enumerate(all_files[_sta2]):
					if c2 <= c1:
						continue

					_filename2_z = read(os.path.join(sac_folder_name, "{}.{}.{}.{}.{}.SAC".format(_sta2, _event2.split(".")[0], str(_event2.split(".")[1]).zfill(3), "EHZ", _event2.split(".")[2])))
					_filename2_n = read(os.path.join(sac_folder_name, "{}.{}.{}.{}.{}.SAC".format(_sta2, _event2.split(".")[0], str(_event2.split(".")[1]).zfill(3), "EHN", _event2.split(".")[2])))
					_filename2_e = read(os.path.join(sac_folder_name, "{}.{}.{}.{}.{}.SAC".format(_sta2, _event2.split(".")[0], str(_event2.split(".")[1]).zfill(3), "EHE", _event2.split(".")[2])))

					corr_z = signal.correlate(_filename1_z[0].data, _filename2_z[0].data)
					corr_n = signal.correlate(_filename1_n[0].data, _filename2_n[0].data)
					corr_e = signal.correlate(_filename1_e[0].data, _filename2_e[0].data)
					
					test_sum = max(corr_z) + max(corr_n) + max(corr_e)
					_image[c1][c2] = test_sum

					with open(output_file, "a") as f:
						f.write("{}\t{}\t{}\n".format(_sta1 + "." + _event1, _sta2 + "." + _event2, test_sum))

			# print(_image)

			cmap = plt.get_cmap('inferno')
			levels = MaxNLocator(nbins=15).tick_values(_image.min(), _image.max())
			norm = BoundaryNorm(levels, ncolors=cmap.N, clip = True)			
			plt.pcolormesh(_image, cmap = cmap, norm = norm)
			plt.colorbar()
			plt.savefig("test_TA01-TA19.png", dpi = 300)





do_the_cross(all_files)