from pathlib import Path
import pandas as pd
import argparse
import datetime
import json

def make_reloc_catalog(input_file, output_file):

	df = pd.DataFrame()

	# ID, LAT, LON, DEPTH, X, Y , Z (relative to centroid), EX, EY , EZ (ignore, using LSQR), YR, MO, DY, HR, MI, SC, MAG( 0), nccp, nccs (cross corr), NCTP, NCTS (catalogue p and s), RCC, RCT (residuals for cross corr and catalogue ), CID cluster id

	labels = ["ID", "LAT", "LON", "DEPTH", "X", "Y", "Z", "EX", "EY", "EZ", "YR", "MO", "DY", "HR", "MI","SC", "MAG", "NCCP", "NCCS", "NCTP", "NCTS", "RCC", "RCT", "CID"]

	with open(input_file, 'r') as f:
		for c, line in enumerate(f):
			if not len(line): continue

			#print(line)

			_data = [x.strip() for x in line.split(" ") if x != ""]

			#print(_data)

			for i in range(len(_data)):
				#print(_data[i])
				#print(labels[i])
				df.at[c, labels[i]] = _data[i]

	df.to_csv(output_file, index = False)

def filter_csv(csv_file, output_file, lon = "", lat = "", depth = ""):

	# min/max lat, min/max lon, min/max depth (6 numbers to specify)
	# want to have gmt-like specifiers (e.g. 1/4 for range 1-4)
	# 
	# hence the use will be like: -lon 1/4 -lat 2/4 -depth 5/20

	#if lon:

	minlon, maxlon, minlat, maxlat, mindep, maxdep = "", "", "", "", "", ""

	if lon:
		minlon, maxlon = lon.split('/')

		if float(minlon) > float(maxlon):
			maxlon, minlon = minlon, maxlon

	if lat:
		minlat, maxlat = lat.split('/')
		if float(minlat) > float(maxlat):
			maxlat, minlat = minlat, maxlat

	if depth:
		mindep, maxdep = depth.split('/')

		if float(mindep) > float(maxdep):
			maxdep,mindep = mindep, maxdep
	# load csv


	df = pd.read_csv(csv_file)

	if minlon != "":
		df = df[df["LON"] >= float(minlon)]
	if maxlon != "":
		df = df[df["LON"] <= float(maxlon)] 
	if minlat != "":
		df = df[df["LAT"] >= float(minlat)]
	if maxlat != "":
		df = df[df["LAT"] <= float(maxlat)] 
	if mindep != "":
		df = df[df["DEPTH"] >= float(mindep)]
	if maxdep != "":
		df = df[df["DEPTH"] <= float(maxdep)] 

	df.to_csv(output_file, index = False)






def join_hypophase(search_dir, output_file, c = 0):

	filelist = [str(p) for p in Path(search_dir).rglob("hypophase.dat")] 

	filelist = sorted(filelist)

	data = []

	# just need to append everything and the ID be in order 

	for file in filelist:
		with open(file, 'r') as f:
			for line in f:
				if line[0] == "#":
					_data = line.split(" ")
					_data[-1] = f"{c:06d}\n"
					data.append(" ".join(_data))
					c += 1
				else:
					data.append(line)

	with open(output_file, 'w') as f:
		f.write("".join(data))

def join_catalog_sel(search_dir, output_file, search_file = "", n = 0):

	#search_dir = "/home/zy/Downloads/REAL_test_10station/REAL_test/Waveform"
	#print(search_file)
	if search_file == "" or search_file not in ["hypo", "cat"]:
		print("wrong search file selected, exiting")
		return 

	if search_file == "hypo":
		search_term = "hypolocSA.dat"
	elif search_file == "cat":
		search_term = "catalog_sel.txt"
	else:
		print("wrong search file selected, exiting")
		return 


	filelist = [str(p) for p in Path(search_dir).rglob(search_term)]

	df = pd.DataFrame()

	c = 0
	try:
		assert len(filelist) > 0
	except:
		raise AssertionError("No files were selected! Quitting.")

	for file in filelist:
		with open(file, 'r') as f:
			for line in f:
				data = [x for x in line.split(" ") if x != ""]

				#print(data)

				if search_file == "cat":

					df.at[c, 'YR'], df.at[c, 'MO'], df.at[c, 'DY'] = data[1:4]			
					df.at[c, 'HR'], df.at[c, 'MI'], df.at[c, 'SC'] = data[4].split(":")

					if float(df.at[c, 'SC']) < 0:
						ts = datetime.datetime.strptime("-".join(data[1:4]), "%Y-%m-%d-%H:%M")
						ts -= datetime.timedelta(seconds = float(df[c, 'SC']))
						df.at[c, 'timestamp'] = ts

					else:
						df.at[c, 'timestamp'] = datetime.datetime.strptime("-".join(data[1:5]), "%Y-%m-%d-%H-%M-%S.%f")

					df.at[c, 'LAT'] = float(data[7])
					df.at[c, 'LON'] = float(data[8])
					df.at[c, 'DEPTH'] = float(data[9])
					df.at[c, 'residual_time'] = float(data[6])
					df.at[c, 'n_p_picks'] = int(data[12])
					df.at[c, 'n_s_picks'] = int(data[13])
					df.at[c, 'n_picks'] = int(data[14])
					df.at[c, 'n_both_picks'] = int(data[15])
					df.at[c, 'station_gap'] = float(data[16])


				elif search_file == "hypo":


					df.at[c, 'YR'], df.at[c, 'MO'], df.at[c, 'DY'] = data[0:3]			
					df.at[c, 'HR'], df.at[c, 'MI'], df.at[c, 'SC'] = data[3:6]
					if float(df.at[c, 'SC']) < 0:
						ts = datetime.datetime.strptime("-".join(data[0:5]), "%Y-%m-%d-%H:%M")
						ts -= datetime.timedelta(seconds = float(df[c, 'SC']))
						df.at[c, 'timestamp'] = ts
					else:
						df.at[c, 'timestamp'] = datetime.datetime.strptime("-".join(data[0:6]), "%Y-%m-%d-%H-%M-%S.%f")

					df.at[c, 'LAT'] = float(data[6])
					df.at[c, 'LON'] = float(data[7])
					df.at[c, 'DEPTH'] = float(data[8])
					df.at[c, 'MAG'] = float(data[9])			

					df.at[c, 'n_picks'] = int(data[10])
					df.at[c, 'station_gap'] = float(data[11])
					df.at[c, 'residual_time'] = float(data[12])
					
					
				c += 1

	df = df.sort_values(by = ['timestamp'])
	df = df.reset_index(drop = True)

	for index, row in df.iterrows():
		
		df.at[index, "ID"] = "{:06d}".format(index + n)

	df.to_csv(output_file, index = False)




def convert_phase(input_file, output_file):

	#input_file = "aceh_phase.dat"
	#output_file = "aceh_phase.json"

	df = pd.DataFrame()

	def parse(x):
		contents = [y.strip() for y in x[1:].split(" ") if y != ""]

		return contents

	all_phases = {}

	with open(input_file, 'r') as f:

		_station_list = []
		row_counter = 0
		headers = ['year', 'month', 'day', 'hour', 'min', 'sec', 'lat_guess', 'lon_guess', 'dep_guess']

		for c, line in enumerate(f):

			if line[0] == "#":
				metadata = parse(line)

				_id = metadata[-1]

				all_phases[_id] = {}

				for i in range(9):
					all_phases[_id][headers[i]] = metadata[i]

				all_phases[_id]['timestamp'] = str(datetime.datetime.strptime('-'.join(metadata[0:6]), "%Y-%m-%d-%H-%M-%S.%f"))
				all_phases[_id]['data'] = []


			else:
				_data = [x.strip() for x in line.split(" ") if x != ""]

				all_phases[_id]['data'].append(_data) 

	for event_id in all_phases:
		_station_dict = {}

		for x in all_phases[event_id]['data']:
			if x[0] not in _station_dict:
				_station_dict[x[0]] = {}
			_station_dict[x[0]][x[3]] = x[1] # natural support for only P or only S picks

		all_phases[event_id]['data'] = _station_dict


	with open(output_file, 'w') as f:

		json.dump(all_phases, f, indent = 2)

	#df.to_csv(output_file, index = False)
	# build a table, with a column for stations,
	# separate each station by like some character




# for each ID, get the timestamp, get the list of stations + their original times and search for the waveforms

if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument('-i','--input', help = "generic input")
	parser.add_argument('-o', '--output',)
	parser.add_argument("-sf", '--search_file', help = "'cat' or 'hypo'", default = "")

	parser.add_argument('-cat', action = "store_true")
	parser.add_argument('-pha', action = "store_true")
	parser.add_argument('-json', action = "store_true")
	parser.add_argument('-reloc', action = "store_true")
	parser.add_argument('-f', action = "store_true")

	parser.add_argument('-lon', default = "")
	parser.add_argument('-lat', default = "")
	parser.add_argument('-depth', default = "")

	parser.add_argument("-n", "--start_n", default = 0, type = int)




	args = parser.parse_args()


	if args.cat:
		join_catalog_sel(args.input, args.output, args.search_file, args.start_n)

		# to use: Python collect_latlon.py -i INPUT_FOLDER -o OUTPUT_CSV -cat -search_file hypoloc|cat

		# hypoloc: the 'refined' output that 'should' be used
		# cat: the initial estimate from catalog_sel but is included for completion anyway
		# 

	elif args.pha:
	 	join_hypophase(args.input, args.output, args.start_n)

	elif args.reloc:
		make_reloc_catalog(args.input, args.output)

	elif args.f:
		filter_csv(args.input, args.output, lat = args.lat, lon = args.lon, depth = args.depth)

	elif args.json:
		convert_phase(args.input, args.output)