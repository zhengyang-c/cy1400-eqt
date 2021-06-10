# cy1400-eqt

Helper and (pre/post)-processing scripts for a data-driven seismology project. Initially for the requirements of a Year 1 Research Module. 

Uses the [EQTransformer model created by S. Mousavi](https://github.com/smousavi05/EQTransformer)

# Table of Contents:

_insert next time_

## Selecting stations and timeframe: ```multi_station.py```

Tools I use to process files from multiple stations.

### 1 What are the .SAC files already present? 

To get all SAC files inside a data folder (recursively, should be a one-off operation). Generates a CSV (comma separated values) with the rqeuired text metadata to locate all the SAC files. 


```
Args:
  --get: Name of parent SAC folder, prints to output option
  -o: Output file
```

### 2 Choosing your stations

Subsequently, choose a set of stations using a text file, separated by linebreaks.

Example:

```
(TA.txt)

TA01
TA02
```
### 3 Choosing a time period and generating HDF5 files

The same script can cut the generated .csv file (in Part 1) for feeding into ```sac_to_hdf5.py```. 

```
Args:
  -sf: txt file that chooses the stations
  -i: csv file generated in Part 1
  -o: csv file that is filtered using the station list, and the selected start and end dates
  -s: Start date (inclusive). By default, this is the Year and Julian day separated with an underscore e.g. 2019_123
  -e: End date (inclusive). 
  -m: In case for some reason you want to select the whole month (2020_03 to select the first day of March)
```

Sample:

```
$ python multi_station.py -sf station/test_select.txt -i station/all_aceh_sac.csv -o station_time/7jun_testselect.csv -s 2020_085 -e 2020_086
```

### Plotting station up-time

Generates a 18 by 12 inch (150dpi) image. Doesn't work well with many days because all the xtics are so squeezed together. 

## Encode function to prepare for multi-station running over multiple HPC nodes

Given the number of arguments, it makes sense to write a bash script to store all the needed arguments. 

use multi_station encode fn

then edit multi_eqt.pbs, would be nice to have screenshots


**Important Args (need these to use):**

```
  -i: station list text file, endline separated
  -o: filepath to save a .csv file with all the required metadata
  -job: job name - a unique string identifier for your jobs, defaults to timestamp
  -s: start day in %Y_%j format (4 digit year and julian day separated by underscore)
  -e: end day, similar format'''


**Args to select functionality (without the flag, it is false)**

```
  -writehdf5: flag to write from sac to hdf5 folder
  -runeqt: flag to run prediction (multi-run and merge)
  -ploteqt: flag to cut 150s SAC traces'''


**Optional Args (settings, etc):**
```
  -detparent: parent folder to keep detection output files. defaults to "detection/job_name"
  -hdfparent: parent folder to keep hdf5 files. defaults to "prediction_files/job_name"
  -modelpath: path to model, defaults to my copy of EqT default model
  -n_multi: no. of times to repeat prediction, default 20
  -n_nodes: no. of HPC nodes to use, default 20'''


## Writing HDF5 file model input: ```sac_to_hdf5.py'''

Performs bandpass filter from 1 to 45 Hz with 2 corners with zero phases, following the preprocessing by S. Mousavi. Resamples to 100 Hz, then performs a demean.

Writes to ```output_folder```, creating subfolders named by station. The generated HDF5 file and .csv file (which are required for input to EQTransformer) also share the station name.

Also, since it is assumed that there will be 3 channel files for each station, if there are fewer files than expected, it will make an uptime image inside the log folder with a timestamp.

```
Args:
  csv_path: path to csv generated by multi_station -sf
  output_folder: parent directory in which to create station-named folders. it will makedir the output_folder if it doesn't exist.
  station_json: a json file with coordinates that I'll document next time
  
Optional:
  -t: logs the amount of time taken for the script to run to this text file (the text file needs to exist
  -p: no. of processors but I might remove this in the future
```

Sample:

``` $ python sac_to_hdf5.py station_time/TA19_085.txt prediction_files/7jun_TA19.085 station_list.json ```

