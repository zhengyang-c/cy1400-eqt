# preferably, do not use this bc you lose the metadata
# i.e. the station, year, day

# run this to go through a list of time stamps for manual picking purposes
# preferably you'd have written headers into the sac file
# $1: file with list of timestamps separated by linebreak
# as long as each row will fit inside *${}* it's ok
# $2: the folder in which the sac files are stored
# $3: the file to write the pick results to, full path to txt file

# note that it only appends to the file so uhh it doesn't delete and rewrite
: '
c=0
for f in $(cat $1)
	do
	echo $f
	printf "sac\nqdp off\nr ${2}/sac_picks/*${f}*\nbp p 2 n 4 c 1 45\nppk\nq\n" | sac
	echo "2:good, 1:idk, 0:noise, r:regional"
	read qual
	echo ${f},$qual >> $3
done
'