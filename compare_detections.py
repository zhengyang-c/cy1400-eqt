import os
import argparse
import numpy as np

import math
import random

import datetime
import pandas as pd

from pathlib import Path


def main(known_picks, unknown_sac_folder):

	sac_tracename = [str(path).split("/")[-1].split(".png")[0] for path in Path(unknown_sac_folder).rglob('*.png')]

	print(sac_tracename)

	graded_traces = []
	grades = []

	with open(known_picks, "r") as f:
		for line in f:
			_x = line.strip().split(",")
			graded_traces.append(_x[0])
			grades.append(_x[1])

	#print(graded_traces)

	matched_indices = []
	matched_grades = []

	# i know this is stupid but like i'm not bothered enough?? to use a pandas dataframe

	for unknown_sac in sac_tracename:
		if unknown_sac in graded_traces:
			_index = graded_traces.index(unknown_sac)
			matched_indices.append(_index)

			matched_grades.append(grades[_index])

	grade_counter = {}

	for _g in matched_grades:
		if _g not in grade_counter:
			grade_counter[_g] = 1
		else:
			grade_counter[_g] += 1

	print(grade_counter)


main("manual/21mar_default_multi_repicked.txt", "imported_figures/27mar_wholemonth_aceh1e-6frozen/TA19_outputs/sac_picks")

