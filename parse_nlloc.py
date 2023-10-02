from pprint import PrettyPrinter
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import argparse as ap
from pathlib import Path

def main(search_folder, phase_output, event_output):

	# search_folder = "/home/zy/NonLinLoc/nlloc_owntest/obs_test"

	# event_output = "nll/test_event.csv"
	# phase_output = "nll/test_phase.csv"

	file_list = [str(p) for p in Path(search_folder).rglob("last.hyp")]

	master_df = []
	phase_df = []

	for f in file_list:
		event_id = f.split("/")[-2]
		e_meta, e_phase = parse_hyp_file(f)
		phase_df.append(e_phase)
		master_df.append(pd.DataFrame(e_meta, index = [event_id,]))

	master_df = pd.concat(master_df, )
	phase_df = pd.concat(phase_df,)
	master_df.index.name = "ID"

	phase_df.to_csv(phase_output, index = False)
	master_df.to_csv(event_output)



def parse_hyp_file(file_path):
	
	event_id = file_path.split("/")[-2]

	with open(file_path, "r") as f:
		text_data = [x for x in f.read().split("\n") if len(x)]

	event_metadata = {}
	phase_data = pd.DataFrame()
	c = 0

	phase_flag = False

	for line in text_data:
		_x = [x for x in line.split(" ") if len(x)]
		if "GEOGRAPHIC" in line:
			origin_time_str = _x[2:8]
			lat_str = _x[9]
			lon_str = _x[11]
			dep_str = _x[13]
			origin_time_dt = datetime.datetime.strptime(" ".join(origin_time_str), "%Y %m %d %H %M %S.%f")

			event_metadata["origin_time"] = origin_time_dt
			event_metadata["best_lon"] = float(lon_str)
			event_metadata["best_lat"] = float(lat_str)
			event_metadata["best_depth"] = float(dep_str)
		
		elif "VPVSRATIO" in line:
			event_metadata["vpvs_ratio"] = float(_x[2])

		elif "STATISTICS" in line:
			event_metadata["cov_xx"] = float(_x[8])
			event_metadata["cov_xy"] = float(_x[10])
			event_metadata["cov_xz"] = float(_x[12])
			event_metadata["cov_yy"] = float(_x[14])
			event_metadata["cov_yz"] = float(_x[16])
			event_metadata["cov_zz"] = float(_x[18])

		elif "STAT_GEOG" in line:
			event_metadata["expect_lat"] = float(_x[2])
			event_metadata["expect_lon"] = float(_x[4])
			event_metadata["expect_depth"] = float(_x[6])
		
		elif "QML_OriginQuality" in line:
			event_metadata["RMS"] = float(_x[12])
			event_metadata["gap"] = float(_x[14])
			event_metadata["n_phases"] = float(_x[2])

		elif "QML_OriginUncertainty" in line:
			event_metadata["min_hor_unc"] = float(_x[4])
			event_metadata["max_hor_unc"] = float(_x[6])
			event_metadata["az_max_hor_unc"] = float(_x[8])
		
		elif "ConfidenceEllipsoid" in line:
			event_metadata["semi_major_axis_length"] = float(_x[2])
			event_metadata["semi_minor_axis_length"] = float(_x[4])
			event_metadata["semi_int_axis_length"] = float(_x[6])
			event_metadata["major_axis_plunge"] = float(_x[8])
			event_metadata["major_axis_azimuth"] = float(_x[10])
			event_metadata["major_axis_rotation"] = float(_x[12])


		if "PHASE ID" in line:
			phase_flag = True
			continue

		if "END_PHASE" in line:
			phase_flag = False

		if phase_flag:
			phase_data.at[c, "ID"] = event_id
			phase_data.at[c, "station"] = _x[0]
			phase_data.at[c, "phase"] = _x[4]
			phase_data.at[c, "error_mag"] = _x[10]
			phase_data.at[c, "tt_pred"] = _x[15]
			phase_data.at[c, "residual"] = _x[16]
			phase_data.at[c, "weight"] = _x[17]

			c += 1

	return event_metadata, phase_data

	"""
	desired statistics:

	geographic OT, geographic location

	RMS 
	vpvs, 
	what's diff?

	cov xx, xy, xz, yy, yz, zz

	ellaz1, dip1, len1, az2, dip2, len2, len3

	don't need ellipse parameters if i am plotting covariance ellipsoids in like matlab
	want to: have a measure of total area uncertainty, only plot those in 3D with error ellipsoids if the volume is less than some number

	stat: expectlat,long,depth

	qml confidence llipsoid parameters

	focal mech: 

	residual distribution
	"""



if __name__ == "__main__":
	a = ap.ArgumentParser(description="looks for last.hyp files in a folder recursively and compiles phase and event info into two dataframes")
	a.add_argument('-i', "--input", help = "input folder to search for NLL .hyp files")
	a.add_argument('-p', "--phase", help = "phase output file path")
	a.add_argument("-e", "--event", help = "event output file path")

	args = a.parse_args()

	main(args.input, args.phase, args.event)