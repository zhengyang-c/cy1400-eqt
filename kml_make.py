import simplekml
import argparse
import pandas as pd

from utils import parse_event_coord, parse_station_info, parse_xy_lines

# inputs: coordinates from different sources 
# output: kml file that can be imported into google earth
# 
# want to support: .csv file, .reloc file, REAL output
# 
# simplekml documentation: https://simplekml.readthedocs.io/en/latest/geometries.html#simplekml.Point


# taken from search_grid.py


def events(input_file, output_file, meta_desc, file_type = "event_csv"):

	#input_file = "real_postprocessing/5jul_assoc/5jul_reloc.csv"
	#output_file = "gearth_kml/5jul_afterhypoDD.kml"
	#
	#
	# pass in a dictionary with the lat, lon, key is the ID 
	
	if file_type == "direct":
		event_info = input_file
	else:
		event_info = parse_event_coord(input_file, file_type)

	#meta_desc = "After hypoDD relocation, 5 Jul Aceh catalogue"

	kml = simplekml.Kml()

	for _id in event_info:
		if "dep" in event_info[_id]:
			pt = kml.newpoint(name=_id, description = meta_desc + "\nDepth: {}".format(event_info[_id]["dep"]), coords = [(event_info[_id]["lon"], event_info[_id]["lat"], -1 *event_info[_id]["dep"])])
		else:
			pt = kml.newpoint(name=_id, description = meta_desc, coords = [(event_info[_id]["lon"], event_info[_id]["lat"])])

		pt.style.iconstyle.color = 'ff00ff00' # green; the format is like ALPHA B G R

	kml.save(output_file)

def stations(input_file, output_file, meta_desc):
	#input_file = "station_info.dat"
	#output_file = "gearth_kml/old_stations.kml"

	station_info = parse_station_info(input_file)

	#meta_desc = "Old stations (before August remapping)"

	kml = simplekml.Kml()

	for sta in station_info:
		pt = kml.newpoint(name = sta, description = meta_desc, coords = [(station_info[sta]["lon"], station_info[sta]["lat"])])
		pt.style.iconstyle.color = 'ff0000ff' # red

	kml.save(output_file)

def parse_xy(input_file, output_file, meta_desc):
	# use kml line string

	line_info = parse_xy_lines(input_file)

	kml = simplekml.Kml()

	for line in line_info:
		#print(line)
		kml.newlinestring(name = "", description = meta_desc, coords = line)

	kml.save(output_file)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument("input_file")
	parser.add_argument("output_file")
	parser.add_argument("meta_desc")
	parser.add_argument("-ft", "--file_type", default = "event_csv")

	parser.add_argument("-e", "--event", action = "store_true")
	parser.add_argument("-s", "--station", action = "store_true")
	parser.add_argument("-xy", "--xy_file", action = "store_true")

	args = parser.parse_args()

	if args.event:
		events(args.input_file, args.output_file, args.meta_desc, args.file_type)

	# a bit redundant but it's ok
	elif args.station:
		stations(args.input_file, args.output_file, args.meta_desc)

	elif args.xy_file:
		#print("yes")
		parse_xy(args.input_file, args.output_file, args.meta_desc)