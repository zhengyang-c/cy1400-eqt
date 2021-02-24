import argparse
import pandas as pd
import obspy
from obspy import read
import glob
import os


def plot(data_parent_folder_name, detection_folder_name):

	for csv_file in glob.glob("{}/*/*.csv".format(detection_folder_name)):

		print(csv_file)
		df = pd.read_csv(csv_file)

		sta = csv_file.split("/")[1].split("_")[0]

		csv_dir = "/".join(csv_file.split("/")[:-1])

		save_dir = "sac_picks"

		if not os.path.exists(os.path.join(csv_dir, save_dir)):
			os.makedirs(os.path.join(csv_dir, save_dir))
			
		pick_date_times = []

		for p_arrival in df['event_start_time']:
			pick_date_times.append(datetime.datetime.strptime(p_arrival.split(".")[0], "%Y-%m-%d %H:%M:%S"))

		#for p_arrival in pick_date_times:

		for _sta, _sta_details in all_files:
			if _sta == sta:
				sta_details = copy.deepcopy(_sta_details)
				break

		assert sta_details

		for c, p_arrival in enumerate(pick_date_times):
			# get year and julian day
			prev_year_day = ""
			_year = p_arrival.strftime("%Y")
			_day = p_arrival.strftime("%j")
			pick_year_day =  _year + "_" + _day

			print(sta_details[pick_year_day])

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
					tr.stats.stla, tr.stats.stlo = station_list[sta]["coords"][1], station_list[sta]["coords"][2], 
					#print(tr.stats.stla)
					#print(tr.stats.stlo)
					tr.write(os.path.join(csv_dir, save_dir, "{}.{}.{}.{}.{}.SAC".format(sta, _year, _day, tr.stats.channel, p_arrival.strftime("%H%M%S"))), format = "SAC")

			# trim a bit more then plot ?
			_st.trim(start_UTC_time + delta_t - 5, start_UTC_time + delta_t + 10)
			png_file = "{}.{}.{}.{}.png".format(sta, _year, _day, p_arrival.strftime("%H%M%S"))
			if not os.path.exists(os.path.join(csv_dir, save_dir, png_file)):
				_st.plot(outfile = os.path.join(csv_dir, save_dir, png_file), size = (800, 600))


			prev_year_day = pick_year_day


parser = argparse.ArgumentParser()

parser.add_argument('sac_folder')
parser.add_argument('input_folder')

args = parser.parse_args()

plot(args.sac_folder, args.input_folder)

