gmt set PS_MEDIA=A2
gmt set FORMAT_GEO_MAP=D

PROJ="-JM6i"
LIMS="-R95/96.5/4/6"
STATION_FILE=/home/zy/cy1400-eqt/station_info.dat
ETOP="/home/zy/gmt/etop/GMRTv3_9_20210325topo_61m.grd"
CPT="-C/home/zy/gmt/cpt/colombia.cpt"

PLATE="/home/zy/gmt/plate/sumatran_fault_ll.xy"
SLAB="/home/zy/gmt/slab/sum_slab2_dep_02.23.18.grd"

DEPCPT="-C/home/zy/gmt/cpt/dep.cpt"


PSFILE=test.ps

gmt xyz2grd test.xyz -Gtest.grd -I0.05 $LIMS

#AFTER=$2

gmt makecpt -Crainbow -T0/200/10 > temp.cpt



gmt grdimage test.grd $PROJ $LIMS -Ctemp.cpt -K > $PSFILE

#gmt psxy test.xyz $PROJ $LIMS -Sc0.07 -W0.01 -Ctemp.cpt -K > $PSFILE
gmt pscoast $PROJ $LIMS -W1p -Df -N1/0.5p -A0/0/1 -K -O >> $PSFILE

#gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE
gmt psscale $PROJ $LIMS -Dg95.75/4.1+w10c/0.5c+jBC+h -G0/50/10 -Ctemp.cpt --LABEL_FONT_SIZE=8 -K -O >> $PSFILE

gmt psbasemap $PROJ $LIMS -BWeSn -Bxa0.5 -Bya0.5 -O >> $PSFILE

gmt psconvert $PSFILE -Tf -A+m1c

rm temp.cpt