import os
import pandas as pd
import numpy as np
import datetime
import json

import matplotlib.pyplot as plt
from subprocess import check_output
# http://geophysics.eas.gatech.edu/people/zpeng/Software/sac_msc/

from obspy.geodetics import gps2dist_azimuth
from obspy.geodetics import locations2degrees

from search_rotate import rotater, normS, S, baz


def cell_rotate(i, j, lb_corner, DX, station_coord, rotation_coeff):

	cell_coords = (lb_corner[0] + i * DX, lb_corner[1] + j * DX)

	_baz = baz(station_coord, cell_coords)

	return normS(_baz, *rotation_coeff)

def cell_fn(i,j,k, lb_corner, phase_info, station_info, tt, DX, DZ, TT_DX, TT_DZ, TT_NX, find_station_misfit = False, ref_mean = 0, ref_origin = 0):
	cell_coords = [i * DX + lb_corner[0], j * DX + lb_corner[1], lb_corner[2] + k * DZ]

	delta_r = [] # distance and depth pairs
	phase_list = []

	#obs_tt = []

	arrivals = [] # origin times
	_station_list = []
	# this only uses phases chosen by REAL association

	for station in phase_info:

		for phase in ["station_P", "station_S"]:
			if phase not in phase_info[station]:
				continue

			_dep = k * DZ # stations assumed to be at 0 km elevation

			_dist = dx([station_info[station]["lon"], station_info[station]["lat"]], cell_coords[:2])

			_row = [_dist, _dep]
			delta_r.append(_row)

			if phase == "station_P":
				phase_list.append("P")
				
			elif phase == "station_S":
				phase_list.append("S")

			_arrivaltime = phase_info[station][phase]

			try:
				_arrivaltime = datetime.datetime.strptime(_arrivaltime, "%Y%m%d-%H%M%S.%f")
			except:
				_arrivaltime = datetime.datetime.strptime(_arrivaltime, "%Y%m%d-%H%M%S")

			arrivals.append(_arrivaltime)

			# if do_mc:
			# 	mc_delta = np.random.normal(0, scale = mc_args["sigma_ml"])
			# else:
			# 	mc_delta = 0

			_station_list.append(station)

			#print(_row)

	delta_r = np.array(delta_r)
	#obs_tt = np.array(obs_tt)

	# bin the distance and depth 
	# bin distance only (?) i won't be touching depth
	# 
	# the travel time table is defined in kilometres, but the dx function
	# returns kilometres, so this is fine....
	# 
	
	tt_dist_indices = np.array([int(round(x)) for x in delta_r[:, 0]/TT_DX]) # for table interpolation

	
	# TT_DX is 1 so this is ok
	tt_dist_deltas = delta_r[:,0] - tt_dist_indices * TT_DX

	tt_dep_index = int(round((lb_corner[2] + k * DZ)/TT_DZ))

	# print("indices", tt_dist_indices[:5])
	# print("actual", delta_r[:5,0])
	# print("deltas", tt_dist_deltas[:5])
	#print(tt_dep_index)

	#print(max(delta_r[:,0]))

	#print(tt_dist_indices)
	#print(tt_dist_deltas)
	#
	
	tt_cell = []
	
	tt_dist_gradients = []


	# do an interpolation operation by taking the nearby indices
	# and estimating gradient

	for _c, _i in enumerate(tt_dist_indices): #_i are for travel time table indices

		if _i + 1 > TT_NX:
			_indices = np.array([_i - 1, _i])
		elif _i - 1 < 0:
			_indices = np.array([_i, _i + 1])
		else:
			_indices = np.array([_i - 1, _i, _i + 1]) 

		if phase_list[_c] == "P":
			_Y = [tt[_x][tt_dep_index][0] for _x in _indices]
			tt_cell.append(tt[_i][tt_dep_index][0])

		elif phase_list[_c] == "S":
			_Y = [tt[_x][tt_dep_index][1] for _x in _indices]

			tt_cell.append(tt[_i][tt_dep_index][1])

		tt_dist_gradients.append(ip((_indices) * TT_DX, _Y))

	tt_dist_gradients = np.array(tt_dist_gradients)
	tt_cell = np.array(tt_cell)

	#print("without correction", tt_cell[:5])

	# add the correction from the table terms using interpolation method

	tt_cell += tt_dist_gradients * tt_dist_deltas

	#print("w corr", tt_cell[:5])

	# with the travel times, find the set of origin times

	assert len(phase_list) == len(arrivals) == len(tt_cell)

	guess_ot = []

	for _c in range(len(arrivals)):
		guess_ot.append(arrivals[_c] - datetime.timedelta(seconds = tt_cell[_c]))

	# normalise the origin times and find the std 

	min_origin_time = min(guess_ot)
	for _c in range(len(guess_ot)):
		guess_ot[_c] = (guess_ot[_c] - min_origin_time).total_seconds()

	mean_time = np.mean(guess_ot)
	std_time = np.std(guess_ot)


	# SAVE the misfits on a per station basis (currently it's just summed )
	# save it somewhere (json)

	# instead of taking the mean i should be trying to minimise the residuals
	# 
	# 
	#ref_str = datetime.datetime.strftime(min_origin_time, "%Y%m%d-%H%M%S.%f")
	#
	 
	if find_station_misfit:
		# find the squared deltas between the mean times and the observation times

		station_misfit = {}
		for _i in range(len(_station_list)):
			_sta = _station_list[_i]

			if _sta not in station_misfit:
				station_misfit[_sta] = {}

			_phase = phase_list[_i]

			station_misfit[_sta][_phase] = (np.abs((min_origin_time + datetime.timedelta(seconds = guess_ot[_i] - ref_mean) - datetime.datetime.fromtimestamp(ref_origin)).total_seconds()))

		print(station_misfit)
		return station_misfit

	else:
		return (std_time, mean_time, min_origin_time.timestamp())



def arbitrary_search(args, lb_corner, grid_length, phase_info, station_info, tt, get_grid = False,):

	# pass in an arbitrary lower left corner, along with the size of the box

	#print("lb_corner", lb_corner, "grid_length", grid_length)


	N_Z = args["N_Z"]
	
	DZ = args["DZ"]
	
	TT_DX = args["TT_DX"]
	TT_DZ = args["TT_DZ"]
	TT_NX = args["TT_NX"]
	TT_NZ = args["TT_NZ"]

	DX = grid_length / (args["N_DX"])
	args["DX"] = DX

	rotate_grid = ""	
	combined = ""

	grid = np.zeros([args["N_DX"] + 1, args["N_DX"] + 1, N_Z, 3])

	if args["run_rotate"]:

		actual_stnlst = []

		event_folder = args["event_folder"]
			
		_station_list = phase_info.keys()
		ignored_stations = 0
		rotation_coeff = {}
		for station in _station_list:
			_coeff = rotater(station, args["pid"], event_folder,)
			try:
				if _coeff == -1:
					ignored_stations += 1
					continue
			except:
				rotation_coeff[station] = _coeff
				actual_stnlst.append(station)

		if len(rotation_coeff.keys()) == 0:
			if do_rotate:
				print("No rotation operation will be performed.")
			do_rotate = False
		else:
			do_rotate = True
		
		rotate_grid = np.zeros([args["N_DX"] + 1, args["N_DX"] + 1])
	else:
		do_rotate = False

	for i in range(args["N_DX"] + 1): # lon
	#for i in range(1):
	#	for j in range(1):
		for j in range(args["N_DX"] + 1): # lat
			for k in range(N_Z): # depth

				_cell_output = cell_fn(i, j, k, lb_corner, phase_info, station_info, tt, DX, DZ, TT_DX, TT_DZ, TT_NX)
				grid[i][j][k][:] = _cell_output

			if args["run_rotate"]:
				for station in actual_stnlst:
					station_coord = (station_info[station]["lon"], station_info[station]["lat"])

					rotate_grid[i][j] += cell_rotate(i, j, lb_corner, DX, station_coord, rotation_coeff[station])
					
	L2 = grid[:,:,:,0] # 0: get the standard deviation

	indices = np.where(L2 == L2.min())

	print("Inside gridsearch: ", indices)

	best_i = indices[0][0]
	best_j = indices[1][0]
	best_k = indices[2][0]

	best_x = lb_corner[0] + best_i * args["DX"]
	best_y = lb_corner[1] + best_j * args["DX"]
	best_z = lb_corner[2] + best_k * args["DZ"]

	print("Inside gridsearch: ", best_i, best_j, best_k)


	if do_rotate:
		# get best depth layer

		rotate_grid /= (len(actual_stnlst)) 

		norm_rotate_grid = (rotate_grid - np.min(rotate_grid))/np.ptp(rotate_grid)

		best_depths = L2[:, :, best_k]

		norm_best_depths = (best_depths - np.min(best_depths))/np.ptp(best_depths)

		combined = norm_best_depths + norm_rotate_grid

		c_indices = np.where(combined == combined.min())

	output = {
		"DX":DX,
		"best_x": best_x,		
		"best_y": best_y,
		"best_z": best_z,
		"best_i": best_i,
		"best_j": best_j,
		"best_k": best_k,
		"sigma_ml":  grid[best_i, best_j, best_k, 0],
		"mean_time": grid[best_i, best_j, best_k, 1],
		"ref_time":  grid[best_i, best_j, best_k, 2],
		"ref_timestamp":  datetime.datetime.strftime(datetime.datetime.fromtimestamp(grid[best_i, best_j, best_k, 2]), "%Y%m%d-%H%M%S.%f"),
	}

	if do_rotate:
		best_i_c = c_indices[0][0]
		best_j_c = c_indices[1][0]
		best_x_c = lb_corner[0] + best_i_c * args["DX"] 
		best_y_c = lb_corner[1] + best_j_c * args["DX"] 

		output["combined_misfit"] = combined[best_i_c, best_j_c]
		output["best_x_c"] = best_x_c
		output["best_y_c"] = best_y_c
		output["best_i_c"] = best_i_c
		output["best_j_c"] = best_j_c
		  
	#print(output)

	# get station misfits if it's the minimum

	if get_grid:

		if do_rotate:
			station_misfit = cell_fn(best_i_c,best_j_c,best_k, lb_corner, phase_info, station_info, tt, DX, DZ, TT_DX, TT_DZ, TT_NX, find_station_misfit = True, ref_mean = grid[best_i_c, best_j_c, best_k, 1], ref_origin = grid[best_i_c, best_j_c, best_k, 2])

			for _station in _station_list:
				_station_coords = station_info[_station]


				_baz = baz((_station_coords["lon"], _station_coords["lat"]), (output["best_x_c"], output["best_y_c"]))
				_baz = baz((_station_coords["lon"], _station_coords["lat"]), (output["best_x"], output["best_y"]))

				rotater(_station, args["pid"], args["event_folder"], save = True, output_folder = os.path.join(args["output_folder"], args["pid"]),  best_baz = _baz)

		else:
			station_misfit = cell_fn(best_i,best_j,best_k, lb_corner, phase_info, station_info, tt, DX, DZ, TT_DX, TT_DZ, TT_NX, find_station_misfit = True, ref_mean = grid[best_i, best_j, best_k, 1], ref_origin = grid[best_i, best_j, best_k, 2])

		return (grid, station_misfit, lb_corner, DX, args["N_DX"] + 1, rotate_grid, combined, output)


	# positions:

	# centre around the minimum point, take +/- 2 indices
	# for an initial N of 20, this means that you will pass 4 points 
	# 
	# i also realise that like i have fence post problem . . . .actually maybe not because i'm rounding up my gridlength
	
	# find new lower left corner:


	# find new N_Z and vertical component of corner

	new_N_Z = int(round(21 / args["DZ"])) # 21 just seems like a nice number so +/-10 km depth 

	if best_z - 11 * args["DZ"]< 0:
		new_Z_start = 0
	elif best_z + 11 * args["DZ"] > tt.shape[1]:
		new_Z_start = best_z - 21 * args["DZ"]
	else:
		new_Z_start = best_z - 10 * args["DZ"]
	
	args["N_Z"] = new_N_Z

	if do_rotate:
		# the rotation results should guide the iterative gridsearch
		new_lb_corner = (best_x_c - 2 * DX, best_y_c - 2 * DX, new_Z_start)
	else:
		new_lb_corner = (best_x - 2 * DX, best_y - 2 * DX, new_Z_start)

	new_grid_length = DX * 4
	new_DX = new_grid_length / args["N_DX"]
		
	if new_DX < (0.1/111.11):
		return output
	else:
		return arbitrary_search(args, new_lb_corner, new_grid_length, phase_info, station_info, tt,) 


def dx(X1, X2):
	"""
	
	takes in two coordinate tuples (lon, lat), (lon, lat) returning their distance in kilometres
	gps2dist_azimuth also returns the azimuth but i guess i don't need that yet
	it also returns distances in metres so i just divide by 1000

	the order doesn't matter
	
	:param      X1:   The x 1
	:type       X1:   { type_description }
	:param      X2:   The x 2
	:type       X2:   { type_description }

	"""

	#print(X1, X2)
	return gps2dist_azimuth(X1[1], X1[0], X2[1], X2[0])[0] / 1000

	# out = check_output(["./gridsearch/distbaz", "{:.7g}".format(X1[0]), "{:.7g}".format(X1[1]), "{:.7g}".format(X2[0]), "{:.7g}".format(X2[1])])
	# #print(out)
	# out = [float(x) for x in out.decode('UTF-8').strip().split(" ") if x != ""]
	# #print(out[0])
	# return out[0]


def ip(X, Y):
	if len(X) == 3:

		# arithmetic average of in between gradients to approximate gradient at midpoint

		return 0.5 * ((Y[2] - Y[1])/(X[2] - X[1]) + (Y[1] - Y[0])/(X[1] - X[0]))

	if len(X) == 2:

		return (Y[1] - Y[0])/(X[1] - X[0])



"""
# save the mean and std origin time in the grid
					# saving the datetime object sounds like a bad idea
					# so just convert the reference time to a string?
					# so it'll be
					# 
					# std
					# mean delta
					# min_time reference as string
					# 
					# then i can look up the cell, and reobtain the mean time
					# 
					
					following code was done assuming the truth of REAL travel times, which
					may not always be the case
					they are left here for reference

					# # calculate L2 and L1 errors

					# sq_residuals = (tt_cell - obs_tt)**2
					# abs_residuals = np.sqrt(sq_residuals)

					# # keep standard dev in array because idk that could be useful? 

					# volume = (grid_length * DX)**2 * (Z_RANGE)

					# sq_residuals /= volume
					# abs_residuals /= volume

					# L2 = np.sum(sq_residuals)
					# L2_std = np.std(sq_residuals)
					# L1 = np.sum(abs_residuals)
					# L1_std = np.std(abs_residuals)

					# grid[i][j][k][0] = L2
					# grid[i][j][k][1] = L2_std
					# grid[i][j][k][2] = L1
					# grid[i][j][k][3] = L1_std

"""



	