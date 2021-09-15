# $1: folder to sac_picks without the / e.g. detections/yes/TA19_outputs
# $2: file to append to (the manual pick file) e.g. manual/yes.txt
# $3: trace name e.g. TA19.2020.085.000000

monopick () {
	echo ${1}/sac_picks/${3}
	printf "sac\nqdp off\nr ${1}/sac_picks/${f%.png}*C\nbp p 2 n 4 c 1 45\nppk\nq\n" | sac
	echo "2:good, 1:idk, 0:noise, r:regional"
	read qual
	echo $3,$qual >> $2
}

# for f in some compiled list, 

