# i hate bash

#$1 : path to sac_picks

#$2: csv file

mapfile -t sac_files < <( ls $1/sac_picks | grep .SAC | sed -n '0~3p') 

# echo ${sac_files[@]} # the array reference (@ --> the whole array)
c=1 
# c is the counter because we are in BASH

#format_date
for f in ${sac_files[@]} # f is a file name to read
do 
	echo "$1/sac_picks/$f" # the file to read from sac

	# 
	p_time=$(cat $2 | awk -F "," '{print $3}' | sed -n "${c}p")
	s_time=$(cat $2 | awk -F "," '{print $4}' | sed -n "${c}p")
	stla=$(cat $2 | awk -F "," '{print $2}' | sed -n "${c}p")
	stlo=$(cat $2 | awk -F "," '{print $1}' | sed -n "${c}p")

	echo $p_time
	echo $s_time

	printf "r $1/sac_picks/${f%.EHZ.SAC}.*.SAC\nch stla $stla\nch stlo $stlo\nch A $p_time\nch T0 $s_time\nwh\nq\n" | sac

	#printf "r *.BHE.SAC\nch cmpaz 90 cmpinc 90\nwh\nq\n" | sac
	#s_time=$(sed '1d' X_prediction_results.csv | awk -F "," '{print $16}' | sed -n "${c}p")
	#end_time=$(sed '1d' X_prediction_results.csv | awk -F "," '{print $9}' | sed -n "${c}p") # end time
	#start_time=${start_time::-1}	
	#echo $p_time
	#echo $s_time

	#format_date "$start_time"

	#echo 

	#echo $((start_time - p_time))
	

	#echo 'date --date=$(start_time) "+%S.%N"'

	#sed '1d' X_prediction_results.csv | awk -F "," '{print $12}' | sed -n "${c}p" # p wave
	#sed '1d' X_prediction_results.csv | awk -F "," '{print $16}' | sed -n "${c}p" # s wave
	

	# now, compute the time to write


	c=$((c+1))
done
# have a target folder

# list files in target folder

# for each file in target folder, open all 3 channels in SAC

# where to get the header, and what to write


# OMARKER = 0			# event origin marker
# AMARKER = 1.848		# first arrival (P) marker which is from start of day
#T0MARKER = 3.192		# t0 (S) marker # also from start of day

# so just convert the HH:MM:SS to seconds from 0

# i hate bash so much

# wish i appended like an event id / index using the csv file



# 1) p start time and s start time
# 2) (lat lon) of station, get from station_data 
# 