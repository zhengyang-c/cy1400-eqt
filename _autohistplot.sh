#plot file is the intermediate plot file

csv_file=$1
#csv_file="imported_figures/detections/1e4model_LR1e-3_TA19.085/TA19_outputs/X_prediction_results.csv"
#csv_file="imported_figures/detections/retrain_with_noise/TA19_outputs/X_prediction_results.csv"
#csv_file="imported_figures/detections/single_day_test/TA19_outputs/X_prediction_results.csv"


#plot_file=plot_data/5mar_default_model_ta19.txt
#plot_file=plot_data/28feb_noise_model_ta19.txt
plot_file=plot_data/${3}.txt
#plot_file=plot_data/16mar_1e4WF_1e-3LR_model.txt
# plot_file --> actual data to plot


# txt file --> manual picks to feed into python
#txt_file=manual/5mar_default_model_manual.txt
#txt_file=manual/14mar_1e4model_TA19.085.txt
#txt_file=manual/28feb_retrained_700_300_1e-3_manual.txt
manual_file=$2

#filename=plots/5mar_default_model.pdf
#filename=plots/14mar_LR1e-3.pdf
#filename=plots/16mar_1e4WF_1e-3LR_detection_p.pdf
filename=plots/${3}.pdf
#filename=plots/28feb_withnoise_300-700_LR1e-3.pdf
#title= space expansion is a no no, fill in below because i'm lazy to solve

python3 plot_hist.py $csv_file $manual_file $plot_file -t d
gnuplot -e "filename='"$filename"';plot_file='"$plot_file"'" hist_plotter.gn
#"plots/28feb_p_withnoise.pdf"
