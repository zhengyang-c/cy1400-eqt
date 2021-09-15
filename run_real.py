import subprocess
import pandas as pd
import argparse
import os

# first get folder list

# for each folder, get the Y M D
# copy the perl script over, and run the perl script
# 
# 
# 

folder_list = os.listdir("../Pick")

for folder in folder_list:

	year, month, day = folder[0:4], folder[4:6], folder[:-2]

	