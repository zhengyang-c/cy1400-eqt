#!/bin/bash
gmt set PS_MEDIA=A2


PSFILE="2020count_abs.ps"
PROJ="-JM6i"
LIMS="-R95/96.5/4/6"
ETOP="../etop/GMRTv3_9_20210325topo_61m.grd"
CPT="-C../cpt/colombia.cpt"
PLATE="../plate/usgs2015_plates.xy"
SLAB="../slab/sum_slab2_dep_02.23.18.grd"

gmt pscoast $PROJ $LIMS -W1p -Df -N1/0.5p -A0/0/4 -Sblue -Ggreen -K > $PSFILE
gmt psbasemap $PROJ $LIMS -Bxa0.5 -Bya0.25 -BWeSn -K -O --FORMAT_GEO_MAP=D>> $PSFILE
gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE
gmt grdimage $ETOP $PROJ $LIMS $CPT -K -O >> $PSFILE
gmt grdcontour $SLAB $PROJ $LIMS -C10 -W0.5p,grey50 -K -O >> $PSFILE
gmt grdcontour $SLAB $PROJ $LIMS -C50 -W2p -A100 -Gd4c -K -O >> $PSFILE
#awk -F, '{if (NR!=1) {print $2, $3, $6/50}}' array_sta.csv | gmt psxy $PROJ $LIMS -W0.5p -Sci -Gred -K -O >> $PSFILE
awk -F, '{if (NR!=1) {print $2, $3, $4/5000}}' array_sta.csv | gmt psxy $PROJ $LIMS -W0.5p -Sci -Gred -K -O >> $PSFILE
awk -F, '{if (NR!=1 && $4 > 800) {print $2, $3, $1}}' array_sta.csv | gmt pstext $PROJ $LIMS -D0.5i/0 -K -O >> $PSFILE
#awk -F, '{if (NR!=1 && $4 > 800) {printf "%.5f,%.5f,%.2f\n",$2, $3, $6}}' array_sta.csv | gmt pstext $PROJ $LIMS -D-0.5i/0 -K -O >> $PSFILE
awk -F, '{if (NR!=1 && $4 > 800) {printf "%.5f,%.5f,%d\n",$2, $3, $4}}' array_sta.csv | gmt pstext $PROJ $LIMS -D-0.5i/0 -K -O >> $PSFILE



printf '95.75 4.25 Events per day (filtered)\n' | gmt pstext $PROJ $LIMS -F+f14p,0+jTC -K -O >> $PSFILE

#awk '{print $2, $3, $1}' station_info.dat | gmt pstext $PROJ $LIMS -D0.5i/0 -O >> $PSFILE

gmt psscale $PROJ $LIMS -Dg95.75/4.20+w10c/0.5c+jTC+h -G-4000/4000 -Bx2000+l"Elevation" $CPT --LABEL_FONT_SIZE=14 -O >> $PSFILE

gmt psconvert $PSFILE -Tf -A+m1c