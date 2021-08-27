import pandas as pd
import numpy as np
import datetime
import json

import matplotlib.pyplot as plt

def arbitrary_search(args, lb_corner, grid_length, phase_info, station_info, tt, compute_lambda= False, N_monte_carlo = 1, do_mc = False, mc_args = None):

	# pass in an arbitrary lower left corner, along with the size of the box

	print("lb_corner", lb_corner, "grid_length", grid_length)


	N_Z = args["N_Z"]
	
	DZ = args["DZ"]
	
	TT_DX = args["TT_DX"]
	TT_DZ = args["TT_DZ"]
	TT_NX = args["TT_NX"]
	TT_NZ = args["TT_NZ"]


	# arbitrary_search (call itself)

	# 111km --> 1 degree
	# 0.3 km --> 
	# 
	
	# grid_length is in units of decimal degrees

	DX = grid_length / (args["N_DX"])
	args["DX"] = DX	

	if do_mc:
		mc_mask = np.zeros([args["N_DX"]+1, args["N_DX"]+1, N_Z])

	for _c in range(N_monte_carlo):
		grid = np.zeros([args["N_DX"] + 1, args["N_DX"] + 1, N_Z, 3])

		if compute_lambda:
			lambdas = np.zeros([args["N_DX"]+1, args["N_DX"]+1, N_Z])


		for i in range(args["N_DX"] + 1): # lon
			for j in range(args["N_DX"] + 1): # lat
				for k in range(N_Z): # depth

					cell_coords = [i * DX + lb_corner[0], j * DX + lb_corner[1], k * DZ]

					delta_r = [] # distance and depth pairs
					phase_list = []
					#obs_tt = []

					arrivals = [] # origin times
					# this only uses phases chosen by REAL association
					for station in phase_info:

						for phase in ["P", "S"]:
							if phase not in phase_info[station]:
								continue

							_dep = k * DZ # stations assumed to be at 0 km elevation

							_dist = dx([station_info[station]["lon"], station_info[station]["lat"]], cell_coords[:2])

							_row = [_dist, _dep]

							phase_list.append(phase)
							delta_r.append(_row)
							#obs_tt.append(float(phase_info[station][phase]))

							if do_mc:
								mc_delta = np.random.normal(0, scale = mc_args["sigma_ml"])
							else:
								mc_delta = 0
							if phase == "P":
								arrivals.append(phase_info[station]["station_P"] + datetime.timedelta(seconds = mc_delta))

							elif phase == "S":
								arrivals.append(phase_info[station]["station_S"] + datetime.timedelta(seconds = mc_delta))

							#print(_row)

					delta_r = np.array(delta_r)
					#obs_tt = np.array(obs_tt)

					# bin the distance and depth 
					# bin distance only (?) i won't be touching depth
					
					tt_dist_indices = np.array([int(round(x)) for x in delta_r[:, 0]/TT_DX])

					tt_dist_deltas = delta_r[:,0] - tt_dist_indices * TT_DX

					tt_dep_index = int(round((k * DZ)/TT_DZ))
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

					# add the correction from the table terms using interpolation method

					tt_cell += tt_dist_gradients * tt_dist_deltas

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


					# compute lambdas

					if compute_lambda:
						lambdas[i][j][k] = np.sqrt(len(guess_ot))/(2 * std_time) + len(guess_ot) * np.log(std_time)


					# instead of taking the mean i should be trying to minimise the residuals
					# 
					# 
					#ref_str = datetime.datetime.strftime(min_origin_time, "%Y%m%d-%H%M%S.%f")

					grid[i][j][k][0] = std_time
					grid[i][j][k][1] = mean_time
					grid[i][j][k][2] = min_origin_time.timestamp()

		if do_mc:
			# locate mc origin
			_mc_indices = np.where(grid == grid.min())

			#_mc_tau = lambdas -  lambdas[_mc_indices[0][0], _mc_indices[1][0],_mc_indices[2][0]]

			#mc_mask += (_mc_tau < mc_args["ref_tau"]).astype('int')

			mc_mask[_mc_indices[0][0], _mc_indices[1][0],_mc_indices[2][0]] += 1


	# found_coordinates
	if not do_mc:
		#print(grid)

		L2 = grid[:,:,:,0] # 0: get the standard deviation

		indices = np.where(L2 == L2.min())

		print(indices)

		min_x = lb_corner[0] + indices[0][0] * args["DX"]
		min_y = lb_corner[1] + indices[1][0] * args["DX"]
		min_z = indices[2][0] * args["DZ"]

		output = {
			"min_x": min_x,		
			"min_y": min_y,
			"min_z": min_z,
			"sigma_ml": grid[indices[0][0],indices[1][0],indices[2][0], 0],
			"ref_time": grid[indices[0][0],indices[1][0],indices[2][0], 1],
			"mean_time": grid[indices[0][0],indices[1][0],indices[2][0], 2],
		}

		# positions:

		# centre around the minimum point, take +/- 2 indices
		# for an initial N of 20, this means that you will pass 4 points 
		# 
		# i also realise that like i have fence post problem . . . .actually maybe not because i'm rounding up my gridlength
		# 
		# 
		
		# find new lower left corner:

		new_lb_corner = (min_x - 2 * DX, min_y - 2 * DX)
		new_grid_length = DX * 4

		

		# return the (x,y coordinates), sigma, and the mean origin time / reference time 
		if compute_lambda:
			# indices = np.where(lambdas == lambdas.min())
			# print(indices)

			# plt.imshow(lambdas[:,:,indices[2][0]])
			# plt.show()

			return lambdas
		elif DX < (0.3/111.11):
			return output
		else:
			return arbitrary_search(args, new_lb_corner, new_grid_length, phase_info, station_info, tt)

	else:
		mc_mask /= N_monte_carlo

		# plt.title("map view")
		# plt.imshow(mc_mask[:,:,int(mc_args["min_z"])])
		# plt.colorbar()
		# plt.show()
		# plt.title("lat and depth")
		# plt.imshow(mc_mask[10,:,:])
		# plt.colorbar()
		# plt.show()
		# plt.title("lon and depth")
		# plt.imshow(mc_mask[:,10,:])
		# plt.colorbar()
		# plt.show()

		with open("gridsearch/test_stdmask.npy", "wb") as f:
			np.save(f, mc_mask)

		return mc_mask



def dx(X1, X2):
	return np.sqrt((X1[0] - X2[0])**2 + (X1[1] - X2[1])**2)



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



	