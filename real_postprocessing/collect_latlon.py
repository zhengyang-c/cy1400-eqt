from pathlib import Path
import pandas as pd
import argparse
import datetime

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

	if lat:
		minlat, maxlat = lat.split('/')

	if depth:
		mindep, maxdep = depth.split('/')
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






def join_hypophase(search_dir, output_file):

	filelist = [str(p) for p in Path(search_dir).rglob("hypophase.dat")] 

	filelist = sorted(filelist)



	#print(filelist)


	data = []

	# just need to append everything and the ID be in order 

	c = 0
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




		

def join_catalog_sel(search_dir, output_file, search_file = ""):

	#search_dir = "/home/zy/Downloads/REAL_test_10station/REAL_test/Waveform"

	if search_file == "" or search_file not in ["hypoloc", "cat"]:
		print("wrong search file selected, exiting")
		return 

	if search_file == "hypoloc":
		search_term = "hypolocSA.dat"
	elif search_file == "cat":
		search_term = "catalog_sel.txt"
	else:
		print("wrong search file selected, exiting")
		return 


	filelist = [str(p) for p in Path(search_dir).rglob(search_term)]

	df = pd.DataFrame()

	c = 0
	for file in filelist:
		with open(file, 'r') as f:
			for line in f:
				data = [x for x in line.split(" ") if x != ""]

				#print(data)

				if search_file == "cat":

					df.at[c, 'year'], df.at[c, 'month'], df.at[c, 'day'] = data[1:4]			
					df.at[c, 'hour'], df.at[c, 'min'], df.at[c, 'sec'] = data[4].split(":")

					df.at[c, 'timestamp'] = datetime.datetime.strptime("-".join(data[1:5]), "%Y-%m-%d-%H:%M:%S.%f")
					df.at[c, 'lat'] = float(data[7])
					df.at[c, 'lon'] = float(data[8])
					df.at[c, 'depth'] = float(data[9])
					df.at[c, 'residual_time'] = float(data[6])
					df.at[c, 'n_p_picks'] = int(data[12])
					df.at[c, 'n_s_picks'] = int(data[13])
					df.at[c, 'n_picks'] = int(data[14])
					df.at[c, 'n_both_picks'] = int(data[15])
					df.at[c, 'station_gap'] = float(data[16])


				elif search_file == "hypoloc":
					df.at[c, 'year'], df.at[c, 'month'], df.at[c, 'day'] = data[0:3]			
					df.at[c, 'hour'], df.at[c, 'min'], df.at[c, 'sec'] = data[3:6]

					df.at[c, 'timestamp'] = datetime.datetime.strptime("-".join(data[0:6]), "%Y-%m-%d-%H-%M-%S.%f")
					df.at[c, 'lat'] = float(data[6])
					df.at[c, 'lon'] = float(data[7])
					df.at[c, 'depth'] = float(data[8])
					df.at[c, 'mag'] = float(data[9])			

					df.at[c, 'n_picks'] = int(data[10])
					df.at[c, 'station_gap'] = float(data[11])
					df.at[c, 'residual_time'] = float(data[12])
					
					
				c += 1

	df = df.sort_values(by = ['timestamp'])
	df = df.reset_index(drop = True)

	for index, row in df.iterrows():
		
		df.at[index, "cat_index"] = f"{index:06d}"

	df.to_csv(output_file, index = False)


	
if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument('-i','--input', help = "generic input")
	parser.add_argument('-o', '--output',)
	parser.add_argument('-search_file', help = "'cat' or 'hypoloc'", default = "")

	parser.add_argument('-cat', action = "store_true")
	parser.add_argument('-pha', action = "store_true")
	parser.add_argument('-reloc', action = "store_true")
	parser.add_argument('-f', action = "store_true")

	parser.add_argument('-lon', default = "")
	parser.add_argument('-lat', default = "")
	parser.add_argument('-depth', default = "")




	args = parser.parse_args()


	if args.cat:
		join_catalog_sel(args.input, args.output, args.search_file)

		# to use: Python collect_latlon.py -i INPUT_FOLDER -o OUTPUT_CSV -cat -search_file hypoloc|cat

		# hypoloc: the refined estimate
		# cat: the initial estimate from catalog_sel
		# 

	if args.pha:
		join_hypophase(args.input, args.output)

	if args.reloc:
		make_reloc_catalog(args.input, args.output)

	if args.f:
		filter_csv(args.input, args.output, lat = args.lat, lon = args.lon, depth = args.depth)
