# goal: use gekko arrays to distribute tasks

# prepare csv files so upon receiving an ID each script can do a lookup and get the files they need

import argparse
import pandas as pd
import os
from pathlib import Path

# load station selector file





parser = argparse.ArgumentParser()

parser.add_argument("-id")

args = parser.parse_args()

print(args.id)
