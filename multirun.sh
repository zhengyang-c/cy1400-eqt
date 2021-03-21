SAC_FOLDER=TA19_no_preproc
DEFAULT_MODEL=/home/zchoong001/cy1400/cy1400-eqt/EQTransformer/ModelsAndSampleData/EqT_model.h5
MODEL=/home/zchoong001/cy1400/cy1400-eqt/models/17mar_freezetoplayers_acehtrainingset_LR1e-6_outputs/final_model.h5

STATION_DATA=station_info.dat

#OUTPUT_FOLDER2="detections/1e4model_LR1e-3_TA19.085"
STA=TA19

#python sac_to_mseed.py $SAC_FOLDER
#python mseed_to_h5.py "mseed_${SAC_FOLDER}" $STATION_DATA $STA
monorun () {
	OUTPUT_FOLDER="detections/21mar_default/multi_${1}"
	echo python run_eqt.py "mseed_${SAC_FOLDER}_processed_hdfs" $DEFAULT_MODEL $OUTPUT_FOLDER
	#python run_eqt.py /home/zchoong001/cy1400/cy1400-eqt/training_files/aceh_noise_13mar_wholeday $DEFAULT_MODEL $OUTPUT_FOLDER

	echo python plot_eqt.py $SAC_FOLDER $STA $OUTPUT_FOLDER

	echo python header_writer.py "${OUTPUT_FOLDER}/${STA}_outputs/X_prediction_results.csv" "${OUTPUT_FOLDER}/${STA}_outputs/header.txt" $STATION_DATA

	echo ./writerino.sh "$OUTPUT_FOLDER/${STA}_outputs" "${OUTPUT_FOLDER}/${STA}_outputs/header.txt"
}

for f in {1..50} do
	echo $f
	monorun $f
done

#python run_eqt.py "mseed_${SAC_FOLDER}_processed_hdfs" $MODEL2 $OUTPUT_FOLDER2
#python plot_eqt.py $SAC_FOLDER $STA $OUTPUT_FOLDER2
#python header_writer.py "${OUTPUT_FOLDER2}/${STA}_outputs/X_prediction_results.csv" "${OUTPUT_FOLDER2}/${STA}_outputs/header.txt" $STATION_DATA

#./writerino.sh "$OUTPUT_FOLDER2/${STA}_outputs" "${OUTPUT_FOLDER2}/${STA}_outputs/header.txt"

