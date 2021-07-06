# always use absolute paths if possible

#python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TA_all.txt -job 23jun_allTA_Mar -s 2020.063 -e 2020.093 -pbs  -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers


# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TA_all.txt -job 23jun_allTA_Oct-Dec -s 2020.278 -e 2020.366 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/A_all.txt -job 24jun_allA_Jan-Mar -s 2020.001 -e 2020.091 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/A_all.txt -job 24jun_allA_Apr-May -s 2020.092 -e 2020.183 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/A_all.txt -job 24jun_allA_Jul-Sep -s 2020.184 -e 2020.275 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/A_all.txt -job 24jun_allA_Oct-Dec -s 2020.276 -e 2020.366 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers

#python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/A_all.txt -job 05jul_test_A_all_2020 -s 2020.001 -e 2020.366 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers -sac_select /home/zchoong001/cy1400/cy1400-eqt/missing_sac_5jul.csv

#python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/A01A02.txt -job 06jul_test_hdf5 -s 2020.001 -e 2020.366 -pbs -write_hdf5 -sac_select /home/zchoong001/cy1400/cy1400-eqt/missing_sac_5jul.csv


python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/BB-CB-MA.txt -job 06jul_leftover_BBCBMA_2020 -s 2020.001 -e 2020.366 -pbs -write_hdf5 -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers -sac_select /home/zchoong001/cy1400/cy1400-eqt/missing_sac_5jul.csv

python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/GE-GM.txt -job 06jul_leftover_GE-GM_2020 -s 2020.001 -e 2020.366 -pbs -write_hdf5 -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers -sac_select /home/zchoong001/cy1400/cy1400-eqt/missing_sac_5jul.csv

python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TG-TS.txt -job 06jul_leftover_TG-TS_2020 -s 2020.001 -e 2020.366 -pbs -write_hdf5 -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers -sac_select /home/zchoong001/cy1400/cy1400-eqt/missing_sac_5jul.csv

python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TA_all.txt -job 06jul_leftover_TA_all_2020 -s 2020.001 -e 2020.366 -pbs -write_hdf5 -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers -sac_select /home/zchoong001/cy1400/cy1400-eqt/missing_sac_5jul.csv
# 
# 
# 
# 
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/BB-CB-MA.txt -job 24jun_BB-CB-MA_Jan-Mar -s 2020.001 -e 2020.091 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/BB-CB-MA.txt -job 24jun_BB-CB-MA_Apr-May -s 2020.092 -e 2020.183 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/BB-CB-MA.txt -job 24jun_BB-CB-MA_Jul-Sep -s 2020.184 -e 2020.275 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/BB-CB-MA.txt -job 24jun_BB-CB-MA_Oct-Dec -s 2020.276 -e 2020.366 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/30jun_rerun.txt -job 30jun_rerun_Apr1 -s 2020.092 -e 2020.107 -pbs  -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/30jun_rerun.txt -job 30jun_rerun_Apr2 -s 2020.108 -e 2020.123 -pbs  -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/30jun_rerun.txt -job 30jun_rerun_May1 -s 2020.124 -e 2020.139 -pbs  -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/30jun_rerun.txt -job 30jun_rerun_May2 -s 2020.140 -e 2020.155 -pbs  -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/30jun_rerun.txt -job 30jun_rerun_Jun1 -s 2020.156 -e 2020.171 -pbs  -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/30jun_rerun.txt -job 30jun_rerun_Jun2 -s 2020.172 -e 2020.183 -pbs  -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 


# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/30jun_rerun_GE0203.txt -job 30jun_rerun_GE0203_Jan -s 2020.001 -e 2020.031 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/30jun_rerun_GE0203.txt -job 30jun_rerun_GE0203_Feb -s 2020.032 -e 2020.060 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/30jun_rerun_GE0203.txt -job 30jun_rerun_GE0203_Mar -s 2020.061 -e 2020.091 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers

#python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/GE-GM.txt -job 24jun_GE-GM_Jan-Mar -s 2020.001 -e 2020.091 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 
#python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/GE-GM.txt -job 24jun_GE-GM_Apr-May -s 2020.092 -e 2020.183 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/GE-GM.txt -job 24jun_GE-GM_Jul-Sep -s 2020.184 -e 2020.275 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TG-TS.txt -job 24jun_TG-TS_Jan-Mar -s 2020.001 -e 2020.091 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
#python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TG-TS.txt -job 24jun_TG-TS_Apr-May -s 2020.092 -e 2020.183 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers 
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TG-TS.txt -job 24jun_TG-TS_Jul-Sep -s 2020.184 -e 2020.275 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers

# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TA_all.txt -job 23jun_allTA_ -s 2020.063 -e 2020.093 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TA_all.txt -job 23jun_allTA_Apr -s 2020.094 -e 2020.124 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TA_all.txt -job 23jun_allTA_May -s 2020.125 -e 2020.155 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers
# python multi_station.py -encode -i /home/zchoong001/cy1400/cy1400-eqt/station/TA_all.txt -job 23jun_allTA_Jun -s 2020.156 -e 2020.186 -pbs -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers





#  -write_hdf5 -run_eqt -merge_csv -recompute_snr -filter_csv -plot_eqt -write_headers

# -hdf5_parent /home/zchoong001/cy1400/cy1400-eqt/prediction_files/9jun_10random_150-151 sac_select /home/zchoong001/cy1400/cy1400-eqt/station_time/20jun_random10_1month.csv 