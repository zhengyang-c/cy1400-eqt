import numpy as np
import math
import os

import argparse

#lon_i = 95 
#lat_i = 10
#lon_f = 110
#lat_f = -5

# https://stackoverflow.com/questions/29545704/fast-haversine-approximation-python-pandas
def haversine_np(lon1, lat1, lon2, lat2):
	"""
	Calculate the great circle distance between two points
	on the earth (specified in decimal degrees)

	All args must be of equal length.    

	"""
	lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

	c = 2 * np.arcsin(np.sqrt(a))
	km = 6371 * c
	return km

def calc(input_file, output_file, lon_i, lat_i, lon_f, lat_f, n_bins, n):

	n = int(n[-4]) # shitty hack, read the file name properly with regex

	#input_file = "main/sumatra_1.binned/profile0.temp"
	#output_file = "main/sumatra_1.binned/pprofile0.xy"

	data = []
	with open(input_file, "r") as f:
		for line in f:
			data.append([x.strip() for x in line.split("\t")])

	r_i = np.array([lon_i, lat_i])
	r_f = np.array([lon_f, lat_f])

	unit = (r_f - r_i)/np.linalg.norm(r_f - r_i)

	mids = []

	for i in range(1, n_bins):
		mids.append((1/n_bins) * (i * r_f + (n_bins - i) * r_i))

	bins = [r_i]
	bins.extend(mids)
	bins.append(r_f)
	#print(bins)

	unit = (r_f - r_i)/np.linalg.norm(r_f - r_i) 

	midpoints = [0.5 *(bins[i] + bins[i+1]) for i in range(n_bins)]

	normal_vector = np.array([-1 * unit[1], unit[0]])

	profile_coords = []

	minus_distance = 3
	positive_distance = 0

	#print(distance * normal_vector)

	for z in midpoints:
		profile_coords.append([z - minus_distance * normal_vector, z + positive_distance*normal_vector])

	profile_used = profile_coords[n]
	profile_i = profile_used[0]
	profile_f = profile_used[1]

	unit_profile = (profile_f - profile_i)/np.linalg.norm(profile_f - profile_i)

	with open(output_file, "w") as f:
		for datum in data:
			r_x = [float(datum[0]), float(datum[1])]

			rel_dist = float(np.dot(unit_profile, (r_x - profile_i))) # distance along line
			rel_dist *= 111.1
			#print(rel_dist)


			f.write("{:.3f}\t{}\n".format(rel_dist, datum[2]))
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('input_file', metavar="input", type=str, nargs=1)
	parser.add_argument('output_file', metavar="output", type=str, nargs=1)
	parser.add_argument('lon_i', type = float, nargs = 1)
	parser.add_argument('lat_i', type = float, nargs = 1)
	parser.add_argument('lon_f', type = float, nargs = 1)
	parser.add_argument('lat_f', type = float, nargs = 1)
	parser.add_argument('n_bins', type = int, nargs = 1)
	parser.add_argument('n', type = str, nargs = 1)

	#parser.add_argument('az', metavar='az', help="Counterclockwise rotation along North axis. ", type=float, nargs=1)

	args = parser.parse_args()

	calc(args.input_file[0], args.output_file[0], args.lon_i[0], args.lat_i[0], args.lon_f[0], args.lat_f[0], args.n_bins[0], args.n[0])




