# load the txt file
# plot histogram of correlation values to get a feeling of the distribution
# see if there can be like a threshold
# try grouping them together

# and this is just for one station i should run the cross correlate on other stations


import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import json

import obspy
from obspy import read

file_name = "test.log"
threshold = 1e-7


# tbh not using data frames is pretty dumb but uhh 
# but it's stupid slow so
"""
sta1, sta2, cc = [], [], []

with open(file_name, "r") as f:
	for line in f:
		[_sta1, _sta2, _cc] = line.strip().split("\t")
		# np.append(sta1, _sta1)

		sta1.append(_sta1)
		sta2.append(_sta2)
		cc.append(float(_cc))"""

#sta1 = np.array(sta1)
#sta2 = np.array(sta2)
#cc = np.array(cc)

#cc = np.log10(cc)

"""no_events = len(np.unique(sta1)) + 1

unique_events = list(np.unique(sta1))
unique_events.append(sta2[-1])

image = np.zeros((no_events, no_events))
for _sta1, _sta2, _cc in zip(sta1, sta2, cc):
 	image[unique_events.index(_sta1), unique_events.index(_sta2)] = _cc
 	image[unique_events.index(_sta2), unique_events.index(_sta1)] = _cc"""

# print(cc.index(max(cc)))
# print(sta1[cc.index(max(cc))])
# print(sta2[cc.index(max(cc))])

# threshold = 10e-7 

#all_events = list(zip(sta1, sta2, cc))
#all_events.sort(key = lambda x: x[2], reverse = True)

grouped = []
"""
for c, (_sta1, _sta2, _cc) in enumerate(all_events):
	if _cc > threshold:
		if len(grouped) == 0:
			grouped.append([_sta1, _sta2])
		if all([((_sta1 not in x) and (_sta2 not in x)) for x in grouped]):
			grouped.append([_sta1, _sta2])

		for g in grouped:
			if all([(_sta1) not in x for x in grouped]) and _sta2 in g:
				g.append(_sta1)
				break
			if all([(_sta2) not in x for x in grouped]) and _sta1 in g:
				g.append(_sta2)
				break

# check unique
with open("corr_log.txt", "w") as f:
	json.dump(grouped, f)"""

with open("corr_log.txt", "r") as f:
	grouped = json.load(f)

print(grouped)

search_dir = "imported_figures/2020_085-113_TA01_sac_picks"

for line in grouped:
	# load files, plot traces together

	if len(line) > 10:
		n_plots = 10
	else:
		n_plots = len(line)

	fig, ax = plt.subplots(n_plots, 3)
	fig.suptitle(search_dir)


	for n in range(n_plots):
		_temp = line[n]
		[_sta, _year, _day, _time] = _temp.split(".")

		channels = ["EHZ", "EHN", "EHE"]

		for _n, _cha in enumerate(channels):
			st = read(os.path.join(search_dir, "{}.{}.{}.{}.{}.SAC".format(_sta, _year, _day, _cha, _time)))

			ax[n, _n].plot(st[0].data)
			ax[n, _n].set_title("{} {} {} - {}".format(_year, _day, _time, _cha))

	plt.show()

		



#TA01.2020.111.170849
#TA01.2020.112.025556




# cmap = plt.get_cmap('inferno')
# levels = MaxNLocator(nbins=15).tick_values(cc.min(), cc.max())
# norm = BoundaryNorm(levels, ncolors=cmap.N, clip = True)			
# plt.pcolormesh(image, cmap = cmap, norm = norm)
# plt.colorbar()
# plt.show()