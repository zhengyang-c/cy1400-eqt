# $1: input folder

# assuming it's from: TA19.2020.085.EHE.013808.SAC --> TA19.2020.085.013808.EHE.SAC

mapfile -t sac_files < <( ls $1/sac_picks | grep .SAC | sed -n '0~3p') 

for f in ${sac_files[@]} # f is a file name to read
do 
	echo "$1/sac_picks/$f" # the file to read from sac
	awk -F "." "{print $1.$2.$3.$5.$4.SAC}" $f
done