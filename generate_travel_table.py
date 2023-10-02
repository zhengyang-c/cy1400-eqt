import obspy
from obspy.taup import TauPyModel
model = TauPyModel(model="iasp91")


DX = 0.1
DZ = 1

dist = 1.4
dep = 40

n_x = int(dist / DX) + 1
n_z = int(dep / DZ) + 1

for i in range(0, n_z):
	for j in range(1, n_x):
		_dist = DX * j
		_dep = DZ * i

		arrivals = model.get_travel_times(source_depth_in_km = _dep, distance_in_degree = _dist, phase_list = ["P", "S"])

		print(arrivals)