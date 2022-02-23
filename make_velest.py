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
import os
import argparse
import pandas as pd
from utils import parse_station_info
import fortranformat as ff

def main():

	N_EVENTS = 20

	# do the station file first since it's easiest
	station_info = parse_station_info("csi/new_station_info_elv.dat")
	phase_file = "real_postprocessing/rereal_all/all_rereal_events.pha"
	mag_file = "imported_figures/all_rereal_mags.csv"

	for key in list(station_info.keys()):
		if len(key) == 3:
			station_info[key + "Z"] = station_info.pop(key)

	# this is because VELEST is written with station names of 4 characters, so just append a Z at the back 

	output_folder = "velest"	
	output_root = "master_real_test"
	output_path = os.path.join(output_folder, output_root)

	
	outputs = {
		"station_file": output_path + ".sta",
		"event_file": output_path + ".events",
		"model_file": output_path + ".model",
		"control_file": os.path.join(output_folder, "velest.cmn")
	}

	params = {
		"station":output_root + ".sta",
		"event":output_root + ".events",
		"model":output_root + ".model",
		"output": output_root + ".output",
		"n_events": N_EVENTS,
		"station_corr": output_root + ".stacorr",
		"hypo_output": output_root + ".hypo",
		"residual": output_root + ".res",
	}

	def write_station(station_info):
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

		return sta_str


	# need to determine the ICC number, which probably doesn't matter so much (?)

	# TA19 has the most detections, so it should have the highest ICC number
	# assigning the same ICC numbers: computational efficiency not that? important? since VELEST isn't that slow
	# i.e. can give TA19 the highest ICC number first

	# then do the model file

	def write_model():
		initial_p_model = [(-3, 5.2), (0, 5.2), (2.5, 5.35), (5, 5.5), (7.5, 5.75), (10, 6), (15, 6.3), (20, 6.6), (30, 7.6), (40, 8), (50, 8.1), (70, 8.2), (90, 8.2)]

		metadata = "test"
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

		return mod_str


	def write_control_file(params):
		ctrl_str = ""

		# lat lons

		ctrl_str += "test\n4.8 96 1 0.000 0 0.00 0\n"
		ctrl_str += "{0} 0 0.0\n0 0\n100 0 0.0 0.20 5.00 0\n2 0.8 1.73 1\n0.01 0.01 0.01 1.0 0.01\n0 0 0 1 0\n1 1 1 0\n0 0 0 0 0 0 0\n0.010 3 1\n{1}\n{2}\n\n\n\n\n\n{3}\n\n{4}\n\n{5}\n{6}\n\n\n\n\n\n\n\n{7}".format(
			params["n_events"],
			params["model"],
			params["station"],
			params["event"],
			params["output"],
			params["hypo_output"],
			params["station_corr"],
			params["residual"],
		)
		print(ctrl_str)
		return ctrl_str


	def write_event(mag_file):
		# event file....

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

					if len(data[0]) == 3: #station name
						_sta = data[0] + "Z"
					else:
						_sta = data[0]

					event_buffer.append(g.write([_sta, data[3], 1, float(data[1])]))
			if len(event_buffer) != 0:
				# print("print last")
				for i in event_buffer:
					out_str += i
				out_str += " " * 10 + "\n"
			out_str += "\n"

		return out_str 
	sta_str = write_station(station_info)
	mod_str = write_model()
	out_str = write_event(mag_file)
	ctrl_str = write_control_file(params)

	with open(outputs["station_file"], "w") as f:
		f.write(sta_str)
	with open(outputs["model_file"], "w") as f:
		f.write(mod_str)
	with open(outputs["event_file"], "w") as f:
		f.write(out_str)
	
	with open(outputs["control_file"], "w") as f:
		f.write(ctrl_str)
	

if __name__ == "__main__":

	ap = argparse.ArgumentParser()
	main()