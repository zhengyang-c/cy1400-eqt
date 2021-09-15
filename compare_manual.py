""" compare manual pick files 
ascii files with like timestamp comma 2
where 0 --> noise
1 --> idk

plots a venn diagram because that's all neat and cool but i don't think i'll be using a lot of this


"""


import glob
import os
import argparse
import numpy as np
import re
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib_venn import venn2


#print(len(a.union(b)), " union")
#print(len(a.intersection(b)), " intersection")


def main(output_file):
	# use the png to get the date time station since the channels are not impt for this
	
	files = ["manual/28feb_retrained_700_300_1e-3_manual.txt", "manual/5mar_default_model_manual.txt"]

	all_good_picks = []
	global_list = set()

	for file in files:
		good_picks = []
		with open(file, "r") as f:		
			for line in f:
				if line.split(",")[1].strip() == "2":
					good_picks.append(line.split(",")[0].strip())
					global_list.add(line.split(",")[0].strip())
		good_picks.sort()
		all_good_picks.append(good_picks)

	#print(all_good_picks)

	image = np.zeros((len(global_list), len(files)))


	for b, i in enumerate(sorted(global_list)):
		#print(i)
		for c, j in enumerate(all_good_picks):
			if i in j:
				#print(c)
				image[b][c] = 1
	#print(image)


	headers = ["n", "file_name"]
	headers.extend(files)

	#print(headers)
	with open(output_file, 'w') as f:
		f.write("\t".join(headers) + "\n")
		for c, file_name in enumerate(sorted(list(global_list))):
			to_write = "{}\t{}".format(c, file_name)
			for i in image[c]:
				to_write += "\t" + str(int(i))
			to_write += "\n"
			#print(to_write)
			f.write(to_write)
	venn2([set(all_good_picks[0]), set(all_good_picks[1])], ("retrained", "default"))

	plt.title("28feb_retrained_700_300_1e-3_manual vs default")
	plt.savefig("plots/5mar_compare_retrained_with_default.png", dpi = 300)

main("log/compare_manual_default_vs_retrained_700-300_LR1e-3.txt")

# txt files to compare from 'manual' folder:

# 28feb_retrained_700_300_1e-3_manual.txt
# 5mar_default_model_manual.txt
