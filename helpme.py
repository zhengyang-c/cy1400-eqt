import matplotlib
import numpy as np
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os


def log(scnl, picks, polarity, snr, unc, pick_string, file_name):
	# idk what to do with this
	text_file_name = os.path.join("picks", "whole_day", "indiv_" + pick_string, "summary_" + file_name + ".txt")

	headers = ["picks", "polarity", "snr", "unc"]
	texts = [picks, polarity, snr, unc]
	for i in range(len(headers)):
		print("{}:{}".format(headers[i], texts[i]))

	with open(text_file_name, "w" ) as f:
		f.write("#" + "\t".join(headers)+"\n")
		for i in range(len(picks)):			
			f.write("{}\t{}\t{}\t{}\n".format(picks[i], polarity[i], snr[i], unc[i]))

'''trace: direct numpy time series'''
def plot_1(time, trace, file_name, save_folder): # plot only ground motion trace
	plt.title(file_name)
	plt.xlabel("Time (s)")
	plt.ylabel("Ground motion (m)")
	plt.plot(time, trace, color = 'black', linewidth=0.1)
	plt.savefig(os.path.join(save_folder, "{}.png".format(datetime.now().strftime("%Y%m%d %H%M"))), dpi = 300)


def plot_2(time, trace, trace2, file_name, save_folder): # plot ground motion + cf (classic) 
	fig, axs = plt.subplots(2)
	fig.suptitle(file_name)

	axs[0].plot(time, trace, color = 'black', linewidth = 0.1)
	#axs[0].set(xlabel='Time (s)')

	axs[1].plot(time, trace2, color = 'blue', linewidth = 0.2)
	axs[1].set(xlabel='Time (s)')

	plt.savefig(os.path.join(save_folder, "{}_{}-{}.png".format(datetime.now().strftime("%Y%m%d %H%M%S"), start_time, end_time)), dpi = 300)

''' depreciated '''
def plot_3(): # plot ground motion + different cfs
	fig, axs = plt.subplots(6, figsize=(8,10))
	fig.tight_layout()
	fig.suptitle(file_name)

	axs[0].plot(time, trace.data, color = 'black', linewidth = 0.1)

	cfs = ["classic sta lta", "recursive sta lta", "delayed sta lta", "carl sta trig", "z detect"]
	cf_data = [cf_classic.data, cf_recursive.data, cf_delayed.data, cf_carl.data, cf_z.data]
	#axs[0].set(xlabel='Time (s)')

	for n in range(1,6):
		axs[n].plot(time, cf_data[n - 1], color = 'blue', linewidth = 0.2)
		axs[n].set_title(cfs[n - 1], fontsize=8)


	plt.savefig(os.path.join(save_folder, "{}_{}-{}.png".format(datetime.now().strftime("%Y%m%d %H%M%S"), start_time, end_time)), dpi = 300)


'''depreciated'''
def plot_4(): # plot ground motion + classic and recursive with different exponents
	fig, axs = plt.subplots(5,2, figsize=(14,8))
	fig.tight_layout()
	fig.suptitle(file_name)

	axs[0,0].plot(time, trace.data, color = 'black', linewidth = 0.1)
	axs[0,1].plot(time, trace.data, color = 'black', linewidth = 0.1)

	cfs = ["classic sta lta (power 1)", "power 2", "power 3", "power 4"]
	cf_data = [cf_classic.data, cf_classic_2.data, cf_classic_3.data, cf_classic_4.data]
	#axs[0].set(xlabel='Time (s)')

	for n in range(1,5):
		axs[n,0].plot(time, cf_data[n - 1], color = 'blue', linewidth = 0.2)
		axs[n,0].set_title(cfs[n - 1], fontsize=8)

	cfs = ["recursive sta lta (power 1)", "power 2", "power 3", "power 4"]
	cf_data = [cf_recursive.data, cf_recursive_2.data, cf_recursive_3.data, cf_recursive_4.data]

	for n in range(1,5):
		axs[n,1].plot(time, cf_data[n - 1], color = 'blue', linewidth = 0.2)
		axs[n,1].set_title(cfs[n - 1], fontsize=8)

	plt.savefig(os.path.join(save_folder, "classic recursive sta lta power comparison_{}_{}-{}.png".format(datetime.now().strftime("%Y%m%d %H%M%S"), start_time, end_time)), dpi = 300)
	plt.clf()

'''depreciated'''
def plot_5(file_name): # plot ground motion + classic with different sta/lta windows 
	fig, axs = plt.subplots(6, figsize=(8,10))
	fig.tight_layout()
	fig.suptitle(file_name)

	axs[0].plot(time, all_cfs[0], color = 'black', linewidth = 0.1)
	titles = ["1/10", "0.5/5", "2/20", "2/10", "0.1/5"]

	for n in range(1,6):
		axs[n].plot(time, all_cfs[n], color = 'blue', linewidth = 0.2)
		axs[n].set_title(titles[n-1], fontsize=8)


	plt.savefig(os.path.join(save_folder, "timewindow comparison_{}_{}-{}.png".format(datetime.now().strftime("%Y%m%d %H%M%S"), start_time, end_time)), dpi = 300)



# this is to compare different picking functions
def plot_phasepa_picks_together(file_name, time, trace, pick_string, *picks): 
	plot_file_name = os.path.join("picks", pick_string + "_" +  file_name + ".png")
	
	fig, axs = plt.subplots(1 + len(picks), figsize = (8, 10))
	fig.suptitle(file_name)
	fig.tight_layout()


	axs[0].plot(time, trace, color = 'black', linewidth = 0.1)
	axs[len(picks)].set(xlabel='Time (s)')

	for n, pk in enumerate(picks):
		axs[n + 1].plot(time, trace, color = 'black', linewidth = 0.1)
		axs[n + 1].set(title = pick_string.split("_")[n])
		for pick in pk:
			pick = pick - start_UTC_time - start_time
			pick = int(pick * df)
			axs[n + 1].plot([time[pick], time[pick]], [-1e-6, 1e-6], color = 'red', linewidth = 1, linestyle = 'dashed')

	plt.savefig(plot_file_name, dpi = 300)
	plt.clf()


def plot_phasepa_picks(file_name, time, trace, timeshift, triggers, picks, pick_type): # plot all picks from a list picks (from phasePA, picks are in seconds from start)
	# for each pick, output a txt file with ascii time series data, file name the filename of the thing + plot 

	# the plot will have a red line drawn at the pick time 

	before_trigger, after_trigger = triggers

	for n, pick in enumerate(picks):
		# plot file

		pick = pick - start_UTC_time - start_time

		pick = int(pick * df)

		plot_file_name = os.path.join("picks", "indiv_" + pick_type, "phasepa_" + pick_type + "_" + file_name + "_" + str(n).zfill(3) + ".png")
		ascii_file_name = os.path.join("picks", "indiv_" + pick_type, "phasepa_" + pick_type + "_" + file_name + "_" + str(n).zfill(3) + ".txt")

		plt.title("Pick {}:{}".format(str(n).zfill(3), file_name))
		plt.plot(time[pick - before_trigger : pick + after_trigger], trace[pick - before_trigger : pick + after_trigger], color = 'black', linewidth = 0.2)
		plt.plot([time[pick], time[pick]], [-1e-6, 1e-6], color = 'red', linewidth = '1', linestyle = 'dashed')

		plt.savefig(plot_file_name)
		plt.clf()

		with open(ascii_file_name, 'w') as f:
			for i in range(len(trace[pick - before_trigger : pick + after_trigger])):
				f.write("{}\t{}\n".format((time[pick - before_trigger : pick + after_trigger] * 0.0080)[i], trace[pick - before_trigger : pick + after_trigger][i]))

	# also plot all the picks on the same plot 

	plot_file_name = os.path.join("picks", "all_" + pick_type + "_" +  file_name + ".png")
	ascii_file_name = os.path.join("picks", "all_" + pick_type + "_" + file_name + ".txt")
	plt.title(file_name)	
	plt.xlabel("Time (s)")
	plt.ylabel("Ground motion (m)")
	plt.plot(time, trace, color = 'black', linewidth=0.1)
	for pick in picks:
		pick = pick - timeshift
		pick = int(pick * df)
		plt.plot([time[pick], time[pick]], [-1e-6, 1e-6], color = 'red', linewidth = 1, linestyle = 'dashed')

	plt.savefig(plot_file_name, dpi = 300)
	plt.clf()

def plot_obspy_picks_together(file_name, time, trace, picks, pick_string):

	plt.xlabel("Time (s)")
	plt.ylabel("Ground motion (m)")

	plt.plot(time, trace, color = 'black', linewidth = 0.1)
	plot_file_name = os.path.join("picks", "obspy_" + pick_string + "_" + file_name + ".png")
	for (pick,_) in picks:
		# plot file
		plt.plot([time[pick], time[pick]], [-1e-6, 1e-6], color = 'red', linewidth = '1', linestyle = 'dashed')

	plt.savefig(plot_file_name)
	plt.clf()


def plot_obspy_picks(file_name, time, trace, triggers, start_UTC_time, picks, pick_type): # plot all picks from a list picks (from the trigger_onset function)
	# for each pick, output a txt file with ascii time series data, file name the filename of the thing + plot 

	# the plot will have a red line drawn at the pick time 
	(before_trigger, after_trigger) = triggers

	for n, (pick,_) in enumerate(picks):
		# plot file
		event_time = start_UTC_time + pick

		event_time_string = event_time.strftime("%H_%M_%S")
		plot_file_name = os.path.join("picks", "indiv_obspy" , pick_type + "_" + file_name + "_" + event_time_string + ".png")
		ascii_file_name = os.path.join("picks", "indiv_obspy", pick_type + " _" + file_name + "_" + event_time_string + ".txt")

		plt.title("Pick {}:{}".format(str(n).zfill(3), file_name))
		plt.plot(time[pick - before_trigger : pick + after_trigger], trace[pick - before_trigger : pick + after_trigger], color = 'black', linewidth = 0.2)
		plt.plot([time[pick], time[pick]], [-1e-6, 1e-6], color = 'red', linewidth = '1', linestyle = 'dashed')

		plt.savefig(plot_file_name, dpi = 300)
		plt.clf()

		with open(ascii_file_name, 'w') as f:
			for i in range(len(trace[pick - before_trigger : pick + after_trigger])):
				f.write("{}\t{}\n".format((time[pick - before_trigger : pick + after_trigger] * 0.0080)[i], trace[pick - before_trigger : pick + after_trigger][i]))

