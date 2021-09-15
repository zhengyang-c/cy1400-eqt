# the manual pick file i make is very messy
# hence, i just want to generate a new text file, by treating the files within the folders (A/B/Z)
# as a source of truth, thus making a 100% correct pick file without having to reparse or edit the manual picking file


INPUT_FOLDER=$1 # this folder contains all the A/B/Z without hte / at the back
OUTFILE=$2 # this folder is for the fixed manual picks (text file!!)

for f in $(ls $1/A | grep png); do
	echo "${f%.png},A" >> $2
done
for f in $(ls $1/B | grep png); do
 	echo "${f%.png},B" >> $2
done
for f in $(ls $1/Z | grep png); do
	echo "${f%.png},Z" >> $2
done
