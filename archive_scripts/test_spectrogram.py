from scipy.fft import fft, fftfreq
import matplotlib
import matplotlib.pyplot as plt
import obspy
from obspy import read
import numpy as np
import os
import glob
from obspy.signal import PPSD
import pandas as pd


#input_folder = "imported_figures/detections_TA19_no_preproc/TA19_outputs/sac_picks/"

	#print(f)

"""st = read("imported_figures/21mar_default_merge/sac_picks/A/TA19.2020.090.203119.*.SAC")

T = st[0].stats.delta

y_fft = fft(st[0].data)

N = len(st[0].data)
xf = fftfreq(N,T)[:N//2]

with open("plot_data/sample_spectrogram_090_203119.EHZ.txt", "w") as f:
	for c in range(len(xf[1:N//2])):
		f.write("{}\t{}\n".format(xf[1:N//2][c], (2.0/N * np.abs(y_fft[1:N//2][c]))))
"""

def stack_fft():

	# zero term is dropped cos it doesn't do anything

	sac_source = "imported_figures/21mar_default_merge/sac_picks/"
	st = read(sac_source + "A/*C")
	stream2 = read(sac_source + "B/*C")

	st = st + stream2

	E_fft = []
	N_fft = []
	Z_fft = []

	for trace in st:
		trace.detrend('linear')

		T = trace.stats.delta
		N = trace.stats.npts

		#print(trace.stats)

		trace.filter("bandpass", freqmin = 1, freqmax = 45 )  

		_y_fft = fft(trace.data)
		xf = fftfreq(N,T)[1:N//2] # tbh just need to calculate once since it is the same
		_yf = (2.0 / N) * np.abs(_y_fft[1:N//2])

		if trace.stats.channel == "EHE":
			E_fft.append(_yf)
		elif trace.stats.channel == "EHN":
			N_fft.append(_yf)
		elif trace.stats.channel == "EHZ":
			Z_fft.append(_yf)

	
	E_fft = np.array(E_fft)
	N_fft = np.array(N_fft)
	Z_fft = np.array(Z_fft)

	# stack the ffts

	E_fft = np.sum(E_fft, axis = 0)
	N_fft = np.sum(N_fft, axis = 0)
	Z_fft = np.sum(Z_fft, axis = 0)

	# plt.plot(xf, E_fft, label = 'E')
	# plt.plot(xf, N_fft, label = 'N')
	# plt.plot(xf, Z_fft, label = 'Z')
	# plt.ylabel("Amplitude")
	# plt.xlabel("Frequency")
	# plt.xlim(0, 45)
	# plt.legend()
	# plt.grid()

	# plt.show()

	df = pd.DataFrame(np.column_stack((xf, E_fft, N_fft, Z_fft)), columns = ["freq", "E", "N", "Z"])


	out_file = "plot_data/8apr_default1month_stacked_fft.csv"
	df.to_csv(out_file, index = False)

	



		

	# for each trace, perform FFT
	# group the traces into E,H, Z.
	# 
	# then stack and plot the FFT so some file
	# 
	


stack_fft()

#plt.plot(xf[1:N//2], 2.0/N * np.abs(y_fft[1:N//2]), '-b')


"""
fig, axs = plt.subplots(4,3, figsize = (8,8))

# 12 slices

# start: t = 28

for _c, i in enumerate(_t):
	if i > 28:
		break

#fig.


chas = ["EHE", "EHN", "EHZ"]
colors = ["b", "g", "r"]

for i in range(1, 13):
	#_row, _col = i // 3, i % 3

	for j in range(3):
		plt.subplot(7,3,i)
		plt.plot(freqs[0], specs[j][:, i + _c], label = chas[j], color = colors[j])
		plt.xlim(0, 30)
		plt.title("t = {}".format(_t[i + _c]))

plt.legend()

_time = np.arange(len(st[0].data)) * 0.004

for _c, _i in enumerate(chas):
	plt.subplot(7,1,5 + _c)
	plt.title(_i)
	plt.plot(_time, st[_c].data, color = colors[_c])
	plt.xlim(28, 40)
	plt.xticks(np.arange(28,41,1))
plt.tight_layout()
plt.savefig("plots/TA19.2020.108.003429_spectrogram_slices.png", dpi = 300)


# scan through Sxx, find the highest component, then plot like a cross section for that

max_amp = 0
max_location = 0

for _f in range(len(Sxx)): # efficien
	for _t in range(len(Sxx[_f])):
		if Sxx[_f, _t] > max_amp:
			max_amp = Sxx[_f, _t]
			max_location = (_f, _t)
#
#print(max_location)
_x, _y = max_location
print(f[_x], t[_y])
print(max_amp)
plt.plot(f, Sxx[:, _y], color = 'blue', linewidth = 1)
plt.xlim(0,20)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.grid()
plt.xticks(np.arange(0,22,2))
plt.tight_layout()
#plt.savefig("plots/sample_spectrogram_slice_TA19.2020.108.003429.png", dpi = 300)
plt.clf()

# """
# fig, axs = plt.subplots(3,2, figsize = (8,6))
# #fig.tight_layout()

# _x0 = 25
# _x1 = 40

# for i in range(3):
# 	im = axs[i, 1].pcolormesh(ts[i], freqs[i], (specs[i]), shading = 'gouraud', cmap = 'inferno')
# 	axs[i,1].set_ylim(1,20)
# 	axs[i,1].set_xlim(_x0, _x1)
# #plt.imshow(Sxx, cmap = 'inferno')
# cbar_ax = fig.add_axes([0.900, 0.15, 0.025, 0.7])
# fig.colorbar(im, cax = cbar_ax)
# #fig.suptitle("TA19.2020.108.003429.png")

# #axs[0].set_xlim(25, 40)

# # print out which frequencies have the most content

# _time = np.arange(len(st[0].data)) * 0.004
# for i in range(3):
# 	axs[i, 0].plot(_time, st[i].data, color = 'black', linewidth = 0.5)
# 	axs[i, 0].set_title(st[i].stats.channel)
# 	axs[i, 0].set_xlim(_x0, _x1)
# 	#axs[i+1].set_xlim(25, 40)

#plt.savefig("plots/sample_all_spectrogram_with_trace_TA19", dpi = 300)
#plt.savefig("plots/sample_cut_spectrogram_with_trace_TA19", dpi = 300)
#plt.show()