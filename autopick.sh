# this is for going through sac cuts made using my
# plotting script.
# this will allow me to do manual review of the sac files
# similar to autopick_nopng.sh

# it does a bp filter from 1 to 45 Hz so what you see will be similar to 

# note that it only appends to the file so uhh it doesn't delete and rewrite

#  $1 --> path to sac folder with no '/' at the back
#  $2 --> full path to the .txt file in which to write the manual picks


move_or_not=true
while getopts :hm opt; do
    case $opt in 
        h) echo "Set -n to not move files into folders" ; exit ;;
        n) move_or_not=false ;;
        :) echo "Missing argument for option -$OPTARG"; exit 1;;
       \?) echo "Unknown option -$OPTARG"; exit 1;;
    esac
done

# here's the key part: remove the parsed options from the positional params
shift $(( OPTIND - 1 ))

if $move_or_not; then
	echo "Creating subdirectories..."
	mkdir -p $1/sac_picks/A
	mkdir -p $1/sac_picks/B
	mkdir -p $1/sac_picks/Z # d is for don't know, or noise
fi


# with mv, that will track the progress so if i interrupt halfway,
# a future rerun will only run on the files remaining in the root folder

for f in $(ls $1/sac_picks | grep .png)
	do
	echo ${1}/sac_picks/${f%.png}
	printf "sac\nqdp off\nwindow 1 x 0.05 0.95 y 0.15 0.95\nr ${1}/sac_picks/${f%.png}*C\nbp p 2 n 4 c 1 45\nxlim B 20 80\nppk\nq\n" | sac
	# window 1 x 0.05 0.95 y 0.15 0.95\n
	#echo "2:good, 1:idk, 0:noise, r:regional"
	echo "A: unambiguous, B: so-so, Z: don't know or noise"
	read qual
	echo ${f%.png},$qual >> $2

	if $move_or_not; then
		if [[ ${qual^^} == "A"  ]]; then
			echo "Moving event ${f} to good picks"
			mv $1/sac_picks/${f%.png}* $1/sac_picks/A/
		elif [[ ${qual^^} == "B" ]]; then
			echo "Moving event ${f} to not so good picks"
			mv $1/sac_picks/${f%.png}* $1/sac_picks/B/
		elif [[ ${qual^^} == "Z" ]]; then
			echo "Moving event ${f} to noise"
			mv $1/sac_picks/${f%.png}* $1/sac_picks/Z/
		else
			echo "input was invalid, no action"
		fi
	fi
done