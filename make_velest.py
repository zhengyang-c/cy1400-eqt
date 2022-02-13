"""
I too, enjoy reinventing the wheel

PURPOSE
-------

Generate MOD, STA, and CNV file for use in VELEST.

INPUT
-----

STATION LOCATION FILE:

tab separated,
station_name | lon | lat | elv

earthquake event file:
a CSV file with the needed columns

model file:


"""
import argparse
import pandas as pd
from utils import parse_station_info
import fortranformat as ff

def main():

	N_EVENTS = 20

	# do the station file first since it's easiest
	station_info = parse_station_info("csi/new_station_info_elv.dat")

	for key in list(station_info.keys()):
		if len(key) == 3:
			station_info[key + "Z"] = station_info.pop(key)
	

	outputs = {
		"station_file": "velest/test.sta",
		"event_file": "velest/test.cnv",
		"model_file": "velest/test.mod",
	}

	icc = {}
	c = 0
	for station in station_info:
		if station != "TA19":
			icc[station] = c
			c += 1
	icc["TA19"] = len(station_info)

	h = ff.FortranRecordWriter('(a4,f7.4,a1,1x,f8.4,a1,1x,i4,1x,i1,1x,i3,1x,f5.2,2x,f5.2,3x,i1)')

	sta_str = "(a4,f7.4,a1,1x,f8.4,a1,1x,i4,1x,i1,1x,i3,1x,f5.2,2x,f5.2)\n"
	for station in station_info:

		_str = (h.write([station,station_info[station]["lat"],"N", station_info[station]["lon"], "E", int(station_info[station]["elv"]), 1, icc[station], 0, 0, 1]))

		sta_str += _str + "\n"
		# sta_str += "{}{:.5f}N {:.5f}E {} 1 {} 0.00 0.00 1\n".format(
		# 	station.ljust(4),
		# 	station_info[station]["lat"],
		# 	station_info[station]["lon"],
		# 	int(station_info[station]["elv"]),
		# 	icc[station]
		# )

	sta_str += "\n"


	# need to determine the ICC number, which probably doesn't matter so much (?)

	# TA19 has the most detections, so it should have the highest ICC number
	# assigning the same ICC numbers: computational efficiency not that? important? since VELEST isn't that slow
	# i.e. can give TA19 the highest ICC number first

	# then do the model file
	initial_p_model = [(-3, 5.2), (0, 5.2), (2.5, 5.35), (5, 5.5), (7.5, 5.75), (10, 6), (15, 6.3), (20, 6.6), (30, 7.6), (40, 8), (50, 8.1), (70, 8.2), (90, 8.2)]

	metadata = "hello world"
	mod_str = "{}\n{}        vel,depth,vdamp,phase (f5.2,5x,f7.2,2x,f7.3,3x,a1)\n".format(metadata, len(initial_p_model))

	h = ff.FortranRecordWriter('(f5.2,5x,f7.2,2x,f7.3,3x,a1)')

	vpvs = 1.73

	c = 1
	for i in initial_p_model:
		if c:
			# mod_str += "{:.2f}     {:.2f}  001.00   P-VELOCITY MODEL\n".format(i[1], i[0])
			temp_str = h.write([i[1], i[0], 1, "P"]) + "\n"
			temp_str = temp_str.replace("1.000", "001.00")
			mod_str += temp_str
			c = 0
		else:
			mod_str += h.write([i[1], i[0], 1.0]) + "\n"
	c = 1
	mod_str += "{}\n".format(len(initial_p_model))
	for i in initial_p_model:
		if c:
			temp_str = h.write([i[1], i[0], 1, "S"]) + "\n"
			temp_str = temp_str.replace("1.000", "001.00")
			mod_str += temp_str
			c = 0
		else:
			mod_str += h.write([i[1], i[0], 1.0]) + "\n"



	# event file....
	phase_file = "master_csv/phasefiles/master_real.pha"
	mag_file = "master_csv/master_merged_REAL_mags.csv"

	mdf = pd.read_csv(mag_file)

	# just modify the first line

	# seems like the 6 phases per line is mandatory

	# (3i2.2,1x,2i2.2,1x,f5.2,1x,f7.4,a1,1x,f8.4,a1,f7.2,f7.2,i2...)
	h = ff.FortranRecordWriter('(3i2.2,1x,2i2.2,1x,f5.2,1x,f7.4,a1,1x,f8.4,a1,f7.2,f7.2,i2)')

	g = ff.FortranRecordWriter('(a4,a1,i1,f6.2)')

	out_str = ""
	c = 0
	start_flag = True
	event_buffer = []
	with open(phase_file, "r") as f:
		for line in f:
			# print(event_buffer)
			data = [x.strip() for x in line.split(" ") if x != ""]
			if line[0] == "#":
				if start_flag:
					pass
				else:
					for i in event_buffer:
						out_str += i

					out_str +=  (6 - len(event_buffer)) * 12 * " "
					out_str += "\n\n"	
				event_buffer = []

				if c == N_EVENTS:
					break

				event_id = int(data[-1])

				if len(mdf[mdf["ID"] == event_id]) == 0:
					event_mag = 0
				else:
					event_mag = mdf[mdf["ID"] == event_id]["m_l"].sum()

				#out_str += "{}{}{} {}{} {} {}N {}E    {}    {:.2f} 1\n".format(data[1][2:4], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], event_mag)
				out_str += h.write([int(data[1][2:4]), int(data[2]), int(data[3]), int(data[4]), int(data[5]), float(data[6]), float(data[7]), "N", float(data[8]), "E", float(data[9]), event_mag, 1])
				out_str += "\n"
				c += 1
			else:
				start_flag = False
				if len(event_buffer) < 6:
					pass
				else:
					# print("writing")
					for i in event_buffer:
						out_str += i
					out_str += "\n"
					event_buffer = []
				if len(data[0]) == 3:
					_sta = data[0] + "Z"

				event_buffer.append(g.write([_sta, data[3], 1, float(data[1])]))
		if len(event_buffer) != 0:
			# print("print last")
			for i in event_buffer:
				out_str += i
			out_str += " " * 10 + "\n"
		out_str += "\n"


	with open(outputs["station_file"], "w") as f:
		f.write(sta_str)
	with open(outputs["model_file"], "w") as f:
		f.write(mod_str)
	with open(outputs["event_file"], "w") as f:
		f.write(out_str)
	

if __name__ == "__main__":
	main()