import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
import datetime
import time
import subprocess

def load_numpy_file(file_name):

	try:

		with open(file_name, "rb") as f:
			grid = np.load(f)

		print("Loading numpy file: {}".format(file_name))

		return grid
	except:

		raise ValueError(".npy file does not exist yet, please run search_grid first")

def xyz_writer(output, lb_corner, DX, DZ,  filename = "", pers = "map"):
	N_X, N_Y = output.shape

	with open(filename, "w") as f:
		for i in range(N_X):
			for j in range(N_Y):
				if pers == "map":
					x = lb_corner[0] + i * DX
					y = lb_corner[1] + j * DX
				elif pers == "londep":
					x = lb_corner[0] + i * DX
					y = lb_corner[2] + j * DZ
				elif pers == "latdep":
					x = lb_corner[1] + i * DX
					y = lb_corner[2] + j * DZ

				z = output[i,j]

				f.write("{:.7f} {:.7f} {:.3f}\n".format(x,y,z))

# TODO: rewrite plotter s.t. it will plot the confidence intervals for some range / or also show the contours
# 3 plots viewing from 3 diff axes i guess
# also want to put an estimate of vertical and horizontal uncertainty without like any weird coordinate rotation hmm


def preplot(plot_data, target_lb, grid_output, y_cell_size, lims, output_folder, base_filename, _type = "", pers = "map"):

	xyz_filename = os.path.join(output_folder, base_filename + _type + ".xyz")
	grd_filename = os.path.join(output_folder, base_filename + _type + ".grd")
	ps_file = os.path.join(output_folder, base_filename + _type + ".ps")
	sh_file = os.path.join(output_folder, base_filename + _type + "_plot.sh")
	xyz_writer(plot_data, target_lb, grid_output["cell_size"], grid_output["cell_height"], filename = xyz_filename , pers = pers)
	# xyz writer
	# gmt xyz2grid
	# run gmt
	# call gmt plotter probably

	output_str = "gmt xyz2grd {} -G{} -I{:.5g}/{:.5g} -R{:.5g}/{:.5g}/{:.5g}/{:.5g}".format(
		xyz_filename,
		grd_filename,
		grid_output["cell_size"],
		y_cell_size,
		lims[0],
		lims[1],
		lims[2],	
		lims[3],
	)
	print(output_str)
	p = subprocess.Popen(output_str, shell = True)

	return grd_filename, ps_file, sh_file


def gmt_plotter(grd_file, output_file, output_sh, station_list, station_info, lims, station_file, grid_output, pid, output_folder, misfit_file = "", misfitplot_file = "", map_type = "map", colorscale = "0/1/0.05", ticscale = "0.05", gmt_home = "/home/zy/gmt", rotate = False):


	with open(station_file, "w") as f:
		for x in station_list:
			f.write("{}\t{}\t{}\n".format(x, station_info[x]["lon"], station_info[x]["lat"]))

	# this will probably only work for JM6i
	# for londep/latdep you want to use JX
	# 
	# 

	if rotate:
		grid_output["best_x"] = grid_output["best_x_c"]
		grid_output["best_y"] = grid_output["best_y_c"]
		print("hello")
	
	#colorscale = "0/1/0.05"

	# probably want another map with all the stations inside so you can.. see.. the stations
	# just call the fn with another set o lims and output_file

	if map_type == "map":

		output_str = [
		"#!/bin/bash",
		"gmt set PS_MEDIA=A2",
		"gmt set FORMAT_GEO_MAP=D",
		"PROJ=\"-JM6i\"",
		"LIMS=\"-R{:.5g}/{:.5g}/{:.5g}/{:.5g}\"".format(lims[0], lims[1], lims[2], lims[3]),
		"PLATE=\"{}/plate/sumatran_fault_ll.xy\"".format(gmt_home),
		"PSFILE=\"{}\"".format(output_file),
		"CPT=\"-C{}/cpt/colombia.cpt\"".format(gmt_home),
		"ETOP=\"{}/etop/GMRTv3_9_20210325topo_61m.grd\"".format(gmt_home),
		"gmt makecpt -Crainbow -T{} -Z > {}".format(colorscale, os.path.join(output_folder, "temp.cpt")),
		"gmt grdimage $ETOP $PROJ $LIMS $CPT -K > $PSFILE",
		"gmt grdimage {} $PROJ $LIMS -C{} -Q -K -O >> $PSFILE".format(grd_file, os.path.join(output_folder, "temp.cpt")),
		"gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE",
		"gmt pscoast $PROJ $LIMS -W1p -Df -N1/0.5p -A0/0/1 -K -O >> $PSFILE",
		"awk '{{print $2,$3}}' {} | gmt psxy $PROJ $LIMS -Gblack -St0.1i -W0.5p -K -O >> $PSFILE".format(station_file),
		"awk '{{print $2,$3,$1}}' {} | gmt pstext $PROJ $LIMS -F+f6p,0+jRB -D-0.2c/0 -K -O >> $PSFILE".format(station_file),
		"echo {:.7g} {:.7g} | gmt psxy $PROJ $LIMS -Gwhite -Sa0.12i -W0.5p -K -O >> $PSFILE".format(grid_output["best_x"], grid_output["best_y"]),
		"echo \"Best misfit: {:.3g}\" | gmt pstext $PROJ $LIMS -F+cBC -D0/0.1 -K -O >> $PSFILE".format(grid_output["sigma_ml"]),
		"gmt psscale $PROJ $LIMS -DjTC+w14c/0.5c+jTC+h -G{} -C{} --FONT_ANNOT_PRIMARY=6p,Helvetica,black -K -O >> $PSFILE".format(colorscale, os.path.join(output_folder, "temp.cpt")),
		"gmt psbasemap $PROJ $LIMS -BWeSn+t\"ID: {}, Best depth: {:.2g}km\" -Bxa{}g0.01 -Bya{}g0.01 -O >> $PSFILE".format(pid, grid_output["best_z"], ticscale, ticscale),
		"gmt psconvert $PSFILE -Tf -A+m1c",
		#"rm temp.cpt",
		]

	elif map_type == "londep":
		#print("plot lims:",lims)
		output_str = [
		"#!/bin/bash",
		"gmt set PS_MEDIA=A2",
		"gmt set FORMAT_GEO_MAP=D",
		"PROJ=\"-Jx40c/-0.4c\"",
		"LIMS=\"-R{:.5g}/{:.5g}/{:.5g}/{:.5g}\"".format(lims[0], lims[1], -1, lims[3]),
		"PLATE=\"{}/plate/sumatran_fault_ll.xy\"".format(gmt_home),
		"PSFILE=\"{}\"".format(output_file),
		"CPT=\"-C{}/cpt/colombia.cpt\"".format(gmt_home),
		"ETOP=\"{}/etop/GMRTv3_9_20210325topo_61m.grd\"".format(gmt_home),
		"gmt makecpt -Crainbow -T{} -Z > {}".format(colorscale, os.path.join(output_folder, "temp.cpt")),
		"gmt grdimage {} $PROJ $LIMS -C{} -Q -K > $PSFILE".format(grd_file, os.path.join(output_folder, "temp.cpt")),
		#"gmt pscoast $PROJ $LIMS -W1p -Df -N1/0.5p -A0/0/1 -K -O >> $PSFILE",
		"awk '{{print $2,0}}' {} | gmt psxy $PROJ $LIMS -Gblack -St0.1i -W0.5p -K -O >> $PSFILE".format(station_file),
		"awk '{{print $2,0,$1}}' {} | gmt pstext $PROJ $LIMS -F+f6p,0+jRB -D-0.2c/0 -K -O >> $PSFILE".format(station_file),
		"echo {:.7g} {:.7g} | gmt psxy $PROJ $LIMS -Gwhite -Sa0.12i -W0.5p -K -O >> $PSFILE".format(grid_output["best_x"], grid_output["best_z"]),
		"echo \"Best misfit (L2): {:.3g} s\" | gmt pstext $PROJ $LIMS -F+cBC -D0/1c -K -O >> $PSFILE".format(grid_output["sigma_ml"]),
		"gmt psscale $PROJ $LIMS -DjLB+w14c/0.5c+jLB+o0.5c -G{} -C{} --FONT_ANNOT_PRIMARY=6p,Helvetica,black -K -O >> $PSFILE".format(colorscale, os.path.join(output_folder, "temp.cpt")),
		"gmt psbasemap $PROJ $LIMS -BWeSn+t\"ID: {}, Best depth: {:.2g}km\" -Bxa{} -Bya{} -O >> $PSFILE".format(pid, grid_output["best_z"], ticscale, 1),
		"gmt psconvert $PSFILE -Tf -A+m1c",
		]

	elif map_type == "latdep": # copying because i've given up

		output_str = [
		"#!/bin/bash",
		"gmt set PS_MEDIA=A2",
		"gmt set FORMAT_GEO_MAP=D",
		"PROJ=\"-Jx40c/-0.4c\"",
		"LIMS=\"-R{:.5g}/{:.5g}/{:.5g}/{:.5g}\"".format(lims[0], lims[1], -1, lims[3]),
		"PLATE=\"{}/plate/sumatran_fault_ll.xy\"".format(gmt_home),
		"PSFILE=\"{}\"".format(output_file),
		"CPT=\"-C{}/cpt/colombia.cpt\"".format(gmt_home),
		"ETOP=\"{}/etop/GMRTv3_9_20210325topo_61m.grd\"".format(gmt_home),
		"gmt makecpt -Crainbow -T{} -Z > {}".format(colorscale, os.path.join(output_folder, "temp.cpt")),
		"gmt grdimage {} $PROJ $LIMS -C{} -K -Q > $PSFILE".format(grd_file, os.path.join(output_folder, "temp.cpt")),
		#"gmt pscoast $PROJ $LIMS -W1p -Df -N1/0.5p -A0/0/1 -K -O >> $PSFILE",
		"awk '{{print $2,0}}' {} | gmt psxy $PROJ $LIMS -Gblack -St0.1i -W0.5p -K -O >> $PSFILE".format(station_file),
		"awk '{{print $2,0,$1}}' {} | gmt pstext $PROJ $LIMS -F+f6p,0+jRB -D-0.2c/0 -K -O >> $PSFILE".format(station_file),
		"echo {:.7g} {:.7g} | gmt psxy $PROJ $LIMS -Gwhite -Sa0.12i -W0.5p -K -O >> $PSFILE".format(grid_output["best_y"], grid_output["best_z"]),
		"echo \"Best misfit (L2): {:.3g} s\" | gmt pstext $PROJ $LIMS -F+cBC -D0/1c -K -O >> $PSFILE".format(grid_output["sigma_ml"]),
		"gmt psscale $PROJ $LIMS -DjLB+w14c/0.5c+jLB+o0.5c -G{} -C{} --FONT_ANNOT_PRIMARY=6p,Helvetica,black -K -O >> $PSFILE".format(colorscale, os.path.join(output_folder, "temp.cpt")),
		"gmt psbasemap $PROJ $LIMS -BWeSn+t\"ID: {}, Best depth: {:.2g}km\" -Bxa{} -Bya{} -O >> $PSFILE".format(pid, grid_output["best_z"], ticscale, 1),
		"gmt psconvert $PSFILE -Tf -A+m1c",
		]

	with open(output_sh, "w") as f:
		f.write("\n".join(output_str))

	time.sleep(0.5)

	os.chmod(output_sh, 0o775)

	time.sleep(0.5)

	subprocess.call(["./{}".format(output_sh)])


	if misfit_file != "":
		labels = []
		abs_times = []
		output_text = []

		c = 0

		for station in grid_output["station_misfit"]:
			for phase in grid_output["station_misfit"][station]:
				output_text.append("{} {}_{} {}".format(c, station, phase, grid_output["station_misfit"][station][phase]))
				c += 1

		with open(misfit_file, 'w') as f:
			f.write("\n".join(output_text))
		print("gnuplot plotter/plot_misfit.gn {} {}".format(misfitplot_file, misfit_file, ))

		subprocess.call("gnuplot -c plotter/plot_misfit.gn {} {}".format(misfitplot_file, misfit_file, ), shell = True)



def plotter(uid, station_list, station_info, args):

	grid = load_numpy_file(args["npy_filename"])
	L2 = grid[:,:,:,0] # 0: get the standard deviation

	print(grid)

	indices = np.where(L2 == L2.min())

	#print(grid.shape)

	#print(indices)

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

	ax = plt.contourf( output.T, levels = np.arange(0,0.5,0.05), cmap = 'rainbow', origin = 'lower')
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
# def netcdf_writer(lb_corner, DX, DZ ):

# 	# https://unidata.github.io/python-training/workshop/Bonus/netcdf-writing/
# 	grp = netCDF4.Dataset("gmt/gridsearch/test.nc", "w")

# 	with open("gridsearch/55_test_grid.npy", 'rb') as f:
# 		grid = np.load(f)

# 	# need array dimensions

# 	N_X, N_Y, N_Z = grid.shape[:3]

# 	print("loaded shape", grid.shape)

# 	# need starting positions + stepsize
# 	lon_dim = grp.createDimension('x', N_X)
# 	lat_dim = grp.createDimension('y', N_Y)


# 	# write a model title for completion with date 
# 	grp.title = "Test"
# 	grp.setncattr_string("")
# 	x = grp.createVariable('x', np.float64, ('x',))
# 	x.units = 'degrees_east'
# 	x.long_name = 'x'
# 	y = grp.createVariable('y', np.float64, ('y',))
# 	y.units = 'degrees_north'
# 	y.long_name = 'y'

# 	print(N_X, N_Y)
# 	print(lb_corner)


# 	x[:] = lb_corner[0] + np.arange(N_X) * DX
# 	y[:] = lb_corner[1] + np.arange(N_Y) * DX

# 	#print(lon[:])
# 	#print(lat[:])

# 	#print(grid[0][0][0][0].shape)

# 	rms_l2 = grp.createVariable("z", np.float64, ('x', 'y', ))

# 	rms_l2.units = 'km'
# 	rms_l2.long_name = "z"


# 	best_depth = 9

# 	rms_l2[:,:] = grid[:,:,best_depth,0]

# 	print(rms_l2)


# 	grp.close()




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


