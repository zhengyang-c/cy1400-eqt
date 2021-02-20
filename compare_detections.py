# this will compare n lists, building a global list
# used for comparing no. of detections across different runs
# written to compare preproced/ not preprocessed, but can be used to
# compare multiple runs as well

import glob
import os
import argparse
import numpy as np

def main(output_file, *input_folder):
	# use the png to get the date time station since the channels are not impt for this
	
	print(output_file)
	global_list = set()
	indiv_list = []

	for f in input_folder[0]:
		_indiv_set = set()
		for event_name in glob.glob(os.path.join(f, "*.png")):
			name = event_name.split("/")[-1].split(".")
			_name = event_name.split("/")[-1]
			# check +/- 1 second
			name1 = "{}.{}.{}.{}.png".format(name[0], name[1], name[2], int(name[3]) + 1)
			name2 = "{}.{}.{}.{}.png".format(name[0], name[1], name[2], int(name[3]) - 1)
			#print(name1)
			#print(name2)
			#if all([x not in global_list for x in [name1, name2, _name]]):
			global_list.add(_name)
			_indiv_set.add(_name)
		indiv_list.append(_indiv_set)


	image = np.zeros((len(global_list), len(indiv_list)))

	for b, i in enumerate(global_list):
		for c, j in enumerate(indiv_list):
			if i in j:
				image[b][c] = 1
	#print(image)

	headers = ["n", "file_name"]
	headers.extend(input_folder[0])

	#print(headers)
	with open(output_file, 'w') as f:
		f.write("\t".join(headers) + "\n")
		for c, file_name in enumerate(sorted(list(global_list))):
			to_write = "{}\t{}".format(c, file_name)
			for i in image[c]:
				to_write += "\t" + str(int(i))
			to_write += "\n"
			f.write(to_write)

	# for every event in global_list (which is a year month day hour minute second timestamp)
	# load 2 x 3 SAC files (for some specified folders)	


	
# output :
# lookup table: 
# column: all possible files | folder name | folder name 
# TA001XXXX.png | 1 | 1
# image: just to visually see the difference

# i think the purpose is to be able to cut / compare the diff? idk 



parser = argparse.ArgumentParser()
parser.add_argument('output_file', type = str)
parser.add_argument('input_folder', type = str, nargs='*')

args = parser.parse_args()

main(args.output_file, args.input_folder)
