import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
import datetime


def load_numpy_file(file_name):

	try:

		with open(file_name, "rb") as f:
			grid = np.load(f)

		return grid
	except:

		raise ValueError(".npy file does not exist yet, please run search_grid first")


def plotter(uid, station_list, station_info, args):

	grid = load_numpy_file(args["npy_filename"])
	L2 = grid[:,:,:,0] # 0: get the standard deviation

	indices = np.where(L2 == L2.min())

	print(grid.shape)

	print(indices)



	lb_corner = args["lb_corner"]

	min_x = lb_corner[0] + indices[0][0] * args["DX"]
	min_y = lb_corner[1] + indices[1][0] * args["DX"]



	N_X, N_Y, N_Z = grid.shape[:3]	

	# lons = lb_corner[0] + np.arange(N_X)
	# lats = lb_corner[1] + np.arange(N_Y)

	output = L2[:,:,indices[2][0]] # slice only at the depth where residual is minimum

	print(indices)

	mean_time = grid[indices[0][0], indices[1][0], indices[2][0], 1]
	ref_time = grid[indices[0][0], indices[1][0], indices[2][0], 2]

	best_origin_time = datetime.datetime.fromtimestamp(ref_time) + datetime.timedelta(seconds = mean_time)
	print(ref_time)
	print(mean_time)

	print("best origin time: ", best_origin_time)

	origin_time_str = datetime.datetime.strftime(best_origin_time, "%Y-%m-%d %H%M%S.%f")
	best_depth = indices[2][0] * args["DZ"]

	# print(output[indices[0][0], indices[1][0]])
	# print(output[57,28])

	plt.figure(figsize = (8,6), dpi = 300)
	#ax = plt.contour(output, origin = 'lower', cmap = 'rainbow' ,interpolation = 'none')

	ax = plt.contourf( output.T, levels = np.arange(0,20,1), cmap = 'rainbow', origin = 'lower')
	plt.colorbar()
	
	plt.suptitle("Origin: ({:.2f},{:.2f}), EV ID: {}, Origin Time: {}, Best Depth: {}".format(lb_corner[0], lb_corner[1], uid, origin_time_str, best_depth), fontsize = 8)
	plt.title("DX: {:.3g} deg, DZ: {:.3g} km\nMin Loc: {:.4f},{:.4f} (White Sq.) | EV Loc: {:.4f},{:.4f} (Black Star), EV Source: {}".format(args["DX"], args["DZ"], min_x, min_y, args["event_coords"][0], args["event_coords"][1], args["event_coord_format"]), fontsize = 6)

	for station in station_list:
		_x = (station_info[station]["lon"] - lb_corner[0])/args["DX"]
		_y = (station_info[station]["lat"] - lb_corner[1])/args["DX"]

		plt.scatter(_x, _y, marker = "^", c = "0")
		plt.text(_x + 0.5, _y + 0.5,station,fontsize = 4)

	_x = (args["event_coords"][0] - lb_corner[0])/args["DX"]
	_y = (args["event_coords"][1] - lb_corner[1])/args["DX"]

	plt.scatter(_x, _y, marker = "*", color = [0,0,0],)
	plt.scatter(indices[0][0], indices[1][0], marker = "s", color = [1,1,1,0.5])	
	plt.savefig(os.path.join(args["output_folder"], uid, args["base_filename"] + "_mpl.pdf"),)	

	if args["show_mpl"]:
		plt.show()

	#plt.clf()
	#plt.cla()
	plt.close(plt.gcf())

	


	# need location of stations, location of event wrt lower bottom corner

	
"""
note that GMT doesn't recognise the netcdf i produce for some reason, so this is left here
just to make the main grid search script less cluttered
"""
def netcdf_writer(lb_corner, DX, DZ ):

	# https://unidata.github.io/python-training/workshop/Bonus/netcdf-writing/
	grp = netCDF4.Dataset("gmt/gridsearch/test.nc", "w")

	with open("gridsearch/55_test_grid.npy", 'rb') as f:
		grid = np.load(f)

	# need array dimensions

	N_X, N_Y, N_Z = grid.shape[:3]

	print("loaded shape", grid.shape)

	# need starting positions + stepsize
	lon_dim = grp.createDimension('x', N_X)
	lat_dim = grp.createDimension('y', N_Y)


	# write a model title for completion with date 
	grp.title = "Test"
	grp.setncattr_string("")
	x = grp.createVariable('x', np.float64, ('x',))
	x.units = 'degrees_east'
	x.long_name = 'x'
	y = grp.createVariable('y', np.float64, ('y',))
	y.units = 'degrees_north'
	y.long_name = 'y'

	print(N_X, N_Y)
	print(lb_corner)


	x[:] = lb_corner[0] + np.arange(N_X) * DX
	y[:] = lb_corner[1] + np.arange(N_Y) * DX

	#print(lon[:])
	#print(lat[:])

	#print(grid[0][0][0][0].shape)

	rms_l2 = grp.createVariable("z", np.float64, ('x', 'y', ))

	rms_l2.units = 'km'
	rms_l2.long_name = "z"


	best_depth = 9

	rms_l2[:,:] = grid[:,:,best_depth,0]

	print(rms_l2)


	grp.close()




def test_grid():

	file_name = "gridsearch/000055_20210815-220241_DX0.05_DZ5.npy"

	with open(file_name, "rb") as f:
		grid = np.load(f)

	print(grid.shape)

	L2 = grid[:, :, :, 0]

	indices = np.where(L2 == L2.min())
	print(indices)

	depths = L2[indices[0][0], indices[1][0], :, ]

	plt.plot(np.arange(len(depths)), depths)
	plt.show()



	# ax = plt.imshow(L2[:, :, indices[2]], cmap = 'rainbow')
	# plt.colorbar(ax, cmap = "rainbow")

	# plt.show()


