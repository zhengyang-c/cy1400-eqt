import json
import pandas as pd
import os
import argparse as ap
import datetime
from multiprocessing import Pool
import multiprocessing

def main(target_dir, vel_file, phase_json, station_file, run = False):
	
	params = {
		# "target_dir": "/home/zy/NonLinLoc/nlloc_owntest",
		"target_dir": target_dir,
		"p_header": "A",
		"s_header": "T0",
		"p_err": 0.03,
		"s_err": 0.06,
		"n_cpus" : 20,

		# location success criteria
		"min_p": 1,# min no. of P/S phases
		"min_s": 1,
		"min_ps": 4,
		"rms_max": 0.5,# max rms residual of travel times for a successful location
		"p_res_max": 0.3,# max travel time residual for P phase
		"s_res_max": 0.5,# max travel time residual for S phase
		"station_gap_max": 270,

		"vel_type": 1,
		# "vel_file": "/home/zy/NonLinLoc/nlloc_owntest/vel.mod",
		"vel_file": vel_file,

		# "phase_json":"/home/zy/cy1400-eqt/real_postprocessing/julaug_20_assoc/julaug_phases_traveltimes.json",
		"phase_json": phase_json,
		"nll_ctrl_name":"ctrl.nll", 

		"obs_file": "data.obs",
		"obs_file_dir": "obs_test",
		"loc_dir_base": "loc_test",
		"model_dir_base": "model_test",
		"time_dir_base": "time_test",
		"input_dir": "input_test",
		# "station_file": "/home/zy/NonLinLoc/nlloc_owntest/new_station_info_elv.dat", 
		"station_file": station_file,
		"lat_orig": 5.0,
		"lon_orig": 95.5,
		"vpvs": 1.73,
		"VGGRID" : "2 481 51 0.0 0.0 0.0 1 1 1 SLOW_LEN",
		"LOCGRID":"481 481 41 -240.0 -240.0 0.0 1 1 1 PROB_DENSITY SAVE",
		"OCT_LOC":"30 30 10 0.01 150000 15000 0 1",

		"obs_file_virtual": 'virtual_file.obs', 
		"proj_name": "AcehLoc",
		"wave_type": 1,
		"obs_type":"NLLOC_OBS",
	}

	#station_file = "station_YeU.dat" # format: sta lat lon ele(m)
	#vel_file = "YeU_model.dat" # format 1: depth_top vp vs pho
								# format 2: thickness vp vs pho

	global phase_data
	with open(params["phase_json"], "r") as f:
		phase_data = json.load(f)


	for _k in ["obs_file_dir", "loc_dir_base", "model_dir_base", "time_dir_base", "input_dir"]:
		params[_k] = os.path.join(params["target_dir"], params[_k])

		if not os.path.exists(params[_k]):
			os.makedirs(params[_k])

	# calculate travel times
	nll_input = os.path.join(params["target_dir"], params["nll_ctrl_name"])
	params["nll_input"] = nll_input

	loc_dir_virtual = os.path.join(params["loc_dir_base"], 'loc_virtual')
	
	default_nll = os.path.join(params["target_dir"], params["nll_ctrl_name"])

	obs_file_virtual = 'virtual_file.obs'

	print('calculating P travel times...')
	w_nll_input(params, 'P', loc_dir_virtual, params["obs_file_virtual"], default_nll )
	print(nll_input)

	if not run:
		os.system('Vel2Grid {}'.format(nll_input))
		os.system('Grid2Time {}'.format(nll_input))
		if params["wave_type"] == 1:
			print('calculating S travel times...')
			w_nll_input(params, 'S', loc_dir_virtual, params["obs_file_virtual"], default_nll)
			os.system('Vel2Grid {}'.format(nll_input))
			os.system('Grid2Time {}'.format(nll_input))

		neve_good = 0

		loc_success_sum_file = params["loc_dir_base"] + 'loc_success_sum.hyp'
		pha_file_hypodd = params["obs_file_dir"] + 'phase_success_sum.pha'
		pha_file_outlier = params["obs_file_dir"] + 'phase_outlier_sum.obs'
		t_dist_file = params["loc_dir_base"] + 't_dist.dat'
		pha_res_file = params["loc_dir_base"] + 'phase_res.dat'
		eve_loc_sum_file = params["loc_dir_base"] + 'event_info.dat'

		w_phase_from_json(phase_data, params)


	event_id_list = list(phase_data.keys())

	target_file_list = [os.path.join(params["obs_file_dir"], x, params["nll_ctrl_name"]) for x in event_id_list]

	print(target_file_list)


	if run:	
		with Pool(multiprocessing.cpu_count()) as p:
			p.map(nll_runner, target_file_list)


	#w_nll_input(params, 'S', os.path.join(params["loc_dir_base"], "002639"), os.path.join(params["obs_file_dir"], "002639", params["obs_file"]))


def nll_runner(target_file):
	print(target_file)
	os.system("NLLoc {}".format(target_file))

def w_nll_input(params, phase_type, loc_dir, target_phase_file, target_nll_ctrl):
	with open(target_nll_ctrl, 'w') as f_nll:
		f_nll.write('CONTROL 1 54321\n')
		f_nll.write('\n')

		f_nll.write('TRANS SDC {:10.6f} {:11.6f} 0.0\n'.format(params["lat_orig"], params["lon_orig"]))
		f_nll.write('\n')

		f_nll.write('VGOUT {}\n'.format(os.path.join(params["model_dir_base"], params["proj_name"])))
		f_nll.write('VGTYPE {}\n'.format(phase_type))
		f_nll.write('VGGRID {}\n'.format(params["VGGRID"]))

		with open(params["vel_file"] , 'r') as f_vel:

			if "csv" in params["vel_file"]:
				vf = pd.read_csv(params["vel_file"])
				vf.sort_values("depth", inplace = True)
				for index, row in vf.iterrows():
					f_nll.write('LAYER {:6.2f} {:6.3f} 0.00 {:6.3f} 0.00 {:5.2f} 0.00\n'.format(
						row.depth,
						row.v_p,
						row.v_s,
						3.0
					))

			
			elif params["vel_type"] == 1:
				for line in f_vel:
					if len(line) > 0:
						depth_top, vp, vs, pho = line.strip().split()
						f_nll.write('LAYER {:6.2f} {:6.3f} 0.00 {:6.3f} 0.00 {:5.2f} 0.00\n'.format(
							float(depth_top), float(vp), float(vs), float(pho) ) )
			elif params["vel_type"] == 2:
				dep_top = 0.0
				for line in f_vel:
					thk, vp, vs, pho = line.strip().split()
					f_nll.write('LAYER {:6.2f} {:6.3f} 0.00 {:6.3f} 0.00 {:5.2f} 0.00\n'.format(
						float(depth_top), float(vp), float(vs), float(pho) ) )
					dep_top += thk
			

		f_nll.write('\n')

		f_nll.write('GTFILES {} {} {} 0\n'.format(os.path.join(params["model_dir_base"], params["proj_name"]), os.path.join(params["time_dir_base"],params["proj_name"]) , phase_type) )
		f_nll.write('GTMODE GRID2D ANGLES_YES\n')
		with open(params["station_file"] , 'r') as f_sta:
			for line in f_sta:
				sta_nm, sta_lon, sta_lat, sta_ele = line.strip().split('\t')
				f_nll.write('GTSRCE {:<6s} LATLON {:10.6f} {:11.6f} 0.00 {:6.3f}\n'.
					format(sta_nm, float(sta_lat), float(sta_lon), float(0.0)/1000.0 ) )

		f_nll.write('\n')
		f_nll.write('GT_PLFD 0.0001 0\n')
		f_nll.write('\n')

		f_nll.write('LOCFILES {} {} {} {} 0\n'.format(
			target_phase_file , 
			params["obs_type"] , 
			os.path.join(params["time_dir_base"], params["proj_name"]) , 
			os.path.join(loc_dir, params["proj_name"])))
		f_nll.write('LOCHYPOUT SAVE_NLLOC_ALL FILENAME_DEC_SEC\n')
		f_nll.write('LOCSEARCH OCT {}\n'.format(params["OCT_LOC"] ) )
		f_nll.write('LOCMETH EDT_OT_WT 9999.0 {} 9999 {} -1 -1 -1 1\n'.format(params["min_ps"] , params["min_s"] ))
		f_nll.write('LOCGAU 0.1 0.0\n')
		f_nll.write('LOCGAU2 0.02 0.03 2.0\n')
		f_nll.write('LOCQUAL2ERR 0.01 0.05 0.1 0.5 1.0\n')
		f_nll.write('LOCGRID {}\n'.format(params["LOCGRID"] ) )

def parse_format(x):
	#"station_P": "2020-01-01 03:54:25.630000",
	if ":" in x:
		try:
			y = datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
		except:
			y = datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
	else:
		try:
			y = datetime.datetime.strptime(x, "%Y%m%d-%H%M%S.%f")
		except:
			y = datetime.datetime.strptime(x, "%Y%m%d-%H%M%S")
	
	return y

def write_ts(ts, phase, sta, err):

	ts = parse_format(ts)

	ymd = '{}{:02d}{:02d}'.format(ts.year, ts.month, ts.day)
	hm = '{:02d}{:02d}'.format(ts.hour, ts.minute)
	sec = ts.second + ts.microsecond/1e6

	network = "AC"
	write_str = '{:<6s} {:4s} {:4s} {:1s} {:6s} {:1s} {} {} {:7.4f} {:3s} {:9.2e} {:9.2e} {:9.2e} {:9.2e} {:9.2e} \n'.format(sta, network, '?', '?', phase, '?', ymd, hm, sec, 'GAU', err, -1, -1, -1, 1 ) 

	return write_str


def w_phase_from_json(phase_data, params):
	# output file location: 
	for event_id in phase_data:
		target_folder = os.path.join(params["obs_file_dir"], event_id)
		if not os.path.exists(target_folder):
			os.makedirs(target_folder)

		with open(os.path.join(target_folder, params["obs_file"]), "w") as f:
			print("opening {}".format(os.path.join(target_folder, params["obs_file"])))
			for sta in phase_data[event_id]["data"]:
				if "P" in phase_data[event_id]["data"][sta]:
					ts = phase_data[event_id]["data"][sta]["station_P"]
					f.write(write_ts(ts, "P", sta, params["p_err"]))
				if "S" in phase_data[event_id]["data"][sta]:
					ts = phase_data[event_id]["data"][sta]["station_S"]
					f.write(write_ts(ts, "S", sta, params["s_err"]))

			f.write("\n")

		w_nll_input(params, "S", target_folder, os.path.join(target_folder, params["obs_file"]), os.path.join(target_folder, params["nll_ctrl_name"]))


if __name__ == "__main__":

	ap = ap.ArgumentParser()
	ap.add_argument("-dir", "--target_dir")
	ap.add_argument("-p", "--phase_json")
	ap.add_argument("-v", "--vel_file")
	ap.add_argument("-sta", '--station_file')
	ap.add_argument("-r", "--run", action = "store_true", )
	args = ap.parse_args()
	main(args.target_dir, args.vel_file,args.phase_json,  args.station_file, args.run)