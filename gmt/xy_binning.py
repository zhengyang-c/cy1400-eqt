import numpy as np
import math
import os
from rotate_beachball import rotate
import argparse
from subprocess import Popen, PIPE

def binning(input_file, output_folder, n_bins, lon_i, lat_i, lon_f, lat_f):

	#input_file = "main/sumatra_test.xy"
	#output_folder = "main/sumatra_test.xy.binned"

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	# lon / lat
	#r_i = np.array([95, 10] )
	#r_f = np.array([110, -5])
	r_i = np.array([lon_i, lat_i])
	r_f = np.array([lon_f, lat_f])

	# relative distance of the event to the vector
	# arrow starts from the right of the line drawn

	#n_bins = 5
	mids = []

	data = []

	with open(input_file, "r") as f:
		for line in f:
			#data.append([x.strip() for x in line.strip().split(" ")])
			data.append([x.strip() for x in line.strip().split("\t")])

	for i in range(1, n_bins):
		mids.append((1/n_bins) * (i * r_f + (n_bins - i) * r_i))

	bins = [r_i]
	bins.extend(mids)
	bins.append(r_f)
	print(bins)
	binned = {}

	unit_o = (r_f - r_i)/np.linalg.norm(r_f - r_i) 
	az = (np.arcsin(np.cross((0,1), unit_o)) * 180/math.pi)

	midpoints = [0.5 *(bins[i] + bins[i+1]) for i in range(n_bins)]

	normal_vector = np.array([-1 * unit_o[1], unit_o[0]])
	# CCW rotation, also unit vector

	#print(midpoints)
	#print(normal_vector)

	profile_coords = []

	minus_distance = 2.5
	positive_distance = 2.5

	#print(distance * normal_vector)

	for z in midpoints:
		profile_coords.append([z - minus_distance * normal_vector, z + positive_distance*normal_vector])
	#print(profile_coords)
	#print(len(profile_coords))

	def get_bin(r_x, n_bins):
		# r is [lon/lat] of the data point
	
		l = np.dot(unit_o, (r_x - r_i)) # where is it along the line
		bin_value = math.floor(n_bins * (l/np.linalg.norm(r_f - r_i)))
		if bin_value < 0:
			return None
		elif bin_value > (n_bins - 1):
			return None

		#[_r_i, _r_f] = profile_coords[bin_value]
		#print(np.linalg.norm(r_f - r_i))
		#print(l)
		return bin_value
	def get_rel_dist(r_x, n):
		profile_i = profile_coords[n][0]
		profile_f = profile_coords[n][1]

		_l = np.dot(normal_vector, (r_x - profile_i)) # where is it along the profile
		return _l

	for datum in data:
		datum[0], datum[1] = float(datum[0]), float(datum[1])

		bin_value = (get_bin([datum[0], datum[1]], n_bins))
		if bin_value == None:
			continue
		rel_dist =  get_rel_dist([datum[0], datum[1]], bin_value)

		datum.append("{:.3f}".format(rel_dist))

		if bin_value not in binned:
			binned[bin_value] = [datum]
		else:
			binned[bin_value].append(datum)

	# assumes that all bins are filled 
	for k in range(n_bins):
		#print(k)
		#print(binned[k])
		_filename = "bin{}.xy".format(k)
		with open(os.path.join(output_folder, _filename), "w") as f:
			if k in binned:
				for datum in binned[k]:
					# change for beachball
					#f.write(" ".join([str(datum[i]) for i in [-1,2,2,3,4,5,6,7,8,9,10,11,12]]) + "\n")
					# -1: rel_dist, depth
					f.write(" ".join([str(datum[i]) for i in [-1, 2, 2, 3]]) + "\n")

		#.zxy the lat lon so i can plot the binned beachballs
		_filename = "bin{}.zxy".format(k)					
		with open(os.path.join(output_folder, _filename), "w") as g:
			if k in binned:		
				for datum in binned[k]:					
					g.write(" ".join([str(i) for i in datum[:-1]]) + "\n")

		if not os.path.exists(os.path.join(output_folder, "rotated")):
			os.makedirs(os.path.join(output_folder, "rotated"))

		_filename = "bin{}.xy".format(k)
		#rotate(os.path.join(output_folder, _filename), os.path.join(output_folder, "rotated", _filename), az)

	# print the profile endpoints
	for k in range(n_bins):
		#_filename = "profile{}.temp".format(k)
		_temp_filename = "profile{}.temp".format(k)
		with open(os.path.join(output_folder, _temp_filename), "w") as f:
			f.write("{:.2f} {:.2f}\n{:.2f} {:.2f}".format(profile_coords[k][0][0], profile_coords[k][0][1],profile_coords[k][1][0], profile_coords[k][1][1]) + "\n")


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('input_file', metavar="input", help='Input .xy file to bin', type=str, nargs=1)
	parser.add_argument('output_folder', metavar="output", help='Folder to keep binned and rotated files', type=str, nargs=1)
	parser.add_argument('n_bins', type = int, nargs = 1)
	parser.add_argument('lon_i', type = float, nargs = 1)
	parser.add_argument('lat_i', type = float, nargs = 1)
	parser.add_argument('lon_f', type = float, nargs = 1)
	parser.add_argument('lat_f', type = float, nargs = 1)

	#parser.add_argument('az', metavar='az', help="Counterclockwise rotation along North axis. ", type=float, nargs=1)

	args = parser.parse_args()

	binning(args.input_file[0], args.output_folder[0], args.n_bins[0], args.lon_i[0], args.lat_i[0], args.lon_f[0], args.lat_f[0])