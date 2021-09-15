import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

import subprocess

def parse_log():
	customfilter = "imported_figures/aceharray_2020_1jul_allcsv/wc_log_aceharray_2020_customfilter.txt"
	#normalmerge ="imported_figures/wc_log_aceharray_2020_mergefiltered.txt"
	#rawmerge = "imported_figures/wc_log_aceharray_2020_mergeraw.txt"

	text = ""

	df = pd.DataFrame()


	def get_dict(input_file):

		with open(input_file, "r") as f:

			data = {}

			for c, line in enumerate(f):

				if line == "":
					continue
				line = line.strip()

				n_detections = int(line.split(" ")[0]) - 1
				fp = line.split(" ")[1]

				sta = fp.split('/')[-2].split("_")[0]

				#print(sta, n_detections)

				if sta not in data:
					data[sta] = n_detections
				else:
					data[sta] += n_detections

		return data

	# raw = get_dict(rawmerge)
	# normal = get_dict(normalmerge)
	custom = get_dict(customfilter)


	# load station_info.dat and add the no. of detections in another column

	coords = []
	with open("station_info.dat") as f:
		for line in f:

			stuff = [x for x in line.strip().split("\t") if x != ""]

			coords.append(stuff)

	df = pd.DataFrame(columns = ["sta", "lon", "lat"], data = coords)
	#print(df)

	# match coords with station (could be a merge probably)

	for index, row in df.iterrows():
		try:
			df.at[index, 'custom_count'] = custom[row.sta]
		except: # not found error
			df.at[index, 'custom_count'] = 0

	#df.to_csv("gmt/aceh/array_sta.csv", index = False)

	day_df = pd.read_csv("fulldays_2020uptime_1jul.csv")
	day_df = day_df.rename(columns = {"Unnamed: 0": "sta", "no. of days of fullday data":"fulldays"})

	df = df.merge(day_df, on = "sta")
	for index, row in df.iterrows():
		try:
			df.at[index, 'counts_per_day'] = row["custom_count"] / row["fulldays"]
		except ZeroDivisionError:
			df.at[index, 'counts_per_day'] = 0


	df.sort_values(by = ["custom_count"], inplace = True, ascending = False, ignore_index = True)

	df.fulldays.plot.hist()
	plt.show()

def summary():

	search_str = ["merge_raw.csv", "merge_filtered.csv", "merge_filtered_snr_customfilter.csv"]

	yes = []

	for i in search_str:
		line_count = 0

		file_list = [str(p) for p in Path("imported_figures/aceharray_2020_7jul_sacpicks").rglob(i)]

		for fname in file_list:

			line_count += int(subprocess.check_output(["wc", "-l", fname]).decode("utf8").split()[0]) - 1

		print(i, line_count)

	search_str = ["keepPS_raw.csv", "keepPS_filtered.csv"]

	for i in search_str:
		line_count = 0

		file_list = [str(p) for p in Path("imported_figures/13jul_keepPS").rglob(i)]

		for fname in file_list:

			line_count += int(subprocess.check_output(["wc", "-l", fname]).decode("utf8").split()[0]) - 1

		print(i, line_count)


	# merge_raw

	# merge_filtered

	# merge_filtered_snr_customfilter

	# keepPS_raw

	# keepPS_filtered

	




def rearrange_uptime():
	csv_list = "imported_figures/all_aceh_sac.csv"

	# for each station in station list, get no. of rows that are 
	# full day, matching that station, and in 2020
	# 
	df = pd.read_csv(csv_list)

	station_list = []

	with open("station_info.dat", "r") as f:

		for line in f:
			station_list.append(line.strip().split("\t")[0])

	df_list = {}

	count = {}
	for c, sta in enumerate(station_list):
		df_list[sta] = df[(df["station"] == sta) & (df["year"] == 2020) & (df["fullday"])]["jday"].unique()
		count[sta] = df[(df["station"] == sta) & (df["year"] == 2020) & (df["fullday"])]["jday"].nunique()
		

	# print(df_list)
	# all_days = pd.DataFrame.from_dict(df_list, orient = 'index')

	# all_days = all_days.transpose()

	# all_days.to_csv("all_aceh_sac_2020uptime_1jul.csv")

	counts = pd.DataFrame.from_dict(count, orient = 'index', columns = ['no. of days of fullday data'])

	print(counts)

	counts.to_csv("fulldays_2020uptime_1jul.csv")


def parse_picks():

	search_folder = "/home/zy/cy1400-eqt/imported_figures/aceharray_2020_1jul_allcsv"

	search_term = "merge_filtered_snr_customfilter.csv"

	csv_list = [str(p) for p in Path(search_folder).rglob(search_term)]

	p_snr_db = []
	s_snr_db = []

	PS_timing = []

	for csv in csv_list:
		df = pd.read_csv(csv)

		df["p_arrival_time"] = pd.to_datetime(df["p_arrival_time"])
		df["s_arrival_time"] = pd.to_datetime(df["s_arrival_time"])

		df["PS_time"] = (df["s_arrival_time"] - df["p_arrival_time"])

		_pstimes = [x.total_seconds() for x in df["PS_time"].tolist()]

		p_snr_db.extend(df["p_snr_ampsq_db"].tolist())
		s_snr_db.extend(df["s_snr_ampsq_db"].tolist())

		PS_timing.extend(_pstimes)


	# HISTOGRAM FOR PS TIMING
	# -----------------------
	plt.xlabel("PS differential time")
	plt.ylabel("No. of picked events")	
	plt.hist((PS_timing), bins = np.logspace(-1, 2, num = 12))
	plt.xscale('log')
	plt.show()
	
	plt.clf()

	# HISTOGRAM FOR P_SNR_DB

	plt.xlabel("P_SNR (db)")
	plt.ylabel("No. of picks")
	plt.hist(p_snr_db)
	plt.show()

	plt.clf()

	plt.xlabel("S_SNR (db)")
	plt.ylabel("No. of picks")
	plt.hist(s_snr_db)
	plt.show()

def plot_uptime():
	df = pd.read_csv("imported_figures/08jul_aceh_summary_uptime.csv")

	df["total_days"].plot.hist()
	plt.show()

##
## 
## 
## #############################################
##

summary()