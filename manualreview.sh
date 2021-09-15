# put this in the same folder as the A,B,Z

echo $1

if [[ ${1^^} == "A" ]]; then
for f in $(ls A | grep png); do
	printf "sac\nqdp off\nwindow 1 x 0.05 0.95 y 0.15 0.95\nr A/${f%.png}*C\nbp p 2 n 4 c 1 45\nxlim a -10 50\nppk\nq\n" | sac

	echo "A: unambiguous, B: so-so, Z: don't know or noise"
	read qual
	#echo ${f%.png},$qual >> $2

	#if [[ ${qual^^} == "A"  ]]; then
	#	echo "Moving event ${f} to good picks"
	#	mv $1/sac_picks/${f%.png}* $1/sac_picks/A/
	if [[ ${qual^^} == "B" ]]; then
		echo "Moving event ${f} to not so good picks"
		mv A/${f%.png}* B/
	elif [[ ${qual^^} == "Z" ]]; then
		echo "Moving event ${f} to noise"
		mv A/${f%.png}* Z/
	else
		echo "no action"
	fi
done

elif [[ ${1^^} == "B"] ]]; then

	for f in $(ls B | grep png); do
		printf "sac\nqdp off\nwindow 1 x 0.05 0.95 y 0.15 0.95\nr B/${f%.png}*C\nbp p 2 n 4 c 1 45\nxlim a -10 50\nppk\nq\n" | sac

		echo "A: unambiguous, B: so-so, Z: don't know or noise"
		read qual
		#echo ${f%.png},$qual >> $2

		#if [[ ${qual^^} == "A"  ]]; then
		#	echo "Moving event ${f} to good picks"
		#	mv $1/sac_picks/${f%.png}* $1/sac_picks/A/
		if [[ ${qual^^} == "A" ]]; then
			echo "Moving event ${f} to not so good picks"
			mv B/${f%.png}* A/
		elif [[ ${qual^^} == "Z" ]]; then
			echo "Moving event ${f} to noise"
			mv B/${f%.png}* Z/
		else
			echo "no action"
		fi

	done

elif [[ ${1^^} == "Z"] ]]; then

	for f in $(ls Z | grep png); do
		printf "sac\nqdp off\nwindow 1 x 0.05 0.95 y 0.15 0.95\nr Z/${f%.png}*C\nbp p 2 n 4 c 1 45\nxlim a -10 50\nppk\nq\n" | sac

		echo "A: unambiguous, B: so-so, Z: don't know or noise"
		read qual
		#echo ${f%.png},$qual >> $2

		#if [[ ${qual^^} == "A"  ]]; then
		#	echo "Moving event ${f} to good picks"
		#	mv $1/sac_picks/${f%.png}* $1/sac_picks/A/
		if [[ ${qual^^} == "A" ]]; then
			echo "Moving event ${f} to not so good picks"
			mv Z/${f%.png}* A/
		elif [[ ${qual^^} == "B" ]]; then
			echo "Moving event ${f} to noise"
			mv Z/${f%.png}* B/
		else
			echo "no action"
		fi

	done
fi 

	#statements
	#statements



# done



