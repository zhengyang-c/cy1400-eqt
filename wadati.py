import argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

# the problem:

# the input phase file (phase.dat or converted into dictionary as phase.json)
# is produced by REAL; relocation has not be performed yet
# 
# want to: use the 'observations' to get SP times / P arrival relative to  using the sac files in the event catalogue
#
# how: first do 5 jul catalogue since i haven't organised ? 
# 
# then export the 7 jul catalogue and like see what they want to do with it
# 

def main():

	# load the json, include plotting point only if both P and S are present


	with open("real_postprocessing/5jul_assoc/5jul_aceh_phase.json", 'r') as f:
		phase_dict = json.load(f)

	# this uses REAL output arrival times 

	# df_real = pd.DataFrame()

	# c = 0

	# for k in phase_dict:
	# 	for sta in phase_dict[k]["data"]:
	# 		if "P" in phase_dict[k]["data"][sta] and "S" in phase_dict[k]["data"][sta]:
	# 			df_real.at[c, "SP_diff"] = float(phase_dict[k]["data"][sta]["S"]) - float(phase_dict[k]["data"][sta]["P"])
	# 			df_real.at[c, "P"] = float(phase_dict[k]["data"][sta]["P"])
	# 			c += 1

	# print(df_real)

	#df_real.to_csv("real_postprocessing/5jul_assoc/5jul_wadati_real.csv")

	df_dd = pd.read_csv("real_postprocessing/5jul_assoc/wadati_P_Stimes.txt", delim_whitespace = True, names = ["path", "day", "time", "sta", "O", "P", "S"])


	df_dd["SP_diff"] = df_dd["S"] - df_dd["P"]

	# use the json to filter via a direct table lookup

	for index, row in df_dd.iterrows():

		ev_id = row.path.split("/")[0]
		try:
			if "P" in phase_dict[ev_id]["data"][row.sta] and "S" in phase_dict[ev_id]["data"][row.sta]:
				df_dd.at[index, "both"] = 1
			else:
				df_dd.at[index, "both"] = 0
		except:
			if "P" in phase_dict[ev_id]["data"][row.sta[:-1]] and "S" in phase_dict[ev_id]["data"][row.sta[:-1]]:
				df_dd.at[index, "both"] = 1
			else:
				df_dd.at[index, "both"] = 0

	df_dd[df_dd["both"] == 1][["SP_diff", "P"]].to_csv("real_postprocessing/5jul_assoc/5jul_wadati_dd.csv")

	# this uses hypoDD output arrival times

	# load the wadati txt file and use the json to filter


	

main()

