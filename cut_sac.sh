# i hate bash

#$1: filepath to sac source (in eosdata) but this is like hidden inside uhhh 
# 

#$2: info.txt


# echo ${sac_files[@]} # the array reference (@ --> the whole array)


#format_date
for (( c=1; c<=$1; c++ )) # f is a file name to read
do 

	fp=$(cat $2 | awk -F "," '{print $1}' | sed -n "${c}p")
	start_time=$(cat $2 | awk -F "," '{print $2}' | sed -n "${c}p")
	end_time=$(cat $2 | awk -F "," '{print $3}' | sed -n "${c}p")
	f1=$(cat $2 | awk -F "," '{print $4}' | sed -n "${c}p")
	f2=$(cat $2 | awk -F "," '{print $5}' | sed -n "${c}p")
	f3=$(cat $2 | awk -F "," '{print $6}' | sed -n "${c}p")
	sac_id=$(cat $2 | awk -F "," '{print $7}' | sed -n "${c}p")
	png_id="test"

	printf "cut $start_time $end_time\nr $fp/*$sac_id*SAC\nwrite SAC $f1 $f2 $f3\nq\n"
	printf "sgf DIRECTORY /home/zchoong001/cy1400/cy1400-eqt/temp OVERWRITE ON\nqdp off\nr $f1 $f2 $f3\nbp p 2 n 4 c 1 45\nq\n"
	convert /home/zchoong001/cy1400/cy1400-eqt/f001.sgf $png_id

	c=$((c+1))
done
