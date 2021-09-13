import numpy as np
import pandas as pd
import os
from subprocess import check_output
import matplotlib.pyplot as plt

# assuming that points define the bottom of a layer, and that
# first column is height of layer, then v_s, v_p
# want to have many many layers so it can interpolate between many points
# also because there are a lot of shallow events, so the velocity
# behaviour near the surface is going to be important


def txt_velocity_model():

	layer_depth = [0, 5, 10, 20, 30, 40, 50,] # bottom
	layer_velocities = [5.2, 5.5, 6, 6.6, 7.6, 8.0, 8.1]
	vp_vs = 1.76 # from wadati plot

	
	max_depth = 60 # for reasons ...

	# or just have 1 km depth from 0 to 20, then 5 km depths until 5, 
	# think the last layer is like 0 km depth because that should specify the model for the rest of it
	# 
	# 
	# 
	output_depth = []
	output_vp = []
	output_vs = []

	for i in range(len(layer_depth) - 1):
		gradient = (layer_velocities[i+1] - layer_velocities[i])/(layer_depth[i+1] - layer_depth[i])

		for j in range(layer_depth[i] + 1,layer_depth[i+1] + 1):
			new_vp = (gradient * (j - layer_depth[i] - 0.5)) + layer_velocities[i] 

			output_vp.append(new_vp)
			output_vs.append(new_vp / vp_vs)
			output_depth.append(float(j))


	with open("txt_model_dlange_corr2.txt", "w") as f:
		for i in range(len(output_depth)):
			f.write("{:.5g}\t{:.5g}\t{:.5g}\n".format(1, output_vs[i], output_vp[i])) # it's probably model thicknesss

#txt_velocity_model()

def generate_tt():
	# call trav.pl
	# trav.pl [p | s]  model_file source_depth distances
	
	distance_range = 451
	depth_range = 41

	tt = np.zeros([distance_range, depth_range, 2])

	for i in range(0, distance_range):
		print(i)
		for j in range(0, depth_range):

			out = check_output(["./trav.pl", "p", "txt_model_dlange_corr2.txt", str(j), str(i)])
			out = [float(x) for x in out.decode('UTF-8').strip().split(" ") if x != ""]
			tt[i][j][0] = out[1]

			out = check_output(["./trav.pl", "s", "txt_model_dlange_corr2.txt", str(j), str(i)])
			out = [float(x) for x in out.decode('UTF-8').strip().split(" ") if x != ""]

			tt[i][j][1] = out[1]

	with open("model_dlange2_451km.npy", "wb") as f:
		np.save(f, tt)

def check_tt():

	with open("model_dlange2.npy", "rb") as f:
		tt = np.load(f)

	# first plot the velocity model
	plt.title("velocity model, v_p")
	plt.imshow(tt[:,:,0].T, origin = "lower", cmap = 'rainbow')
	plt.ylabel("Depth [km]")
	plt.xlabel("Distance [km]")
	plt.colorbar()
	plt.show()


generate_tt()
	# next, plot a colormap of the travel time table you have


