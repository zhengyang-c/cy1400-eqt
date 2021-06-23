# always use absolute paths if possible

python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TA_all.txt -job 23jun_allTA_Jan -s 2020.001 -e 2020.031 -n_nodes 19 -pbs -make_sac_csv -no_execute

#  -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers

# -hdf5_parent /home/zchoong001/cy1400/cy1400-eqt/prediction_files/9jun_10random_150-151 sac_select /home/zchoong001/cy1400/cy1400-eqt/station_time/20jun_random10_1month.csv 