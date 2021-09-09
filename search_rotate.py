import obspy
import matplotlib.pyplot as plt
import numpy as np
import os
import json
import argparse
from utils import parse_station_info, parse_event_coord
from obspy.geodetics import gps2dist_azimuth
from scipy.optimize import curve_fit
from pathlib import Path
from search_grid import xyz_writer
from plot_gridsearch import gmt_plotter
import subprocess
import kml_make

# get station list, start from nearest

def frequency_test():

	station = "TG11"
	pid = "000212"
	event_folder = "imported_figures/event_archive"

	
	# plot fft of waveforms 
	As = []
	phis = []	
	y0s = []
	
	_test = rotater(station, pid, event_folder)
	print(_test)


	# 	As.append(_test[0])
	# 	phis.append(_test[1])
	# 	y0s.append(_test[2])

	# As = np.abs(np.array(As))
	# phis = np.array(phis)
	# y0s = np.array(y0s)

	# y0s /= np.max(y0s)
	# As /= np.max(As)

	# with open("plot_data/rotate_vary_max_freq.txt", "w") as f:
	# 	for i, c in enumerate(range(2, 80)):
	# 		f.write("{} {} {} {}\n".format(c, As[i], phis[i], y0s[i]))
	

	#_test2 = rotater(station, pid, event_folder, _freqmin = 1, _freqmax = 45)





	# want to know: what is the absolute smallest misfit that you can get with different frequency ranges?

def baz(X1, X2):
	"""
	
	takes in two coordinate tuples (lon, lat), (lon, lat) returning their distance in kilometres
	gps2dist_azimuth also returns the azimuth but i guess i don't need that yet
	it also returns distances in metres so i just divide by 1000
	"""
	return gps2dist_azimuth(X1[1], X1[0], X2[1], X2[0])[1]


def rotate_search(pid, event_folder, output_folder, station_info_file, append_text = ""):

	# pid = "000212"
	# event_folder = "imported_figures/event_archive"
	# station_info_file = "station_info.dat"

	# output_folder = "gridsearch/output"

	output_folder = os.path.join(output_folder, pid)
	

	# i should automatically look for the json file
	if append_text:
		search_name = pid + "_" + append_text
	else:
		search_name = pid

	basename = os.path.join(output_folder, "{}".format(search_name))

	json_candidates = [str(p) for p in Path(output_folder).glob("{}.json".format(search_name))]


	print(search_name, output_folder)
	print(json_candidates)
	assert len(json_candidates) == 1
	json_file = json_candidates[0]

	npy_candidates = [str(p) for p in Path(output_folder).glob("{}.npy".format(search_name))]
	assert len(npy_candidates) ## this is so NOT future proof zzzz
	np_file = npy_candidates[0]

	station_info = parse_station_info(station_info_file)

	# get list of stations by doing an ls, then getting the unique values

	station_list = list(set([x.split(".")[0] for x in os.listdir(os.path.join(event_folder, pid)) if "SAC" in x]))

	#print(station_list)

	#rotater(station_list[0], pid, event_folder, station_info_file)
	rotation_coeff = {}

	for station in station_list:
		rotation_coeff[station] = rotater(station, pid, event_folder,)

	station_info_file

	#print(rotation_coeff)

	with open(json_file, "r") as f:
		gs_output = json.load(f)

	lb_corner = (gs_output["lb_corner_x"], gs_output["lb_corner_y"])
	DX = gs_output["cell_size"]
	DZ = 1
	try:
		NX = gs_output["cell_n"]
	except:
		NX = 100

	grid = np.zeros((NX + 1, NX + 1))

	for station in station_list:
		print("processing", station)
		station_coord = (station_info[station]["lon"], station_info[station]["lat"])
		#print(station_coord)

		for i in range(NX + 1):
			for j in range(NX + 1):
				cell_coords = (lb_corner[0] + i * DX, lb_corner[1] + j * DX)

				#print(cell_coords)
				_baz = baz(station_coord, cell_coords)

				grid[i][j] += normS(_baz, *rotation_coeff[station])

	grid /= len(station_list)

	# plt.contourf(grid.T, origin = "lower")
	# plt.colorbar()
	# plt.show()

	# load numpy file and overlay misfits



	with open(np_file, 'rb') as f:
		gs_grid = np.load(f)

	best_depths = gs_grid[:, :,int(gs_output["best_z"]),0]

	norm_best_depths = (best_depths - np.min(best_depths))/np.ptp(best_depths)

	combined = norm_best_depths + grid

	# plt.contourf(combined.T, origin = "lower")
	# plt.colorbar()
	# plt.show()
	
	
	xyz_file = basename+"rotated.xyz"
	grd_file = basename+"rotated.grd"
	ps_file = basename+"rotated.ps"
	sh_file = basename+"rotated_plot.sh"
	station_filename = basename+"station.txt"

	xyz_writer(grid, lb_corner, DX, DZ, filename = xyz_file, pers = "map")
	_lims = [lb_corner[0],
		lb_corner[0] + NX * DX,
		lb_corner[1],	
		lb_corner[1] + NX * DX,]
	output_str = "gmt xyz2grd {} -G{} -I{:.5g}/{:.5g} -R{:.5g}/{:.5g}/{:.5g}/{:.5g}".format(
		xyz_file,
		grd_file,
		DX,
		DX,
		*_lims,
	)

	print(output_str)
	p = subprocess.Popen(output_str, shell = True)

	_grid_output = {} # this is the temp one 

	for _x in ["best_x", "best_y", "best_z"]:
		_grid_output[_x] = gs_output[_x]

	_grid_output["sigma_ml"] = np.min(grid)

	gmt_plotter(grd_file, ps_file, sh_file, station_list, station_info, _lims, station_filename, _grid_output, pid,  map_type = "map")



	# plot for combined
	xyz_file = basename+"combined.xyz"
	grd_file = basename+"combined.grd"
	ps_file = basename+"combined.ps"
	sh_file = basename+"combined_plot.sh"
	#station_filename = basename+"station.txt"

	xyz_writer(combined, lb_corner, DX, DZ, filename = xyz_file, pers = "map")

	output_str = "gmt xyz2grd {} -G{} -I{:.5g}/{:.5g} -R{:.5g}/{:.5g}/{:.5g}/{:.5g}".format(
		xyz_file,
		grd_file,
		DX,
		DX,
		*_lims,
	)

	print(output_str)
	p = subprocess.Popen(output_str, shell = True)

	_grid_output = {} # this is the temp one 
	_indices = np.where(combined == combined.min())

	_grid_output["best_x"] = _indices[0][0] * DX + lb_corner[0]
	_grid_output["best_y"] = _indices[1][0] * DX + lb_corner[1]
	_grid_output["best_z"] = gs_output["best_z"]

	_grid_output["sigma_ml"] = np.min(combined)


	gmt_plotter(grd_file, ps_file, sh_file, station_list, station_info, _lims, station_filename, _grid_output, pid,  map_type = "map")

	kml_filename = basename+"combined.kml"

	_event_info = {pid+"g+r":{
	"lat":_grid_output["best_y"], 
	"lon":_grid_output["best_x"], 
	"dep":_grid_output["best_z"],}
	}

	kml_make.events(_event_info, kml_filename, "combined rotation misfits and gridsearch misfits", file_type = "direct")




	# need to know lb_corner

	# load json file with lb_corner and best x best y



	# for each station, do one rotation, fit the function to a sine wave
	# normalise the value to between 0 and 1 (?) 
	# do a grid search, query the relative backazimuth, and ask the sine wave equation what the energy misfit it
	# 
	# sum up all the grids and then divide by the no. of stations, the lower the better
	# then load the other grid at the best depth, normalise it, then add them together and plot
	# 
	# 
	# 

def normS(x, *p):
	A, phi, y0 = p
	return (np.cos((2 * x + phi) * np.pi/180) * 0.5) + 0.5

def S(x, *p):
	A, phi, y0 = p
	return np.abs(A) * np.cos((2 * x + phi) * np.pi/180) + y0

def grid_search():
	pass




def rotater(station, pid, event_folder, _freqmin = 1, _freqmax = 45, t_min = -0.1, t_max = 0.1):

	# get station list, get a grid (?) seed the grid with some starting reference point and grid area (?)
	# so that the two results are comparable i.e. i can add the results from this gridsearch to the other
	# 
	# how to get station list: ls the waveform folder, 

	#station = "TG07"

	

	# need station_info to get station coordinates
	
	# desired output: the two best guesses for the azimuth of the event relative to the station 

	# no need to seed with an event guess, it should be like an independent guess

	print(station)

	# load the SAC files

	#search_folder = "imported_figures/event_archive/000212"

	search_folder = os.path.join(event_folder, pid)

	st = obspy.read(os.path.join(search_folder, station + "*C"))

	#print(st)

	# get P arrival, get S arrival ,plot for some range

	# print(st[0].stats["sac"]["o"])
	# print(st[0].stats["sac"]["a"])
	# print(st[0].stats["sac"]["t0"])

	#dt = st[0].stats["starttime"] + 

	# need to build kztime from the sac stats to get the reference point O

	_o = [st[0].stats["sac"][x] for x in ["nzyear", "nzjday", "nzhour", "nzmin", "nzsec", "nzmsec"]]
	_o = obspy.UTCDateTime(year = _o[0], julday = _o[1], hour = _o[2], minute = _o[3], second = _o[4], microsecond = _o[5] * 1000)

	#print(_o)

	_a = _o + st[0].stats["sac"]["a"]
	_t0 = _o + st[0].stats["sac"]["t0"]

	#st.plot(starttime = _o, endtime = _o + 5)

	st.filter('bandpass', freqmin = _freqmin, freqmax = _freqmax, zerophase = True)
	_st = st.copy()

	_stt = _st.trim(starttime = _a + t_min, endtime = _t0 - t_max)

	# now rotate acccoring to the BAZ

	_X = []
	_Y = []

	for i in range(0, 360, 1):
		#print(i)

		_sti = _stt.copy()

		_sti.rotate(method="NE->RT", back_azimuth = i)

		
		
		assert _sti[0].stats["channel"] == "EHT"

		energy = np.sum(_sti[0].data**2)/(_t0 - _a - 0.2) # minimise the transverse component


		#print("BAZ", i, "energy", energy)
		_X.append(i)
		_Y.append(energy)

	_X = np.array(_X)
	_Y = np.array(_Y)

	x0 = (0.5, 180, 0.3)

	coeff, var_matrix = curve_fit(S, _X, _Y, p0 = x0)

	#print(coeff)

	# plt.plot(_X, _Y)
	# plt.plot(_X, S(_X, *coeff))
	# plt.show()
	
	

	return coeff

	#print(_X[np.argmin(_Y)])

	# want to rescale the energy misfits (assuming no weighting in between stations, which...)

	# so rescale to in between 0 and 1 so they are directly comparable

	# if they aren't directly comparable then 

if __name__ == "__main__":

	frequency_test()

	# parser = argparse.ArgumentParser()
	# parser.add_argument("pid")
	# parser.add_argument("event_folder")
	# parser.add_argument("output_folder")
	# parser.add_argument("station_info_file")

	# args = parser.parse_args()

	# rotate_search(args.pid, args.event_folder, args.output_folder, args.station_info_file)