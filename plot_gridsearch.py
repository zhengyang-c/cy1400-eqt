import matplotlib.pyplot as plt
import numpy as np
import os
import argparse


def load_numpy_file(file_name):

	try:

		with open(file_name, "rb") as f:
			grid = np.load(f)

		return grid
	except:

		raise ValueError(".npy file does not exist yet, please run search_grid first")


def plotter(uid, station_list, station_info, args):

	grid = load_numpy_file(args["npy_filename"])
	L2 = grid[:,:,:,args["layer_index"]]

	indices = np.where(L2 == L2.min())

	print(grid.shape)

	lb_corner = args["lb_corner"]

	min_x = lb_corner[0] + indices[0][0] * args["DX"]
	min_y = lb_corner[1] + indices[1][0] * args["DX"]



	N_X, N_Y, N_Z = grid.shape[:3]	

	output = L2[:,:,indices[2][0]] # slice only at the depth where residual is minimum

	plt.figure(figsize = (8,6), dpi = 300)
	ax = plt.imshow(output, origin = 'lower', cmap = 'rainbow' ,interpolation = 'none')
	plt.colorbar()
	
	plt.suptitle("Origin: ({:.2f},{:.2f}), EV ID: {}".format(lb_corner[0], lb_corner[1], uid), fontsize = 8)
	plt.title("DX: {} deg, DZ: {} km\nMin Loc: {:.4f},{:.4f} (White Sq.) | EV Loc: {:.4f},{:.4f} (Black Star), EV Source: {}".format(args["DX"], args["DZ"], min_x, min_y, args["event_coords"][0], args["event_coords"][1], args["event_coord_format"]), fontsize = 6)

	for station in station_list:
		_x = (station_info[station]["lon"] - lb_corner[0])/args["DX"]
		_y = (station_info[station]["lat"] - lb_corner[1])/args["DX"]

		plt.scatter(_x, _y, marker = "^", c = "0")
		plt.text(_x + 0.5, _y + 0.5,station,fontsize = 4)

	_x = (args["event_coords"][0] - lb_corner[0])/args["DX"]
	_y = (args["event_coords"][1] - lb_corner[1])/args["DX"]

	plt.scatter(_x, _y, marker = "*", color = [0,0,0,0.5],)
	plt.scatter(indices[0][0], indices[1][0], marker = "s", color = [1,1,1,0.3])	
	plt.savefig(os.path.join(args["output_folder"], args["base_filename"] + "_mpl.pdf"),)	

	if args["show_mpl"]:
		plt.show()

	


	# need location of stations, location of event wrt lower bottom corner