from obspy import read
from obspy.signal.trigger import *
import numpy as np
import os
import math
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
from helpme import *
import sys

sys.path.append("PhasePApy-master")
from phasepapy.phasepicker import *

save_folder = "one_plot"
file_name = "EOS_SAC/TA01/AC.TA01.00.EHZ.D.2020.085.000000.SAC.preproc"

matplotlib.use('TkAgg')

#relative to the start of the file
start_time = 0
end_time = 600

st = read(file_name)

trace = st[0]

start_UTC_time = trace.stats.starttime

print(trace.stats) # there could be multiple traces in the data stream, so [0] index is needed 

df = trace.stats.sampling_rate

#trim to get more manageable dataset
trace.trim(trace.stats.starttime + start_time, trace.stats.starttime + end_time)

# write to miniseed 

#st.write('mseed_test/TA01/AC__TA01__EHZ.mseed', format = 'MSEED')

#print(len(trace.data))

'''pick_string = {phasepa_aic, phasepa_kt, phasepa_fb, obspy}
mostly for the PhasePA pickers'''


"""
picker_kt = ktpicker.KTPicker(t_win = 1, t_ma = 10, nsigma = 6, t_up = 0.78, nr_len = 2, 
nr_coeff = 2, pol_len = 10, pol_coeff = 10, uncert_coeff = 3)
scnl, kt_picks, polarity, snr, uncert = picker_kt.picks(trace)
log(scnl, kt_picks, polarity, snr, uncert, "phasepa_kt", file_name)


picker_fb = fbpicker.FBPicker(t_long = 5, freqmin = 1, mode = 'rms', t_ma = 20, nsigma = 8, t_up = 0.4, nr_len = 2, nr_coeff = 2, pol_len = 10, pol_coeff = 10, uncert_coeff = 3)
scnl, fb_picks, polarity, snr, uncert = picker_fb.picks(trace) 
log(scnl, fb_picks, polarity, snr, uncert, "phasepa_fb", file_name)

picker_aic = aicdpicker.AICDPicker(t_ma = 3, nsigma = 8, t_up = 0.78, nr_len = 2, nr_coeff = 2, pol_len = 10, pol_coeff = 10, uncert_coeff = 3)
scnl, aic_picks, polarity, snr, uncert = picker_aic.picks(trace)
log(scnl, aic_picks, polarity, snr, uncert, "phasepa_aic", file_name)
"""


# get the cf (e.g. classic_sta_lta), the first argument is a trace object
cf_classic_2 = classic_sta_lta(trace, int(1 * df), int(10 * df))**2 # argument: length in samples

# trigger from cf
cf_picks = np.array(trigger_onset(cf_classic_2, 25, 15))

#print(len(cf_picks))

# in sample index

before_trigger = int(10 * df)
after_trigger = int(30 * df)

time = np.arange(0, len(trace.data)) * 0.008 # 125 HZ sampling dum dum



##########
# PLOTTING
##########

#plot_phasepa_picks(fb_picks, "phasepa_fb")
#plot_phasepa_picks(kt_picks, "phasepa_kt")
#plot_phasepa_picks(aic_picks, "phasepa_aic")

#plot_phasepa_picks_together("fb_kt_aic", fb_picks, kt_picks, aic_picks)

#plot_obspy_picks_together(cf_picks, "classic2")
plot_obspy_picks(file_name, time, trace.data, (before_trigger, after_trigger), start_UTC_time, cf_picks, "classic2")

#cf_recursive = recursive_sta_lta(trace, int(1 * df), int(10 * df)) # argument: length in samples

#cf_carl = carl_sta_trig(trace,int(1 * df), int(10 * df),  1, 1) # ratio and quiet. as each number gets smaller, the CF gets more sensitive. 1: trial function
#cf_z = z_detect(trace, int(1 * df))



#plot_2()


#plot_trigger(trace.data[:, cft, 1.5, 0.5) # 1st hour

# \delta t = 0.0125 s


# testing different timing windows  
# --------------------------------
# all_cfs = []
#all_cfs.extend([trace.data, cf_classic**2, classic_sta_lta(trace, int(0.5 * df), int(5 * df))**2, classic_sta_lta(trace, int(2 * df), int(20 * df))**2, classic_sta_lta(trace, int(2 * df), int(10 * df))**2, classic_sta_lta(trace, int(0.1 * df), int(5 * df))**2])

#print(len(all_cfs))

#cf_recursive = recursive_sta_lta(trace, int(1 * df), int(10 * df))
#cf_recursive_2, cf_recursive_3, cf_recursive_4 = cf_recursive**2, cf_recursive**3, cf_recursive**4
