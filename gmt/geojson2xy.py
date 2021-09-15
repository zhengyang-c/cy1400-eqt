import numpy as np
import json
import datetime
import os
import argparse

"""
['mag', 
'place', --> text description of location
'time',  unix time code for event
'updated',  when was the event updated
'tz',  null
'url', uh
'detail', another url
'felt', --> citizen scientist report 
'cdi', 
'mmi',  maximum estimated intensity
'alert', 
'status', 
'tsunami', 
'sig',  significance of event 
'net', 
'code',  identifying code
'ids', 
'sources', 
'types', 
'nst', 
'dmin', 
'rms', 
'gap', 
'magType', 
'type', 
'title' --> for display purposes]

depth --> 3rd value in geometry
"""
def main(input_file, output_file):
	for file in input_file:
		with open(file, encoding='utf-8') as f:
			a = json.load(f)

		with open(output_file, "a") as f:
			for feature in a["features"]:
				f.write("{}\t{}\t{}\t{}\n".format(feature["geometry"]["coordinates"][0],feature["geometry"]["coordinates"][1], feature["geometry"]["coordinates"][2], feature["properties"]["mag"]))

parser = argparse.ArgumentParser()
parser.add_argument('output_file', metavar='Output .xy file with lon/lat/depth/mag', type=str, nargs=1)
parser.add_argument('input_file', metavar='Input .json file from USGS', type=str, nargs = "+")
args = parser.parse_args()

main(args.input_file, args.output_file[0])
