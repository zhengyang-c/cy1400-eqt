#!/bin/bash

python search_grid.py -station_info new_station_info.dat -phase_json gridsearch/jul7_phases_arrivaltimes.json -tt_path gridsearch/model_dlange2_451km-60km.npy -output_folder gridsearch/output_7jul -event_id 000023 -dz 1 -zrange 41 -tt_dx 1 -tt_dz 1 -m londep 


#--time_remapping arrivaltime_remapping/main.csv
# -excl gridsearch/test_exclude.txt -r -ef imported_figures/event_archive 

#python search_grid.py station_info.dat real_postprocessing/5jul_assoc/5jul_aceh_phase.json real_postprocessing/5jul_assoc/hypoDD.reloc hypoDD_loc gridsearch/tt_t.npy gridsearch -event_id 55 -zrange 41 -dx 0.01 -dz 1 -zrange 40 -tt_dx 0.01 -tt_dz 1 -load_only -plot_mpl -show_mpl -write_xyz

# on gekko
#python search_grid.py -station_info station_info.dat -phase_json real_postprocessing/7jul_phase.json -coord_file real_postprocessing/aceh_7jul_1/aug5_hypoDD_1.reloc -coord_format hypoDD_loc -tt_path gridsearch/tt_t.npy -output_folder gridsearch -event_id 55 -zrange 40 -tt_dx 0.01 -tt_dz 1 -plot_mpl -write_xyz


# python search_grid.py -station_info station_info.dat -phase_json real_postprocessing/7jul_phase.json -coord_file real_postprocessing/aceh_7jul_1/aug5_hypoDD_1.reloc -coord_format hypoDD_loc -tt_path gridsearch/tt_t.npy -output_folder gridsearch -event_csv real_postprocessing/aug5_hypoDD_1.csv -zrange 40 -tt_dx 0.01 -tt_dz 1 -plot_mpl -write_xyz -dx 0.01 -dz 1 -save_numpy

#python search_grid.py -station_info old_station_info.dat -phase_json real_postprocessing/5jul/5jul_phase.json -coord_file real_postprocessing/5jul/aceh_phase.dat -coord_format real_hypophase -tt_path gridsearch/tt_t.npy -output_folder gridsearch -event_csv real_postprocessing/5jul/real_output_cat.csv -eqt_csv real_postprocessing/7jul_compiled_customfilter.csv -zrange 40 -tt_dx 0.01 -tt_dz 1 -plot_mpl -write_xyz -n_dx 50 -dz 1 -save_numpy
