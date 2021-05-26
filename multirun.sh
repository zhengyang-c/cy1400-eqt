# SAC folder: the original source
# hdf5 folder: the output from sac_to_hdf5 / converted
# model / default: model: self explanatory
# station_data: a nice json that EQT simply needs to have
# output root: place to store the multiple runs 
# 
# # ARGS: first argument: no. of repeats


SAC_FOLDER=no_preproc
DEFAULT_MODEL=/home/zchoong001/cy1400/cy1400-eqt/EQTransformer/ModelsAndSampleData/EqT_model.h5
MODEL=/home/zchoong001/cy1400/cy1400-eqt/models/22mar_frozenlayers_LR1e-6_outputs/final_model.h5
HDF_FOLDER="/home/zchoong001/cy1400/cy1400-eqt/mseed_TA19_no_preproc_processed_hdfs"
STATION_DATA=station_info.dat
OUTPUT_ROOT="detections/26may_default_1month"

#OUTPUT_FOLDER2="detections/1e4model_LR1e-3_TA19.085"
STA=TA19

#python sac_to_mseed.py $SAC_FOLDER
#python mseed_to_h5.py "mseed_${SAC_FOLDER}" $STATION_DATA $STA
monorun () {
	OUTPUT_FOLDER="${OUTPUT_ROOT}/multi_${1}"
	python run_eqt.py $HDF_FOLDER $MODEL $OUTPUT_FOLDER
}

for ((f=0;f<$1;f++))
do
	echo $f
	#monorun $f
done

python merge_csv.py $STA $OUTPUT_ROOT "${OUTPUT_ROOT}_merged" "merged" -csv

python plot_eqt.py $SAC_FOLDER $STA $OUTPUT_FOLDER

python header_writer.py $STA "${OUTPUT_ROOT}_merged/merged.csv" "${OUTPUT_ROOT}_merged/header.txt" $STATION_DATA

./writerino.sh "${OUTPUT_ROOT}_merged" "${OUTPUT_ROOT}_merged/header.txt"

#./writerino.sh "$OUTPUT_FOLDER/${STA}_outputs" "${OUTPUT_FOLDER}/${STA}_outputs/header.txt"

#python run_eqt.py "mseed_${SAC_FOLDER}_processed_hdfs" $MODEL2 $OUTPUT_FOLDER2
#python plot_eqt.py $SAC_FOLDER $STA $OUTPUT_FOLDER2
#python header_writer.py "${OUTPUT_FOLDER2}/${STA}_outputs/X_prediction_results.csv" "${OUTPUT_FOLDER2}/${STA}_outputs/header.txt" $STATION_DATA



