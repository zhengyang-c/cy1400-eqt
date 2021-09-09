import obspy
import pandas as pd
import subprocess
from pathlib import Path
import os
import argparse

"""
need to find the EQT_CSV picks corresponding to the SAC observations (which honestly it should be made unique but i'm not sure if there's a great way to do it)
i.e. use the df_searcher

dump the headers by loading in obspy i think? rather than using saclst
then compute the origin times, compare their difference between the EQT table

"""

def main(sac_folder, eqt_csv, output_csv, p_only = False, s_only = False, both = False, do_all = False):


	#sac_folder = "imported_figures/event_archive/000120"
	#eqt_csv = "real_postprocessing/5jul_assoc/5jul_compiled_customfilter.csv"

	# get a station list (?) or just read all
	# goal: want to know how much the times changed so i can apply a remap (?) that is file specific (?)

	#st = obspy.read(os.path.join(sac_folder, "*Z*C"))

	#_o = [st[0].stats["sac"][x] for x in ["nzyear", "nzjday", "nzhour", "nzmin", "nzsec", "nzmsec"]]
	#_o = obspy.UTCDateTime(year = _o[0], julday = _o[1], hour = _o[2], minute = _o[3], second = _o[4], microsecond = _o[5] * 1000)

	# the header 'A' will give the repicked timing (even though it's like LOC and idk what LOC is)

	# want to compare the times

	# this also means that i'll have to remember to apply the remapping everytime i need to use the arrival times
	# but that's also mostly for gridsearch
	# nbd
	# 
	df = pd.read_csv(eqt_csv)	

	if do_all:
		sac_file_list = [str(p) for p in Path(sac_folder).rglob("*SAC")]
	else:
		sac_file_list = [str(p) for p in Path(sac_folder).glob("*SAC")]


	edf = pd.DataFrame(columns = ["datetime_str", "O_delta", "A_delta", "T0_delta"])
	# e for event dataframe but also bc lazy

	# set values to 0 by default? since it's a delta

	for c, sac_file in enumerate(sac_file_list):
		#print(sac_file)
		_filename = sac_file.split("/")[-1]

		_datetime_str = ".".join(_filename.split(".")[:4])

		edf.at[c, 'datetime_str'] = _datetime_str
		#edf.at[c, 'O_delta'] = 0
		edf.at[c, 'A_delta'] = 0		
		edf.at[c, 'T0_delta'] = 0

		st = obspy.read(sac_file)

		_o = [st[0].stats["sac"][x] for x in ["nzyear", "nzjday", "nzhour", "nzmin", "nzsec", "nzmsec"]]
		_o = obspy.UTCDateTime(year = _o[0], julday = _o[1], hour = _o[2], minute = _o[3], second = _o[4], microsecond = _o[5] * 1000)

		edf.at[c, 'A_new'] = _o + st[0].stats["sac"]["a"]	
		edf.at[c, 'T0_new'] = _o + st[0].stats["sac"]["t0"]

	new_df = df.merge(edf, on ='datetime_str', how = 'inner')	

	for index, row in new_df.iterrows():
		if p_only or both:
			new_df.at[index, "A_delta"] = obspy.UTCDateTime(row.p_arrival_time) - row.A_new # i just realised the columns are dupes 
		if s_only or both:
			new_df.at[index, "T0_delta"] = obspy.UTCDateTime(row.s_arrival_time) - row.T0_new


	try:
		output_df = pd.read_csv(output_csv)
		output_df = pd.concat([output_df, new_df], ignore_index = True)

	except:
		output_df = new_df

	output_df.to_csv(output_csv, index = False, columns = ["datetime_str", "p_arrival_time", "s_arrival_time", "A_new", "A_delta", "T0_new", "T0_delta"])


if __name__ == "__main__":


	parser = argparse.ArgumentParser()
	parser.add_argument("sac_folder")
	parser.add_argument("eqt_csv")
	parser.add_argument("output_csv")
	parser.add_argument("-p", "--p_only", action = "store_true", default = False)
	parser.add_argument("-s", "--s_only", action = "store_true", default = False)
	parser.add_argument("-b", "--both", action = "store_true", default = False)
	parser.add_argument("-a", "--do_all", action = "store_true", default = False, help = "Dump P and S picks for all files (recursive search) in some folder specified by sac_folder.")

	args = parser.parse_args()

	main(args.sac_folder, args.eqt_csv, args.output_csv, p_only = args.p_only, s_only = args.s_only, both = args.both, do_all = args.do_all)

	