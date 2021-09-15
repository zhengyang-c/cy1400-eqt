gmt set PS_MEDIA=A2
gmt set FORMAT_GEO_MAP=D
# variables
PROJ="-JM6i"
LIMS="-R94/97.25/3.5/6"
STATION_FILE=/home/zy/cy1400-eqt/station_info.dat
#LIMS="-R-122.25/-122.24/37.87/37.89"

ETOP="/home/zy/gmt/etop/GMRTv3_9_20210325topo_61m.grd"
CPT="-C/home/zy/gmt/cpt/colombia.cpt"
#PLATE="/home/zy/gmt/plate/usgs2015_plates.xy"
PLATE="/home/zy/gmt/plate/sumatran_fault_ll.xy"
SLAB="/home/zy/gmt/slab/sum_slab2_dep_02.23.18.grd"

DEPCPT="-C/home/zy/gmt/cpt/dep.cpt"

#PLOTFILE=~/cy1400-eqt/real_postprocessing/aug5_hypoDD_1.reloc
#PLOTFILE=~/cy1400-eqt/real_postprocessing/hypoDD.reloc

#PSFILE="aceh_7jul_after.ps"
#PSFILE="aceh_5jul_after.ps"

PLOTFILE=$1
PSFILE=${2}.ps

#AFTER=$2

gmt makecpt -Crainbow -T0/40/2 > temp.cpt


gmt grdimage $ETOP $PROJ $LIMS $CPT -K > $PSFILE
#gmt pscoast $PROJ $LIMS -W1p -Df -N1/0.5p -A0/0/1 -K -O >> $PSFILE

gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE

awk '{print $3, $2, $4}' $PLOTFILE | gmt psxy $PROJ $LIMS -Sc0.05i -W0.5p -Ctemp.cpt -K -O >> $PSFILE
#awk '{print $3, $2, $4}' $AFTER | gmt psxy $PROJ $LIMS -Sd0.25i -W0.5p $DEPCPT -K -O >> $PSFILE

#printf "95.75 4.15 PLOTFILE hypoDD" | gmt pstext $PROJ $LIMS -K -O >> $PSFILE
printf "96.5 6 After hypoDD" | gmt pstext $PROJ $LIMS -F+jTR -D-0.1/-0.1 -K -O >> $PSFILE

awk '{print $2,$3}' $STATION_FILE | gmt psxy $PROJ $LIMS -Gwhite -St0.02i -W0.5p -K -O >> $PSFILE
awk '{print $2,$3,$1}' $STATION_FILE | gmt pstext $PROJ $LIMS -F+f4p,0+jRB -D-0.2c/0 -K -O >> $PSFILE
#gmt grdcontour $SLAB $PROJ $LIMS -C10 -W0.5p,grey50 -K -O >> $PSFILE
#gmt grdcontour $SLAB $PROJ $LIMS -C50 -W2p -A100 -Gd4c -K -O >> $PSFILE
gmt psscale $PROJ $LIMS -Dg95.75/3.8+w12c/0.2c+jBC+h -G0/40 -Bx2+l"Depth" -Ctemp.cpt --LABEL_FONT_SIZE=8 -K -O >> $PSFILE

gmt psbasemap $PROJ $LIMS -BWeSn -Bxa0.5 -Bya0.5 -O >> $PSFILE

gmt psconvert $PSFILE -Tf -A+m1c
gmt psconvert $PSFILE -Tg -A+m1c

rm temp.cpt