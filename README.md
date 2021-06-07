# cy1400-eqt

Helper and (pre/post)-processing scripts for a data-driven seismology project. Initially for the requirements of a Year 1 Research Module. 

Uses the [EQTransformer model created by S. Mousavi](https://github.com/smousavi05/EQTransformer)

## Selecting stations and timeframe: ```multi_station.py```

Tools for (pre)-preparing 

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

```(TA.txt)
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

## Writing HDF5 file model input: ```sac_to_hdf5.py```

Sample:

``` $ python sac_to_hdf5.py station_time/TA19_085.txt prediction_files/7jun_TA19.085 station_list.json ```

