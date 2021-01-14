#!/bin/sh
#######################################################
######## pre-process: remove response, decimate, highpass
#######################################################
source ~/.bashrc
pz=zland_nodes.pz
lmax=`wc -l sta_todo.dat| awk '{print $1}'`
for ((l=1;l<=$lmax;l++));do
echo number $l
dir=`awk '{if (NR=='$l') print $1}' sta_todo.dat`

#for dir in `ls -d *`; do
echo "Doing station " $dir
cd $dir
#cp ../mseed2sac .
mkdir -p preprocessed

# convert to sac
ls *.EH* > file_lst
#ls *a01200119*.EH* > file_lst
while read line ; do
./mseed2sac $line
done < file_lst
rm -rf file_lst

# pre process
#ls *a01200120*.EH[NE]*SAC > file_lst
#ls *.EH[NE]*SAC
ls *.EH[NE]*SAC > file_lst
while read line ; do
endp=`saclst e f ${line} | awk '{print $2+1}'`
#echo endpoint is $endp
echo "cut 0 b +900" > mv_resp.m # cut 15 minutes of data
echo "r ${line}" >> mv_resp.m
echo "chnhdr b -900.004" >> mv_resp.m
echo "w tmp_begin" >> mv_resp.m
echo "chnhdr b ${endp}" >> mv_resp.m
echo "w tmp_end" >> mv_resp.m
echo "cut off" >> mv_resp.m
echo "r tmp_begin" >> mv_resp.m
echo "merge ${line}" >> mv_resp.m
echo "merge tmp_end" >> mv_resp.m
echo "rmean" >> mv_resp.m
echo "rtr" >> mv_resp.m
echo "taper" >> mv_resp.m # taper edges to minimise edge effects
echo "transfer from polezero subtype $pz to VEL freq 0.001 0.003 250 500" >> mv_resp.m
echo "rtr" >> mv_resp.m
echo "mul 15000" >> mv_resp.m # Multiply to get into ground velocity m/s
echo "w tmp" >> mv_resp.m
echo "cut b +900.004 e -901.004" >> mv_resp.m
echo "r tmp" >> mv_resp.m
echo "chnhdr b 0" >> mv_resp.m
echo "decimate 2" >> mv_resp.m
echo "rmean" >> mv_resp.m
echo "rtr" >> mv_resp.m
echo "hp c 0.05 n 4 p 2" >> mv_resp.m
echo "w preprocessed/${line}.preproc" >> mv_resp.m
printf "macro mv_resp.m\nQuit\n" | sac
rm -rf tmp tmp_begin tmp_end
done < file_lst
rm -rf file_lst

# pre process
#ls *a01200120*.EHZ*SAC > file_lst
#ls *.EHZ*SAC
ls *.EHZ*SAC > file_lst
while read line ; do
endp=`saclst e f ${line} | awk '{print $2+1}'`
echo "cut 0 b +900" > mv_resp.m # cut 15 minutes of data
echo "r ${line}" >> mv_resp.m
echo "chnhdr b -900.004" >> mv_resp.m
echo "w tmp_begin" >> mv_resp.m
echo "chnhdr b ${endp}" >> mv_resp.m
echo "w tmp_end" >> mv_resp.m
echo "cut off" >> mv_resp.m
echo "r tmp_begin" >> mv_resp.m
echo "merge ${line}" >> mv_resp.m
echo "merge tmp_end" >> mv_resp.m
echo "rmean" >> mv_resp.m
echo "rtr" >> mv_resp.m
echo "taper" >> mv_resp.m # taper edges to minimise edge effects
echo "transfer from polezero subtype $pz to VEL freq 0.001 0.003 250 500" >> mv_resp.m
echo "rtr" >> mv_resp.m
echo "mul 15000" >> mv_resp.m # Multiply to get into ground velocity m/s
echo "mul -1" >> mv_resp.m #multiple Z to get right polarity
echo "w tmp" >> mv_resp.m
echo "cut b +900.004 e -901.004" >> mv_resp.m
echo "r tmp" >> mv_resp.m
echo "chnhdr b 0" >> mv_resp.m
echo "decimate 2" >> mv_resp.m
echo "rmean" >> mv_resp.m
echo "rtr" >> mv_resp.m
echo "hp c 0.05 n 4 p 2" >> mv_resp.m
echo "w preprocessed/${line}.preproc" >> mv_resp.m
printf "macro mv_resp.m\nQuit\n" | sac
rm -rf tmp tmp1
done < file_lst
rm -rf file_lst


cd ..
done
