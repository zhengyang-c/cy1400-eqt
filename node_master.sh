# always use absolute paths if possible

python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/random10.txt -o /home/zchoong001/cy1400/cy1400-eqt/node_encode/10jun_random10.csv -job 10jun_random10_150-180 -s 2020_150 -e 2020_180 -n_nodes 10 -pbs -sac_select /home/zchoong001/cy1400/cy1400-eqt/station_time/20jun_random10_1month.csv -make_sac_csv

# -hdf5_parent /home/zchoong001/cy1400/cy1400-eqt/prediction_files/9jun_10random_150-151