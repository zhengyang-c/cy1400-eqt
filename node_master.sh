# always use absolute paths if possible


#python multi_station.py --get /tgo/SEISMIC_DATA_TECTONICS/RAW/ACEH/MSEED/Deployed-2020-10-MSEED -o station/sac_oct20.csv

#python multi_station.py -enc -i station/A01A02.txt -job oct20_testram32 -pbs -run_eqt -write_hdf5 -js station/json/oct.json -n_multi 2 -pbs
#python multi_station.py -enc -i station/A01A02.txt -job oct20_testram2 -pbs -run_eqt -write_hdf5 -js station/json/oct.json -n_multi 2 -msc station/sac_oct20.csv
#python multi_station.py -enc -i station/A01A02.txt -job oct20_gputest -pbs -run_eqt -write_hdf5 -js station/json/oct.json -n_multi 2 -msc station/sac_oct20.csv -gpu


python multi_station.py -enc -i station/oct_split_again_aa -job oct20_group_a -run_eqt -write_hdf5 -js station/json/oct.json -nx -pbs
#python multi_station.py -enc -i station/oct_split_again_ab -job oct20_group_b -write_hdf5 -js station/json/oct.json -nx -pbs
#python multi_station.py -enc -i station/oct_split_again_ac -job oct20_group_c -write_hdf5 -js station/json/oct.json -nx -pbs
#python multi_station.py -enc -i station/oct_split_again_ad -job oct20_group_d -write_hdf5 -js station/json/oct.json -nx -pbs
#python multi_station.py -enc -i station/oct_split_again_ae -job oct20_group_e -write_hdf5 -js station/json/oct.json -nx -pbs
