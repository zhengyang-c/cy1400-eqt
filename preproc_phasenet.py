import os
import pandas as pd
import argparse
from pathlib import Path

def main(input_folder, output_csv):
	# output_csv = ""
	# input_folder = "csi/phasenet_test/"

	# do a glob of input folder, 

	sac_file_list = [str(p) for p in Path(input_folder).rglob("*SAC")]

	df = pd.DataFrame()
	odf = pd.DataFrame()

	df["full_path"] = sac_file_list
	
	for index, row in df.iterrows():
		df.at[index, "event_id"] = row.full_path.split("/")[-2]
		df.at[index, "uid"] = ".".join(row.full_path.split("/")[-1].split(".")[:4])

	c = 0

	for _, _df in df.groupby("uid"):
		_df = _df.reset_index()
		odf.at[c, "fname"] = os.path.join(_df["event_id"].iloc[0], _df["uid"].iloc[0])
		odf.at[c, "E"] = os.path.join(_df["event_id"].iloc[0], _df["uid"].iloc[0] + ".EHE.SAC")
		odf.at[c, "N"] = os.path.join(_df["event_id"].iloc[0], _df["uid"].iloc[0] + ".EHN.SAC")
		odf.at[c, "Z"] = os.path.join(_df["event_id"].iloc[0], _df["uid"].iloc[0] + ".EHZ.SAC")
		c += 1

	print(odf.head)

	odf.to_csv(output_csv, index = False)

if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("input_folder")
	ap.add_argument("output_csv")
	args = ap.parse_args()
	main(args.input_folder, args.output_csv)