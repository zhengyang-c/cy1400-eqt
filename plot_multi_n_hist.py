"""
multiple runs will give diff no. of detections

plot this distribution as a histogram
"""

import numpy as np
from pathlib import Path
import pandas as pd
import random
import matplotlib.pyplot as plt

from utils import centre_bin

csv_folder = "/home/zy/cy1400-eqt/imported_figures/21mar_default_merge/csv_collection"

all_csv_files = [str(p) for p in Path(csv_folder).rglob("*csv")]

file_lengths = []

for csv_file in all_csv_files:
	with open(csv_file, "r") as f:
		for i, _ in enumerate(f):
			pass
		file_lengths.append(i) # this is ok because there is a header row for csv files

out_file = "plot_data/10apr_multirun_variance.txt"

print(np.mean(file_lengths))
print(np.std(file_lengths))

hist, bins = np.histogram(file_lengths, bins = np.arange(740, 790, 5))

#centre
bins = centre_bin(bins)

with open(out_file, "w") as f:
	for c, _ in enumerate(hist):
		f.write("{}\t{}\n".format(bins[c], hist[c]))