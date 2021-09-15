import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

FILE_NAME = "Deployed-2020-03-TA01-TA19_availability.txt"
FOLDER_NAME = "TA01-TA019_2020_85-115 ish"

dates = []

with open(os.path.join(FOLDER_NAME, FILE_NAME), "r") as f:
	for line in f:
		dates.append(line.strip())


# for each station name in the dictionary, have a list. 
# later iterate by keys and produce an image with labels. green = up and all 3 channels available.
# red = 
all_stations = {}

# assume year is the same because i am lazy as balls
for file in dates:
	_year = file.split(".")[5]
	_day = int(file.split(".")[6])
	_station = file.split(".")[1]
	_starttime = file.split(".")[7]
	_channel = file.split(".")[3]

	if _station not in all_stations:
		all_stations[_station] = {_day: {"channels": [_channel], "start_time": [_starttime]}}
	elif _day not in all_stations[_station]:
		all_stations[_station][_day] = {"channels": [_channel], "start_time": [_starttime]}
	else:
		all_stations[_station][_day]["channels"].append(_channel)
		all_stations[_station][_day]["start_time"].append(_starttime)

#print()

#print(all_stations)
no_days = max([len(all_stations[k]) for k in all_stations])
no_stations = len(list(all_stations.keys()))
image = np.zeros((no_stations, no_days))
print(image.shape)

first_day = min([min(list(all_stations[s])) for s in all_stations])
last_day = max([max(list(all_stations[s])) for s in all_stations])
print(first_day)
print(last_day)


for c, station in enumerate(list(all_stations)):
	for day in all_stations[station]:
		#print(all_stations[station][day]["start_time"])
		#print(all([all_stations[station][day]["start_time"][i] == "000000" for i in range(3)]))
		if len(all_stations[station][day]["channels"]) == 3 and all([all_stations[station][day]["start_time"][i] == "000000" for i in range(3)]):
			image[c, day - first_day] = 1

plt.figure(figsize=(12,6), dpi = 150)
plt.yticks(np.arange(no_stations) + 0.5, list(all_stations), fontsize = 8)
plt.xticks(np.arange(no_days) + 0.5, np.arange(first_day, last_day + 1), fontsize = 8)
plt.xlabel("Julian days")
plt.ylabel("Station name")
plt.pcolormesh(image, edgecolors ='k', linewidth=2)
plt.savefig(FILE_NAME + ".png")
