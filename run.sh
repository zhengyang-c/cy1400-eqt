SAC_FOLDER=single_day_test
MODEL=/home/zchoong001/cy1400/cy1400-eqt/EQTransformer/ModelsAndSampleData/EqT_model.h5
STATION_DATA=station_info.dat
OUTPUT_FOLDER="detections/single_day_test"
STA=TA19

#python sac_to_mseed.py $SAC_FOLDER
#python mseed_to_h5.py "mseed_${SAC_FOLDER}" $STATION_DATA $STA
python run_eqt.py "mseed_${SAC_FOLDER}_processed_hdfs" $MODEL $OUTPUT_FOLDER
python plot_eqt.py $SAC_FOLDER $OUTPUT_FOLDER
python header_writer.py "${OUTPUT_FOLDER}/${STA}_outputs/X_prediction_results.csv" "${OUTPUT_FOLDER}/${STA}_outputs/header.txt" $STATION_DATA

./writerino.sh "$OUTPUT_FOLDER/${STA}_outputs" "${OUTPUT_FOLDER}/${STA}_outputs/X_prediction_results.csv"