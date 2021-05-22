import argparse
import pandas as pd
import obspy
from obspy import read
import glob
import os
import datetime


def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

def plot(data_parent_folder_name, sta, detection_folder_name):

	for csv_file in glob.glob("{}/*/*.csv".format(detection_folder_name)):

		print(csv_file)
		df = pd.read_csv(csv_file)

		

		csv_dir = "/".join(csv_file.split("/")[:-1])

		save_dir = "sac_picks"

		if not os.path.exists(os.path.join(csv_dir, save_dir)):
			os.makedirs(os.path.join(csv_dir, save_dir))
			
		pick_date_times = []

		# not actually the p_arrival but i switched gears while writing this so

		for p_arrival in df['event_start_time']:
			pick_date_times.append(str_to_datetime(p_arrival))

		#for p_arrival in pick_date_times:


		for c, p_arrival in enumerate(pick_date_times):
			# get year and julian day
			prev_year_day = ""
			_year = p_arrival.strftime("%Y")
			_day = p_arrival.strftime("%j")
			pick_year_day =  _year + "_" + _day

			if c == 0:
				st = read(os.path.join(data_parent_folder_name, sta,"*{}.{}.*".format(_year, _day))) 

			elif not prev_year_day == pick_year_day: # different year_day, so reload new
				st.clear()
				st = read(os.path.join(data_parent_folder_name, sta,"*{}.{}.*".format(_year, _day))) 

			# else, it's already loaded, can start trimming
			_st = st.copy()

			start_UTC_time = _st[0].stats.starttime
			delta_t = obspy.UTCDateTime(p_arrival) - start_UTC_time
			_st.trim(start_UTC_time + delta_t - 30, start_UTC_time + delta_t + 120)


			# write SAC file 
			for tr in _st:
				if not os.path.exists(os.path.join(csv_dir, save_dir, "{}.{}.{}.{}.{}.SAC".format(sta, _year, _day, p_arrival.strftime("%H%M%S"), tr.stats.channel))):

					tr.write(os.path.join(csv_dir, save_dir, "{}.{}.{}.{}.{}.SAC".format(sta, _year, _day, p_arrival.strftime("%H%M%S"),  tr.stats.channel),), format = "SAC")

			# trim a bit more then plot ?
			_st.trim(start_UTC_time + delta_t - 5, start_UTC_time + delta_t + 10)
			png_file = "{}.{}.{}.{}.png".format(sta, _year, _day, p_arrival.strftime("%H%M%S"))
			if not os.path.exists(os.path.join(csv_dir, save_dir, png_file)):
				_st.plot(outfile = os.path.join(csv_dir, save_dir, png_file), size = (800, 600))


			prev_year_day = pick_year_day

if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument('sac_folder')
	parser.add_argument('sta')
	parser.add_argument('input_folder')
	parser.add_argument('-t', '--time', type = str, help = "file path to append to to")

	args = parser.parse_args()



	start_time = datetime.datetime.now()

	plot(args.sac_folder, args.sta, args.input_folder)

	end_time = datetime.datetime.now()

	time_taken = (end_time - start_time).total_seconds()

	if args.time:
		with open(args.time, "a") as f:
			f.write("plot_eqt,{} days,{},{}\n".format(args.input_folder, datetime.datetime.strftime(start_time, "%Y%m%d %H%M%S"),time_taken))



