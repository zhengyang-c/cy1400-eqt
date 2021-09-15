# plot histogram of no. of detections per run

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
import pandas as pd
from datetime import datetime
from dateutil import parser

filename = "imported_figures/21mar_default_merge/21mar_default_filtered.csv"

df = pd.read_csv(filename)


times = [int(x[11:13]) for x in list(df['event_start_time'])]
#plt.title("no. of events by UTC hour for TA19, March 25 to Apr 17 2020")
freqs, bins = np.histogram(times, bins = np.arange(0,25))
plt.clf()

print(bins)
print(freqs)

print(freqs)
plt.hist(freqs)
plt.show()

with open("plot_data/eventhourhistogram_21marmerged.txt", "w") as f:
	for c in range(len(freqs)):
		f.write("{}\t{}\n".format(bins[c], freqs[c]))



#plt.xticks(np.arange(0,24))
#plt.xlabel("Hour (UTC)")
#plt.ylabel("No. of events")
#plt.savefig("plots/events_by_hour_histogram.pdf", dpi = 300)

# bin by hour and plot 



"""ts = []

for i in range(len(times) - 1):
	ts.append((times[i+1] - times[i]).total_seconds())
#print(ts)

plt.hist(ts)
plt.show()"""




"""data = []
with open("log/multi-run.txt", "r") as f:
	for line in f:
		data.append(int(line.strip()))
#print(data)
print(np.mean(data))
print(np.std(data))"""

# no. of detections; 763 +/- 14
#plt.hist(data)
#plt.show()

# -----------------------
# read csv file, histogram the events by hours
# also find the coincidence statistics

