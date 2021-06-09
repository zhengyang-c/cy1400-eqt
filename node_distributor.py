# goal: use gekko arrays to distribute tasks

import argparse
import pandas as pd
import os
from pathlib import Path



parser = argparse.ArgumentParser()

parser.add_argument("-id")

args = parser.parse_args()

print(args.id)
