#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from obspy import read
from obspy.geodetics import gps2dist_azimuth
import os
import glob
import time
import subprocess
import math
import numpy as np
import pandas as pd

def main(event_folder, output_txt, output_csv, pzfile, sac_transfer = False, location_file = "", station_file = ""):

    if station_file:
        station_info = parse_station_info(station_file)
        df = pd.read_csv(location_file)


    time1 = time.time()

    basedir = event_folder
    #basedir = "/home/zy/cy1400-eqt/7jul_event_archive" # directory of sac file folders
    sacdirs = [f for f in os.listdir(basedir) if f.startswith('0')]
    # folder names containing sac files for each event
    sacdirs.sort()
    chane = 'EHE'
    chann = 'EHN'
    chanz = 'EHZ'
    ptime_header = 'a' # sac header variable for P-wave arrival time
    stime_header = 't0' 
    p_before = 0.5 # time window in seconds before P arrival time
    #p_after = 1.5
    #p_win_ratio = 0.09 # time window after P arrival time is p_win_ratio * distance 

    #pzfile = os.path.join(basedir,'zland.pz')
    #pzfile1 = './EOS_MM_station_info/q330_nmx.pz'
    #pzfile2 = './EOS_MM_station_info/q330_STS2.5.pz'
    #pzfile1_stas = ['EW06', 'EW07', 'EW08', 'M002', 'M003', 'M005', 'M007', 'M009', 'M025', 'M026']

    os.putenv("SAC_DISPLAY_COPYRIGHT", "0")

    f_out = open(output_txt,'w')


    odf = pd.DataFrame()
    _c = 0

    for sacdir in sacdirs:
        print(sacdir)
        zfiles = glob.glob(os.path.join(basedir, sacdir, '*' + chanz + '*SAC'))

        print(zfiles)
        stas = [zfile.split('/')[-1].split('.')[0] for zfile in zfiles] # get station names for sac file named in "net.sta.*"

        #read snr file as dataframe
        # snr_file=os.path.join(basedir,sacdir,'snr.txt')
        # snr_df = pd.DataFrame(columns=['sta','chan','snr1','snr2'])
        # with open(snr_file) as f:
        #     lines=f.readlines()
        #     for line in lines:
        #         x=line.split(' ')
        #         xnew=','.join(filter(None,x)).split(',')
        #         pd1=pd.DataFrame([[xnew[0],xnew[1],xnew[2],xnew[3][:-1]]],columns=['sta','chan','snr1','snr2'])
        #         snr_df=snr_df.append(pd1,ignore_index=True)

        mags = []
        for sta in stas:
            s = ""
            for sacfile in glob.glob(basedir+'/'+sacdir+'/*'+sta+'*SAC'):

                print(sacfile)
                chan_tmp = sacfile.split('/')[-1].split('.')[2]
                s += "r {} \n".format(sacfile)
                #s += "ch KCMPNM {} \n".format(chan_tmp)
                s += "rmean; rtr; taper \n"
                s += "bp c 1 45 n 4 p 2 \n"
                s +="transfer from polezero subtype {} to wa \n".format(pzfile)
                #s += "trans from pol s {} to general nzeros 2 freeperiod 0.8 damping 0.7 magnification 2080 \n".format(pzfile) # transfer to Wood-Anderson instrument, in nanometers, meters?
                #s += "trans from polezero s {} to none freq 0.8 1 20 25 \n".format(pzfile) # transfer to Wood-Anderson instrument
                s += "w append .wa \n"
            s += "q \n"


            if sac_transfer:
                subprocess.Popen(['sac'], stdin=subprocess.PIPE).communicate(s.encode())

            efile = glob.glob(os.path.join(basedir, sacdir, "*" + sta + "*" + chane + "*SAC*wa"))
            nfile = glob.glob(os.path.join(basedir, sacdir, "*" + sta + "*" + chann + "*SAC*wa"))

            #print(efile, nfile )

            try:
                ste = read(efile[0])
                stn = read(nfile[0])
            except:
                ste = read(efile)
                stn = read(nfile)

            try:
                ste.detrend('demean')
                ste.detrend('linear')
                ste.filter(type="bandpass", freqmin=0.2, freqmax=20.0, zerophase=True)
            except:
                print("Error with the .wa file")
            #print(ste[0].data)

            datatre = ste[0].data
            stn.detrend('demean')
            stn.detrend('linear')
            stn.filter(type="bandpass", freqmin=0.2, freqmax=20.0, zerophase=True)
            datatrn = stn[0].data
            #print(ste[0].data)
            if station_file:
                _df = pd.DataFrame(data = {'ID': [int(sacdir)]})
                _df = _df.merge(df[["ID", "LAT", "LON"]], how = 'left', on = 'ID')


                _evlo, _evla = _df.at[0, "LON"], _df.at[0, "LAT"]

                _stlo, _stla = station_info[sta]["lon"], station_info[sta]["lat"]


                dist = (0.001) * gps2dist_azimuth(_stla, _stlo, _evla, _evlo)[0]
                
            else:
                dist = ste[0].stats.sac.dist

            
            #try:
            ptime = ste[0].stats.sac[ptime_header]
            stime = ste[0].stats.sac[stime_header]

            #p_after = 0.73*dist/6 + 3
            p_after = stime - ptime + 3
            delta = ste[0].stats.delta
            b_time = ste[0].stats.sac.b

            #print(ptime, b_time, delta)

            ptime_id = round( (ptime - b_time)/delta )
            start_id = ptime_id - round(p_before/delta)
            end_id = ptime_id + round(p_after/delta)
            #amp = max( max(abs(datatre[start_id:end_id])), max(abs(datatrn[start_id:end_id])) ) * 1.0e-6 
            # 1.0e-6 is from nm to millimeter (mm)
            start_id = int(start_id)
            end_id = int(end_id)

            #print(start_id, end_id)
            #print(len(datatre), len(datatrn))
            datatre=datatre[start_id:end_id]
            datatrn=datatrn[start_id:end_id]

            amp = (np.max(datatre) + np.abs(np.min(datatre)) + np.max(datatrn) + np.abs(np.min(datatrn)))/4 * 1000 * 15000 
            # 15000 is for the nodes 
            # 1000 is from meter to millimeter (mm) see Hutton and Boore (1987)
            mag = math.log10(amp) + 1.110*math.log10(dist/100) + 0.00189*(dist-100) + 3.0
            #mag = math.log10(amp) + 1.110*math.log10(dist) + 0.00189*(dist) - 2.09
            #mag = math.log10(amp) + 1.60*math.log10(dist) - 0.15
            #mag = math.log10(amp) + 1.60*math.log10(dist) - 0.15
            #mag = math.log10(amp) + 2.76*math.log10(dist) - 2.48

            odf.at[_c, "ID"] = sacdir
            odf.at[_c, "sta"] = sta
            odf.at[_c, "m_l"] = mag 

            _c += 1

            mags.append(mag)
            #except:
            #    print('May not have some headers in sac file %s'%(efile))
            #mag_mean = np.mean(mags)
        print(mags) 
        mag_mean = np.median(mags)
        mag_std = np.std(mags)
        f_out.write('%s  %.1f  %.2f\n'%(sacdir,mag_mean,mag_std))

    f_out.close()
    time2 = time.time()

    odf.to_csv(output_csv, index = False)
    print("elapsed time: %.2f"%(time2-time1))




def parse_station_info(input_file):
	# 'reusing functions is bad practice' yes haha

	station_info = {}

	with open(input_file, 'r') as f:
		for line in f:
			#print(line)
			try:
				sta, lon, lat = [x for x in line.strip().split("\t") if x != ""]
			except:
				sta, lon, lat = [x for x in line.strip().split(" ") if x != ""] 
			station_info[sta] = {"lon": float(lon), "lat": float(lat)}	
	return station_info

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("event_folder")
    parser.add_argument("output_txt")
    parser.add_argument("output_csv")
    parser.add_argument("pz_file")
    parser.add_argument("-s", "--sac_wa", action = "store_true", help = "Set to true to create .wa files. Only needs to be run once.")
    parser.add_argument("-lf", "--event_location_file", help = "Uses .csv locations instead of SAC headers which may not be available or updated properly.")
    parser.add_argument("-sf", "--station_file", help = "Include to use locations from file instead of the SAC headers.")
    args = parser.parse_args()
    main(args.event_folder, args.output_txt, args.output_csv, args.pz_file,args.sac_wa,  location_file = args.event_location_file, station_file = args.station_file)