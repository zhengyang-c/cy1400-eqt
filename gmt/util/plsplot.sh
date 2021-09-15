#!/bin/bash

##
## 
## DEPTH PROFILE PLOTTING
##
##
##
# what the file names mean:
#
# jul5: before inclusion of partial day events
# jul7: after inclusion of partial day events:
# the problem: 

AFTER_DD_JUL5_1_IN=~/cy1400-eqt/real_postprocessing/5jul_assoc/hypoDD.reloc
AFTER_DD_JUL5_1_OUT=aceh_5jul_afterDD_dp

AFTER_DD_JUL7_1_IN=~/cy1400-eqt/real_postprocessing/7jul_assoc/hypoDD_run_1/aug5_jul5hypoDD_1.reloc
AFTER_DD_JUL7_1_OUT=aceh_7jul_afterDD_dp

#./depth_profile.sh ~/cy1400-eqt/imported_figures/7jul_gsonly_13sep_all.csv 7jul_afterREAL_gs_only_13sep

./depth_profile.sh $AFTER_DD_JUL7_1_IN $AFTER_DD_JUL7_1_OUT

#./afterDD.sh $AFTER_DD_JUL5_1_IN $AFTER_DD_JUL5_1_OUT
#./afterDD.sh $AFTER_DD_JUL7_1_IN $AFTER_DD_JUL7_1_OUT

# AFTER_DD_JUL7_2_IN=~/cy1400-eqt/real_postprocessing/7jul_assoc/hypoDD_run_2/hypoDD_aug12.reloc
# AFTER_DD_JUL7_2_OUT=aceh_7jul_afterDD_2_dp

#./afterDD.sh $AFTER_DD_JUL7_2_IN $AFTER_DD_JUL7_2_OUT



##
## the script's the same between BEFORE and AFTER DD is applied
##
BEFORE_DD_JUL5_1_IN=~/cy1400-eqt/real_postprocessing/5jul_assoc/hypoDD.loc
BEFORE_DD_JUL5_1_OUT=aceh_5jul_beforeDD_dp

BEFORE_DD_JUL7_1_IN=~/cy1400-eqt/real_postprocessing/7jul_assoc/hypoDD.loc
BEFORE_DD_JUL7_1_OUT=aceh_7jul_beforeDD_dp

# ./afterDD.sh $BEFORE_DD_JUL5_1_IN $BEFORE_DD_JUL5_1_OUT
# ./afterDD.sh $BEFORE_DD_JUL7_1_IN $BEFORE_DD_JUL7_1_OUT

# ---------------------------------------------------------------
##
## 
## AFTER REAL PLOTTING: what does the REAL output look like
##
AFTER_REAL_JUL5_1_IN=~/cy1400-eqt/real_postprocessing/5jul_assoc/real_output_cat.csv
AFTER_REAL_JUL5_1_OUT=aceh_5jul_afterREAL
AFTER_REAL_JUL7_1_IN=~/cy1400-eqt/real_postprocessing/7jul_assoc/hypoDD_run_1/real_output_cat.csv
AFTER_REAL_JUL7_1_OUT=aceh_7jul_afterREAL

#./afterREAL.sh $AFTER_REAL_JUL5_1_IN $AFTER_REAL_JUL5_1_OUT
#./afterREAL.sh $AFTER_REAL_JUL7_1_IN $AFTER_REAL_JUL7_1_OUT
