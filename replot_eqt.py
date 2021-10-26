import argparse
import pandas as pd
import glob
import os
import datetime
import subprocess
import matplotlib.pyplot as plt
import time

import obspy

from pathlib import Path


def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")


def sac_plotter():

	# output_file is the bashscript to be kept inside the merged folder
	# it is generated and when run it will do all the necessary cutting 

	csv_file = "julaug_customfilter_matched_patch.csv"

	try:
		df = pd.read_csv(csv_file)	
	except FileNotFoundError:
		print("plot eqt: no files found")	
		return 0

	#print(sac_df)

	csv_dir = "/".join(csv_file.split("/")[:-1])


	save_dir = "julaug_test/"	
	if not os.path.exists(os.path.join(csv_dir, save_dir)):
		os.makedirs(os.path.join(csv_dir, save_dir))

		

	df['event_start_time'] = pd.to_datetime(df['event_start_time'])

	df['start_dt'] = pd.to_datetime(df['start_dt'])

	for index, row in df.iterrows():
		for x in [".EHE.", ".EHN.", ".EHZ."]:
			if x in row.filepath:
				search_term = row.filepath.replace(x, ".EH*.")
				break
		df.at[index, "filepath"] = search_term

	write_str = "#!/bin/sh\n"
	plot_str = "#!/bin/sh\n"

	cut_file = os.path.join(csv_dir, "cut.sh")
	plot_file = os.path.join(csv_dir, "plot.sh")

	with open(cut_file, "w") as f:		

		for index, row in df.iterrows():

			sta = row.station

			event_dt = row.event_start_time

			year = (datetime.datetime.strftime(event_dt, "%Y"))
			jday = (datetime.datetime.strftime(event_dt, "%j"))

			year_day = year + "."+ jday # need string representation

			#_df = (sac_df[(sac_df.station == sta) & (sac_df.year == int(year)) & (sac_df.jday == int(jday))])

			# load routine
			#

			sac_source = row["filepath"]

			timestamp = (datetime.datetime.strftime(event_dt, "%H%M%S"))

			event_id = "{}.{}.{}".format(sta, year_day, timestamp)

			f1 = os.path.join(csv_dir, save_dir, event_id + ".EHE.SAC")
			f2 = os.path.join(csv_dir, save_dir, event_id + ".EHN.SAC")
			f3 = os.path.join(csv_dir, save_dir, event_id + ".EHZ.SAC")

			png_id = event_id + ".png"
			ps_id = event_id + ".ps"

			#start_of_day = datetime.datetime.combine(datetime.datetime.strptime(year_day, "%Y.%j"), datetime.time.min)

			start_of_file = ""

			start_time = (event_dt - row.start_dt).total_seconds() - 30
			end_time = (event_dt - row.start_dt).total_seconds() + 120


			#printf "cut $start_time $end_time\nr $fp/*$sac_id*SAC\nwrite SAC $f1 $f2 $f3\nq\n"
			#printf "sgf DIRECTORY /home/zchoong001/cy1400/cy1400-eqt/temp OVERWRITE ON\nqdp off\nr $f1 $f2 $f3\nbp p 2 n 4 c 1 45\nq\n"
			#
			# one printf to cut sac file, another to plot
			# 
			
			

			write_str += "printf \"cut {:.2f} {:.2f}\\nr {}\\nwrite SAC {} {} {}\\nq\\n\" | sac\n".format(start_time, end_time, sac_source, f1, f2, f3)
			
			plot_str += "printf \"sgf DIRECTORY {0} OVERWRITE ON\\nqdp off\\nr {1} {2} {3}\\nbp p 2 n 4 c 1 45\\nbd sgf\\np1\\nsgftops {0}/f001.sgf {0}/sac_picks/{4}\\nq\\n\" | sac\n".format(csv_dir, f1,f2,f3, ps_id)

			#plot_str += "convert {0}/f001.ps -rotate 90 -density 300 {0}/sac_picks/{1}\n".format(csv_dir, png_id)

			#plot_str += "convert {0}/sac_picks/{1} -background white -alpha remove -alpha off {0}/sac_picks/{1}\n".format(csv_dir, png_id)


		f.write(write_str)

	with open(plot_file, 'w') as f:
		f.write(plot_str)

	# call subprocess
	time.sleep(1)
	os.chmod(cut_file, 0o775)
	time.sleep(1)
	os.chmod(plot_file, 0o775)


def header_writer():


	csv_file ="julaug_customfilter_matched_patch.csv"
	try:
		df = pd.read_csv(csv_file)
	except FileNotFoundError:
		print("header_writer: file not found")
		return 0

	df['event_start_time'] = pd.to_datetime(df['event_start_time'])
	df['p_arrival_time'] = pd.to_datetime(df['p_arrival_time'])
	df['s_arrival_time'] = pd.to_datetime(df['s_arrival_time'])
	df['event_end_time'] = pd.to_datetime(df['event_end_time'])

	df['start_dt'] = pd.to_datetime(df['start_dt'])

	for index, row in df.iterrows():
		for x in [".EHE.", ".EHN.", ".EHZ."]:
			if x in row.filepath:
				search_term = row.filepath.replace(x, ".EH*.")
				break
		df.at[index, "filepath"] = search_term

	
	csv_dir = "julaug_test"

	output_file = os.path.join(csv_dir, "write_headers.sh")

	with open(output_file, 'w') as f:
		f.write("#!/bin/sh\n")

		for index, row in df.iterrows():

			year_day = datetime.datetime.strftime(row.event_start_time, "%Y.%j")


			start_of_file = row.start_dt

			timestamp = datetime.datetime.strftime(row.event_start_time, '%H%M%S')

			if not row.p_arrival_time: # NaN
				p_diff = "-12345"

			else:
				p_diff = (row.p_arrival_time - start_of_file).total_seconds()

			if not row.s_arrival_time:
				s_diff = "-12345"

			else:
				s_diff = (row.s_arrival_time - start_of_file).total_seconds()

			if not row.event_end_time:
				end_diff = "-12345"

			else: 
				end_diff = (row.event_end_time - start_of_file).total_seconds()


			f.write("printf \"r {}\\nch A {:.2f}\\nch T0 {:.2f}\\nch F {:.2f}\\nwh\\nq\\n\" | sac\n".format(
				os.path.join(csv_dir, "*{}.{}*SAC").format(year_day, timestamp),
				p_diff,
				s_diff,
				end_diff
				))


	time.sleep(1)
	os.chmod(output_file, 0o775)

	time.sleep(1)
	subprocess.call(["{}".format(output_file)])	
	time.sleep(1)
	#subprocess.call(["{}".format(plot_file)])


sac_plotter()

header_writer()
# if __name__ == "__main__":

# 	parser = argparse.ArgumentParser()

# 	parser.add_argument('sac_csv', help = "csv file with all the source SAC files")
# 	parser.add_argument('csv_file', help = "filtered csv file generated by EQT")
# 	parser.add_argument('-t', '--time', type = str, help = "file path to append to")

# 	args = parser.parse_args()

# 	start_time = datetime.datetime.now()
# 	sac_plotter(args.sac_csv, args.csv_file)


# 	# plot(args.sac_csv, args.output_folder)

# 	end_time = datetime.datetime.now()

# 	time_taken = (end_time - start_time).total_seconds()

# 	if args.time:
# 		with open(args.time, "a+") as f:
# 			f.write("plot_eqt,{},{}\n".format(datetime.datetime.strftime(start_time, "%Y%m%d %H%M%S"),time_taken))



