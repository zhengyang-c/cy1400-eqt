from subprocess import check_output
import datetime
import pandas as pd
import argparse


def sac_file_checker(input_csv, output_csv, sac_csv, output_folder):

	s_df = pd.read_csv(sac_csv)

	# this is the matcher function

	df = pd.read_csv(input_csv)

	df["event_start_time"] = pd.to_datetime(df["event_start_time"])
	df["local_file_root"] = output_folder



	for index, row in s_df.iterrows():
		s_df.at[index, "start_dt"] = datetime.datetime.strptime("{} {}".format(row.kzdate, row.kztime), "%Y/%m/%d %H:%M:%S.%f")

	for index, row in df.iterrows():
		# get station
		# this feel like a n^2 search omg this is going to be so slow
		jday = int(datetime.datetime.strftime(row.event_start_time, "%j"))
		# filter by station, jday
		# see number of candidates

		_df = s_df[((s_df["jday"] == jday) & (s_df["station"] == row.station))]

		# if there's more than 1 option, need to tie break
		# want to save the file to look in i.e. 
		# there's a lot of duplicate work done e.g. a lot of common station days but at the same time....
		# it's more of a O(n) since the second search just uses filtering and is not a brute force search which is still acceptable

		# want to check that the time stamp is within the kzdate and time

		print(row.station, jday)

		for s_index, s_row in _df.iterrows():
			_df.at[s_index, "is_within"] = (((row.event_start_time - s_row.start_dt).total_seconds()) < s_row.E) and (((row.event_start_time - s_row.start_dt).total_seconds()) > s_row.B) 

			print("event_start_time", row.event_start_time)
			print("row_start_time", s_row.start_dt)
			print("is within: ", (((row.event_start_time - s_row.start_dt).total_seconds()) < s_row.E - 125) and (((row.event_start_time - s_row.start_dt).total_seconds()) > s_row.B - 30))

		_fdf = _df[_df["is_within"] == True]


		print(_fdf["start_dt"])
		# if len(_fdf) != 3:
		# 	# we have a problem, log and fix it later (?)
		# 	# or attempt to search for other jdays

		# 	with open("log/sac_timing.txt", "a") as f:
		# 		#print(row.event_start_time, row.station)
		# 		f.write("{} {}\n".format(row.event_start_time, row.station))

			

		search_term = _fdf["filepath"].iloc[0]

		df.at[index, "source_file"] = search_term



	df = df.merge(s_df, how = "left", left_on = "source_file", right_on = "filepath", suffixes = ("", "_sac")) 

	for index, row in df.iterrows():
		for x in [".EHE.", ".EHN.", ".EHZ."]:
			if x in row.source_file:
				search_term = row.source_file.replace(x, ".EH*.")
				break
		df.at[index, "source_file"] = search_term


	df.to_csv(output_csv, index = False)


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("input_csv")
	ap.add_argument("output_csv")
	ap.add_argument("sac_csv")
	ap.add_argument("output_folder")

	args = ap.parse_args()

	sac_file_checker(args.input_csv, args.output_csv, args.sac_csv, args.output_folder)
