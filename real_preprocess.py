import pandas as pd
import os
import argparse
import datetime

def main(input_csv, output_dir):

	#output_dir = "/home/zchoong001/cy1400/cy1400-eqt/REAL/10stationtest/Pick"

	#input_csv = "/home/zchoong001/cy1400/cy1400-eqt/real_postprocessing/10stationtest.csv"

	df = pd.read_csv(input_csv)
	df["p_arrival_time"] = pd.to_datetime(df["p_arrival_time"])
	df["s_arrival_time"] = pd.to_datetime(df["s_arrival_time"]) # will it throw errors with NaN? idts? it'll just be none/NaN

	for index, row in df.iterrows():

		event_date = datetime.datetime.strftime(row.p_arrival_time, "%Y%m%d") 

		folder_name = os.path.join(output_dir, event_date)
		
		#file_name = "" # network . station . P / S

		if not os.path.exists(folder_name):
			os.makedirs(folder_name)

		start_of_day = datetime.datetime.combine(datetime.datetime.strptime(event_date, "%Y%m%d"), datetime.time.min)

		if row.p_arrival_time:

			_filename = "{}.{}.{}.txt".format(row.network, row.station, "P")

			# append to file because it might already be created

			delta_t = (row.p_arrival_time - start_of_day).total_seconds()

			output_str = "{:.2f} {:.1f} 0\n".format(delta_t, row.p_snr_ampsq_db)
			
			# do you think REAL will throw an error if it encounters a blank line...
			# i'm not going to read the C source code
			# i could compile everything into a new set of dfs but that would mean that everything is in memory
			# which is fine... so like a dictionary of dataframes for each day and it'll only print once it's done
			# i'll use that solution if REAL is dumb enough to not handle that
			# fscanf should return EOF if it can't read so it's probably fine although i will puke blood if i have to rewrite
			# 

			with open(os.path.join(folder_name, _filename), "a") as f:
				f.write(output_dir)

		if row.s_arrival_time:
			_filename = "{}.{}.{}.txt".format(row.network, row.station, "S")

			delta_t = (row.s_arrival_time - start_of_day).total_seconds()

			output_str = "{:.2f} {:.1f} 0\n".format(delta_t, row.s_snr_ampsq_db)

			with open(os.path.join(folder_name, _filename), "a") as f:
				f.write(output_dir)


		# do you think there will be edge effects across the dateline
		# with the new set of events (rerun with partial days) there could very well be? 
		# i'm going to say that it'll be referenced to the P arrival / i wonder if REAL checks that the time is less than 86400 seconds
		# probably not
		# the max duration is about 30 * 86400 seconds which justifies why he says it supports the whole month but honestly.... the behaviour is not even documented
		# 
		# get station
		# one operation each for P and S picks (in case there's only one of them)
		# 
		# time from ZERO (00:00:00 hrs of that day), then the computed SNR, and maximum amplitude (0) because i didn't remove instrument response 
		# 
		# which i could tbh but it's not a priority now
		# 
		



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("input_csv", help = "compiled EQT output csv table with SNR and pick times")
	parser.add_argument("output_dir", help = "Pick folder to create folders in for using REAL")

	args = parser.parse_args()

	main(args.input_csv, args.output_dir)
