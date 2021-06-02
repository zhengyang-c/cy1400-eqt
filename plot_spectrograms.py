from scipy import signal
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import obspy
from obspy import read
import numpy as np
import os
import pandas as pd
from obspy import UTCDateTime
from scipy.ndimage.filters import gaussian_filter

# gather a list of detections in a folder 

manually_selected_pngs = "ta19_nopp.csv"
png_folder_source = "imported_figures/detections_TA19_no_preproc/TA19_outputs/sac_picks"
output_folder = "plots/TA19_yes_spec"
eqt_csv = "imported_figures/detections_TA19_no_preproc/TA19_outputs/X_prediction_results.csv"

pngs_to_plot = []

pick_info = pd.read_csv(eqt_csv)


print(len(pngs_to_plot))

def get_utc(x):
	# 2020-03-25 01:38:08.750000
	try:
		_us = x.split(".")[1]
		[__year, __month, __day] = x.split(" ")[0].split("-")
		[__hour, __minute, __second] = x.split(".")[0].split(" ")[1].split(":")
		
		__year, __month, __day, __hour, __minute, __second, _us = int(__year), int(__month), int(__day), int(__hour), int(__minute), int(__second), int(_us)

		return UTCDateTime(year = __year, month = __month, day = __day, hour = __hour, minute = __minute, second = __second, microsecond =_us)
	except:
		try: # this is pretty bad
			return UTCDateTime(x) 
		except: # checks for NaN
			return None

def plot_spec_png(output_folder):
	# this bit is all manually because i manually put 2 to select pngs
	with open(manually_selected_pngs, "r") as f:
		for c, line in enumerate(f):  # well first line should be blank without header
			[_a, _b] = line.strip().split(",")
			if _b == "2":
				pngs_to_plot.append(_a)

	list_of_start_picks = [get_utc(x) for x in list(pick_info['event_start_time'])]
	list_of_end_picks =   [get_utc(x) for x in list(pick_info['event_end_time'])]
	list_of_p_arrival = list(pick_info['p_arrival_time'])
	list_of_s_arrival = list(pick_info['s_arrival_time'])

	indices_actual_picks = []
	for c, pick in enumerate(pngs_to_plot):
		[_sta, _year, _day, _time, _] = pick.split(".")
		_event_time = UTCDateTime("{},{},{}".format(_year,_day,_time))
		for d, _pick in enumerate(list_of_start_picks):
			if -2 <= (_pick - _event_time) <= 2:							
				try: # verify that p and s picks are valid (probably because i'm not alive long enough to pick all the times)
					assert UTCDateTime(list_of_p_arrival[d])
					assert UTCDateTime(list_of_s_arrival[d])
					indices_actual_picks.append((c,d)) 
					#index of the original handpicked list, mapped to the index of the eqt list
				except:	
					continue

	max_p_triple = []
	max_s_triple = []

	for png_i, csv_i in indices_actual_picks:
		png_name = pngs_to_plot[png_i]
		print(png_name)

		[_sta, _year, _day, __time, _] = png_name.split(".")

		build_file_name = os.path.join(png_folder_source, "{}.{}.{}.*.{}.SAC".format(_sta,_year,_day,__time))

		if not os.path.exists(output_folder):
			os.makedirs(output_folder)

		st = read(build_file_name)

		# E, N, Z read in this order (alphabetical)

		# freqs_p, freqs_s = [], []
		# ts_p, ts_s = [], []
		# specs_p, specs_s = [], []
		# # load the csv file
		# #print(pngs_to_plot[png_i])
		# #print(list_of_start_picks[csv_i])
		# #print(list_of_p_arrival[csv_i])
		# #print(list_of_s_arrival[csv_i])
		# #print(list_of_end_picks)

		# # uhhh trim the file to between these times

		# st_p = st.copy().trim(UTCDateTime(list_of_p_arrival[csv_i]) - 1, UTCDateTime(list_of_s_arrival[csv_i]) + 1)
		# st_s = st.copy().trim(UTCDateTime(list_of_s_arrival[csv_i]) - 1, list_of_end_picks[csv_i] + 1)

		# #print(st_p)
		# #print(st_s)

		# # get the data, run it through the spectrogram

		# # use the two bits inbetween and find the average 

		# _p_t = [] # keep the maximum freq for p wave
		# _s_t = [] # keep the maximum freq for s wave

		# for i in range(3):
		# 	# p to s

		# 	_f, _t, _Sxx = signal.spectrogram(st_p[i].data, fs = 250)
		# 	_Sxx = gaussian_filter(_Sxx, sigma = 5)
		# 	max_p = np.unravel_index(_Sxx.argmax(), _Sxx.shape)
		# 	#print(st[i].stats.channel)
		# 	#print(_Sxx.shape)
		# 	#print(max_p)
		# 	_p_t.append(_f[max_p[0]])
		# 	#freqs_p.append(_f)
		# 	#ts_p.append(_t)
		# 	#specs_p.append(_Sxx)

		# 	# s to coda

		# 	_f, _t, _Sxx = signal.spectrogram(st_s[i].data, fs = 250)
		# 	_Sxx = gaussian_filter(_Sxx, sigma = 5)
		# 	max_s = np.unravel_index(_Sxx.argmax(), _Sxx.shape)
		# 	_s_t.append(_f[max_s[0]])
		# 	#print(_Sxx.shape)
		# 	#print(max_s)
		# 	#print(st[i].stats.channel)
		# 	#freqs_s.append(_f)
		# 	#ts_s.append(_t)
		# 	#specs_s.append(_Sxx)
		# if max(_p_t) > 40:
		# 	print(png_name, max(_p_t))
		# max_p_triple.append(_p_t)
		# max_s_triple.append(_s_t)


		# find the strongest frequencies in each spectogram

		# part that plots below:

		fig, axs = plt.subplots(6, 1, figsize = (8,6), sharex=True,constrained_layout=True)
		fig.suptitle(png_name)
		#fig.tight_layout()

		_x0 = 25
		_x1 = 40

		# for c,i in enumerate([0,2,4]):
		# 	im = axs[i].pcolormesh(ts[c], freqs[c], (specs[c]), shading = 'gouraud', cmap = 'viridis')
		# 	axs[i].set_ylim(1,62.5)
		# 	axs[i].set_xlim(_x0, _x1)

		for c, i in enumerate([0,2,4]):
			st[c].spectrogram(log=False, wlen=0.1,per_lap=0.8, axes=axs[i], clip=[0, 5e-6])
			axs[i].set_ylim(0,125)

		mappable = axs[4].images[0]
		plt.colorbar(mappable=mappable, ax=axs[4])


		_time = np.arange(len(st[0].data)) * 0.004
		for c, i in enumerate([1,3,5]):
			axs[i].plot(_time, st[c].data, color = 'black', linewidth = 0.5)
			axs[i].set_title(st[c].stats.channel)
			axs[i].set_xlim(_x0, _x1)

		plt.savefig(os.path.join(output_folder, "{}.{}.{}.{}.spec.png".format(_sta, _year, _day, __time)),dpi=300)
		plt.clf()

	#max_p_triple = np.array(max_p_triple)
	#max_s_triple = np.array(max_s_triple)

	# plt.title("P wave frequencies from Z channel")
	# plt.xlabel("Max Frequency (Hz)")
	# plt.ylabel("Observations")
	# plt.hist(max_p_triple[:, 2], bins = 20)
	# plt.xlim(0,125	)
	# plt.savefig("plots/ta19_ehz_p_max_freq.png", dpi = 300)
	# plt.clf()

	# plt.hist(max_s_triple[:, 0])
	# plt.title("S wave frequencies from E channel")
	# plt.ylabel("Observations")
	# plt.xlabel("Max Frequency (Hz)")
	# plt.savefig("plots/ta19_ehe_s_max_freq.png", dpi = 300)
	# plt.clf()

	# plt.hist(max_s_triple[:, 1])
	# plt.title("S wave frequencies from N channel")
	# plt.ylabel("Observations")
	# plt.xlabel("Max Frequency (Hz)")
	# plt.savefig("plots/ta19_ehn_s_max_freq.png", dpi = 300)
	# plt.clf()

plot_spec_png(output_folder)

for i in pngs_to_plot:
	pass
	#plot_spec_png(i, output_folder)


"""
from karen

import obspy
import matplotlib.pyplot as plt
st = obspy.read("TA01.2020.085.EH*.180535.SAC") 
dt = obspy.UTCDateTime("2020-03-25T18:05:35")
stt=st.copy()
stt=stt.trim(dt, dt + 10)
fig, axs = plt.subplots(6,1, sharex=True,constrained_layout=True) 
fig.suptitle('TA01 ' + str(dt))
axs[1].plot(stt[0].times(reftime=dt), stt[0].data, "k-")
axs[3].plot(stt[1].times(reftime=dt), stt[1].data, "k-")
axs[5].plot(stt[1].times(reftime=dt), stt[2].data, "k-")
stt[0].spectrogram(log=False, title='TA01 ' + str(dt),wlen=0.1,per_lap=0.8, axes=axs[0], clip=[0, 5e-6],show=False)
stt[1].spectrogram(log=False, title='TA01 ' + str(dt),wlen=0.1,per_lap=0.8, axes=axs[2], clip=[0, 5e-6])
stt[2].spectrogram(log=False, title='TA01 ' + str(dt),wlen=0.1,per_lap=0.8, axes=axs[4], clip=[0, 5e-6])
mappable = axs[4].images[0]
plt.colorbar(mappable=mappable, ax=axs[4])
axs[4].set_title('EHZ')
axs[2].set_title('EHN')
axs[0].set_title('EHE')
plt.xlabel("Time (s)")
plt.show()


"""

