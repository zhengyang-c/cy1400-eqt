station remapping:

ALSO REDOWNLOAD THE UPDATED STATION_INFO.DAT onto local PC + gekko
monkas it's on the EOS server



1. want to change csv metadata first, then start rewriting SAC headers

2. overwrite or make a copy? how much stuff would it affect

3. what about re-running plot_eqt and header_writer? if the station names themselves are remapped

suppose the csv file has STA_1 and is plotted with headers saying STA_1

now for some month, STA_1 is mapped to ATS_1

so i would first change the X_prediction_files, row by row (checking that it's in that month because there might be spillovers (?))

currently the folders are not organised into individual months (e.g. 3 months or so )

so i would have to dig inside the detection folder anyway

i would need to recompile the whole event table (to facilitate organisation by event)

so this means that i should first create a mapping representation for some arbitrary csv file

in principle the mapping is reversible? so I can just overwrite, so long as the mapping is known at every step


then i should remap for all the X_prediction_csv, all the merge_raw, etc. in a one by one fashion

then i should 

when is the linkage between csv and sac file created? 
the local folder is saved (pointing to the sac_picks folder)

would rather just rename all the needed files based on the detection time (as an ondemand service)

