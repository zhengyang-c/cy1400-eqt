"""
Compare USGS events to events in catalogue:

1) do the big events match?
2) if they match
3) if they don't match, 

I can see the future: i have to write the association script mysef

"""
import pandas as pd
import numpy as np
from obspy.geodetics import gps2dist_azimuth

def parse_station_info(input_file):
	# 'reusing functions is bad practice' yes haha

	station_info = {}

	with open(input_file, 'r') as f:
		for line in f:
			#print(line)
			try:
				sta, lon, lat = [x for x in line.strip().split("\t") if x != ""]
			except:
				sta, lon, lat = [x for x in line.strip().split(" ") if x != ""] 
			station_info[sta] = {"lon": float(lon), "lat": float(lat)}	
	return station_info
def dx(X1, X2):
	"""
	
	takes in two coordinate tuples (lon, lat), (lon, lat) returning their distance in kilometres
	gps2dist_azimuth also returns the azimuth but i guess i don't need that yet
	it also returns distances in metres so i just divide by 1000

	the order doesn't matter
	
	:param      X1:   The x 1
	:type       X1:   { type_description }
	:param      X2:   The x 2
	:type       X2:   { type_description }

	"""

	#print(X1, X2)
	return gps2dist_azimuth(X1[1], X1[0], X2[1], X2[0])[0] / 1000


def ip(X, Y):
	if len(X) == 3:

		# arithmetic average of in between gradients to approximate gradient at midpoint

		return 0.5 * ((Y[2] - Y[1])/(X[2] - X[1]) + (Y[1] - Y[0])/(X[1] - X[0]))

	if len(X) == 2:
		return (Y[1] - Y[0])/(X[1] - X[0])
		

station_info = parse_station_info('../new_station_info.dat')


# usgs catalogue
udf = pd.read_csv("usgs_aceh.csv")
udf.rename(columns = {"time": "timestamp", "latitude": "LAT", "longitude": "LON", "depth":"DEPTH", "mag": "MAG"}, inplace = True)
# print(udf.columns)
udf['timestamp'] = pd.to_datetime(udf['timestamp']).dt.tz_localize(None)

# detections
# eqt_df = pd.read_csv("../master_csv/eqtfiles/merged_customfilter_jan20-may21.csv") 
eqt_df = pd.read_csv("../master_csv/eqtfiles/merged_merged_jan20-may21.csv")
eqt_df['p_arrival_time'] = pd.to_datetime(eqt_df['p_arrival_time'])
eqt_df['s_arrival_time'] = pd.to_datetime(eqt_df['s_arrival_time'])

# association file
# real_df = pd.read_csv("../master_csv/master_merged_REAL_mags.csv") 
real_df = pd.read_csv("../imported_figures/all_rereal_events.csv")
real_df.drop("MAG", 1, inplace = True)
real_df['timestamp'] = pd.to_datetime(real_df['timestamp'])

# want to know rate of seismicity before the 'mainshock' 
# i.e. want no. of detections 1 hr, 4 hrs, 24 hrs before + 1hr, 4 hrs, and 24 hrs after

match_counter = 0

for index, row in udf.iterrows():
	ASSOC_WINDOW = 4 # symmetric over left and right side

	real_df['dt'] = (real_df['timestamp'] - row.timestamp).astype('timedelta64[s]') # this does rounding to seconds, which is not the same as .total_seconds() in python datetime
	window_real_df = (real_df[(real_df['dt'] < ASSOC_WINDOW ) & (real_df['dt'] > -ASSOC_WINDOW)] )
	if len(window_real_df):

		#print(row.timestamp)
		match_counter += 1

		udf.at[index, 'matched'] = True

		headers = ["ID", "timestamp", "dt", "LON", "LAT", "DEPTH", "m_l", "station_gap", "residual_time", "n_picks"]

		for h in headers:
			try:
				udf.at[index, 'matched_' + h] = window_real_df[h].to_list()[0]
			except:
				pass
		

mudf = (udf[udf['matched'] == 1])# matched usgs dataframe


# for index, row in mudf.iterrows():
# 	mudf.at[index, 'delta_depth'] = row.matched_DEPTH - row.DEPTH
# 	mudf.at[index, 'delta_dist_km'] = dx((row.LON, row.LAT), (row.matched_LON, row.matched_LAT))
# 	mudf.at[index, 'delta_timestamp'] = (row.matched_timestamp - row.timestamp).total_seconds()

# print("mean:")
# print(mudf[["delta_depth", "delta_dist_km", "delta_timestamp"]].mean())
# print("std:")
# print(mudf[["delta_depth", "delta_dist_km", "delta_timestamp"]].std())

# mudf.to_csv("usgs_match.csv", index = False)

# load look up table lol
with open("../gridsearch/model_dlange2_451km-60km.npy", "rb") as f:
	tt = np.load(f)


TT_DX = 1
TT_DZ = 1 
TT_NX = tt.shape[0]
TT_NZ = tt.shape[1]
matched_phases = []

for index, row in udf[udf["DEPTH"] < 80].iterrows(): # the travel time table goes up to 90km but uh
	print(row.timestamp)

	station_dist = {}

	# key ordering is immutable: throw into array and let numpy handle it

	dists = []
	depths = []

	# compute station distances for all stations
	for sta in station_info:
		_dist = dx((row.LON, row.LAT), (station_info[sta]["lon"], station_info[sta]["lat"]))
		dists.append(_dist)

		_depth = row.DEPTH 
		depths.append(_depth)

	dists = np.array(dists)
	depths = np.array(depths)

	dist_indices = np.array([int(round(x)) for x in dists/TT_DX]) # for table interpolation
	depth_indices = np.array([int(round(x)) for x in depths/TT_DZ]) # for table interpolation

	dist_deltas = dists - dist_indices * TT_DX
	depth_deltas = depths - depth_indices * TT_DZ

	# compute theoretical travel time and do interpolation for distance and depth

	dist_grad_P = []
	dist_grad_S = []

	depth_grad_P = []
	depth_grad_S = []

	tt_P = []
	tt_S = []

	for _c, _i in enumerate(dist_indices):
		if _i + 1 > TT_NX:
			_indices = np.array([_i - 1, _i])
		elif _i - 1 < 0:
			_indices = np.array([_i, _i + 1])
		else:
			_indices = np.array([_i - 1, _i, _i + 1]) 
		

		_Y_P = [tt[_x][depth_indices[_c]][0] for _x in _indices]
		_Y_S = [tt[_x][depth_indices[_c]][1] for _x in _indices]

		tt_P.append(tt[_i][depth_indices[_c]][0])
		tt_S.append(tt[_i][depth_indices[_c]][1])

		dist_grad_P.append(ip((_indices) * TT_DX, _Y_P))
		dist_grad_S.append(ip((_indices) * TT_DX, _Y_S))

	for _c, _i in enumerate(depth_indices):
		if _i + 1 > TT_NZ:
			_indices = np.array([_i - 1, _i])
		elif _i - 1 < 0:
			_indices = np.array([_i, _i + 1])
		else:
			_indices = np.array([_i - 1, _i, _i + 1]) 

		depth_grad_P.append(ip((_indices) * TT_DZ, _Y_P))
		depth_grad_S.append(ip((_indices) * TT_DZ, _Y_S))

	dist_grad_P = np.array(dist_grad_P)
	dist_grad_S = np.array(dist_grad_S)
	depth_grad_P = np.array(depth_grad_P)
	depth_grad_S = np.array(depth_grad_S)

	tt_P = np.array(tt_P)
	tt_S = np.array(tt_S)

	tt_P += dist_grad_P * dist_deltas
	tt_S += dist_grad_S * dist_deltas
	tt_P += depth_grad_P * depth_deltas
	tt_S += depth_grad_S * depth_deltas

	for c, sta in enumerate(station_info):
		station_info[sta]["tt_P"] = tt_P[c]
		station_info[sta]["tt_S"] = tt_S[c]

	# given a set of theoretical arrival times, compare with the detection folder for each station

	P_WINDOW = 4 # SYMMETRIC
	S_WINDOW = 8 # SYMMETRIC
	c = 0


	for sta in station_info:
		_eqt_df = eqt_df[eqt_df['station'] == sta].copy() 

		_eqt_df['dt_p'] = ((_eqt_df['p_arrival_time'] - row.timestamp).dt.total_seconds() - station_info[sta]["tt_P"]) 
		_eqt_df['dt_s'] = ((_eqt_df['s_arrival_time'] - row.timestamp).dt.total_seconds() - station_info[sta]["tt_S"])
		_eqt_df['absdt_p'] = ((_eqt_df['p_arrival_time'] - row.timestamp).dt.total_seconds() - station_info[sta]["tt_P"]).abs()
		_eqt_df['absdt_s'] = ((_eqt_df['s_arrival_time'] - row.timestamp).dt.total_seconds() - station_info[sta]["tt_S"]).abs()

		

		if (_eqt_df['absdt_p'].min()) < P_WINDOW and (_eqt_df['absdt_s'].min()) < S_WINDOW:
			if (_eqt_df['absdt_p'].idxmin()) == (_eqt_df['absdt_s'].idxmin()):
				target_index = _eqt_df['absdt_p'].idxmin()
				matched_phases.append(target_index)

				for h in ["id", "matched_ID" ]:
					eqt_df.at[target_index, h] = row[h]

				eqt_df.at[target_index, "dt_p"] = _eqt_df.at[target_index, "dt_p"]
				eqt_df.at[target_index, "dt_s"] = _eqt_df.at[target_index, "dt_s"]


print(matched_phases)

m_df = eqt_df.iloc[matched_phases]
m_df.to_csv("rereal_matched_usgs_eqt.csv", index = False)





		#_eqt_df['dt_p'] = (_eqt_df['p_arrival_time'] - (row.timestamp + tt_P[c])).abs()
		# _eqt_df['dt_p'] = ((_eqt_df['p_arrival_time'] - (row.timestamp)).dt.total_seconds() - tt_P[c]).abs()
		# _eqt_df['dt_s'] = ((_eqt_df['s_arrival_time'] - (row.timestamp)).dt.total_seconds() - tt_S[c]).abs()

		

		#_eqt_df['dt_s'] = (_eqt_df['s_arrival_time'] - (row.timestamp + tt_S[c])).abs()

		# if len(_eqt_df[(_eqt_df['dt_p'] < P_WINDOW)]):
		# #if len(_eqt_df[(_eqt_df['dt_p'] < P_WINDOW) & (_eqt_df['dt_s'] < S_WINDOW)]):
		# 	print("match: ", sta)



# you know, the big brain gridsearch is to simulate events (pre compute them) and compute arrival times for all stations
# and then match 
# the only problem is that the stored model has like 4 dimensions, it will have 2e9 entries
# so that's probably why it's not done yet
# there's probably an efficient way to do it involving interpolation so you don't have to recalculate every single entry



# if the event is deeper than 60km, it's probably plate interface
# my travel time table goes up to


# get average difference in location, magnitude, and time
	
	# match by timestamp, then check 
	# arrival time window? p wave velocity ~ 5km, maybe 1 minute? 
	# there would be a way to calculate theoretical travel times using the look up table + interpolation

