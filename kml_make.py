import simplekml
import argparse
import pandas as pd

from utils import parse_event_coord

# inputs: coordinates from different sources 
# output: kml file that can be imported into google earth
# 
# want to support: .csv file, .reloc file, REAL output


# taken from search_grid.py