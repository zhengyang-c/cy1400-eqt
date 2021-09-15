#!/usr/bin/python

# input:
# 
# output:
# 

import matplotlib

import matplotlib.pyplot as plt 
import numpy as np
import glob
import os
import sys
import argparse

def str_to_datetime(x):
	try:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	except:
		return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")


def plot(output_file):

	# ordered:
	# not reallllly needed 
	folder_list = [ 
	"imported_figures/frozenlayer_expt/18mar_frozenlayers_aceh_LR1e-3", 
	"imported_figures/frozenlayer_expt/22mar_frozenlayers_aceh_LR1e-4", 
	"imported_figures/frozenlayer_expt/22mar_frozenlayers_aceh_LR1e-5", 
	"imported_figures/frozenlayer_expt/17mar_frozenlayers_aceh_LR1e-6", 
	"imported_figures/frozenlayer_expt/22mar_frozenlayers_aceh_LR1e-7", 
	"imported_figures/frozenlayer_expt/22mar_frozenlayers_aceh_LR1e-8", 
	"imported_figures/frozenlayer_expt/19mar_frozenlayers_aceh_LR1e-9", 
	"imported_figures/frozenlayer_expt/22mar_frozenlayers_aceh_LR1e-10",]

	LR = [-3, -4, -5, -6, -7, -8, -9, -10]


	manual_pick_list = [
	"manual/22mar_frozen/18mar_lr1e-3_repick.txt",
	"manual/22mar_frozen/22mar_fro_LR1e-4.txt",
	"manual/22mar_frozen/22mar_fro_LR1e-5.txt",
	"manual/22mar_frozen/17mar_frozen_repick_LR1e-6.txt",
	"manual/22mar_frozen/22mar_fro_LR1e-7.txt",
	"manual/22mar_frozen/22mar_fro_LR1e-8.txt",
	"manual/22mar_frozen/19mar_freeze_repick_LR1e-9.txt",
	"manual/22mar_frozen/22mar_fro_LR1e-10.txt",
	]

	AB_grad_sys = {"a":0, "b":0, "z": 0}

	def get_gradings(text_file, grad_sys):
		for key in AB_grad_sys:
			AB_grad_sys[key] = 0

		gradings = [] 
		with open(text_file, "r") as f:
			for line in f:
				grade = line.strip().split(",")[1].lower()
				grad_sys[grade] += 1
		
		return grad_sys

	output_str = "" 
	for c, i in enumerate(manual_pick_list):
		_yes = get_gradings(i, AB_grad_sys)
		_temp = [_yes[key] for key in _yes]
		output_str += "{}".format(LR[c])
		for _t in _temp:
			output_str += "\t{}".format(_t)

		output_str += "\n"

	with open(output_file, "w") as f:
		f.write(output_str)

	#print(get_gradings(manual_pick_list[0],  AB_grad_sys))	



	# gradings: A B Z
	# A: unambiguous, quality
	# B: not very good
	# Z: noise or can't tell
	


#plot()
plot("plot_data/26mar_frozenlayer_aceh_precision.txt")