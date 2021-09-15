import numpy as np
from scipy.spatial.transform import Rotation as R
from numpy.linalg import inv

import argparse

def rotate(input_file, output_file, az):
	#input_file = "main/sumatra_test.xy"

	#output_file = "main/sumatra_test_rotated.xy"

	# https://math.stackexchange.com/questions/2303869/tensor-rotation

	# read the file

	print(az)

	data = []

	with open(input_file, "r") as f:
		for line in f:
			data.append(line.split(" "))

	modified_data = []

	# mrr mtt mpp mrt mrp mtp
	for thing in data:
		T = np.array([
		[float(x) for x in [thing[3],thing[6],thing[7]]],
		[float(x) for x in [thing[6],thing[4],thing[8]]], 
		[float(x) for x in [thing[7],thing[8],thing[5]]],
		])
		#print(T)
		r = R.from_euler('xz', [az, 90], degrees=True)
		#print(r.as_matrix())

		r_prime = inv(r.as_matrix())
		# T' = R T R'
		T_prime = np.matmul(np.matmul(r.as_matrix(), T), r_prime)
	#	print(T_prime)

		_data = [thing[x] for x in range(3)]
		_data.extend(['{0:.2f}'.format(x) for x in [T_prime[0][0], T_prime[1][1], T_prime[2][2], T_prime[0][1], T_prime[0][2], T_prime[1][2]]])
		_data.extend([thing[x] for x in range(9,13)])

		modified_data.append(_data)


	with open(output_file, "w") as f:
		for line in modified_data:
			f.write(" ".join(line))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('input_file', metavar="input", help='Input .xy beachball file from GCMT, in GMT format', type=str, nargs=1)
	parser.add_argument('output_file', metavar="output", help='Output .xy with rotated beachball', type=str, nargs=1)
	parser.add_argument('az', metavar='az', help="Counterclockwise rotation along North axis. ", type=float, nargs=1)

	args = parser.parse_args()

	rotate(args.input_file[0], args.output_file[0], args.az[0])
# construct the tensor

# rotate the tensor

# write the file