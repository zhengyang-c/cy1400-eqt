# cy1400-eqt
*Helper and (pre/post)-processing scripts for a data-driven seismology project*

> Note:
> -----
> This repository is in maintenance mode as I've since moved on from this project. 

Please refer to the wiki: [Wiki](https://github.com/zhengyang-c/cy1400-eqt/wiki/) for workflows and my notes.


Uses the [EQTransformer model created by S. Mousavi](https://github.com/smousavi05/EQTransformer)

Should this have more folders and less files in the project root? Yes, but relative file paths are a pain + this is not re-usable enough (yet) to package it as a Python module. 

# Workflow

1. Decide what model to use, start date, end date, number of stations (max 20).
2. Make a linebreak separated file with your list of stations
3. Make a csv file using multi_station.py -sf giving the filepaths to all the SAC files for each day and station, for a specified start and end date
