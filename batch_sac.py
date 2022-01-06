from pathlib import Path
import argparse
import os
import time


def main(input_folder, output_sh):
	output_str = ""

	file_list = [str(p) for p in Path(input_folder).glob("*SAC")]

	for f in file_list:
		output_str += "printf 'r {}\\ninterpolate delta 0.01\\nw over\\nq\\n' | sac \n".format(f)	

	with open(output_sh, "w") as f:
		f.write(output_str)
	
	time.sleep(1)

	os.chmod(output_sh, 0o775)

	

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("input_folder")
	ap.add_argument("output_sh")
	args = ap.parse_args()
	main(args.input_folder, args.output_sh)