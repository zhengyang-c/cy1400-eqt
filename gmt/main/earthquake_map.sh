gmt set PS_MEDIA=A2
# E: 85 - 120
# N: -15 - 15

# variables
PROJ="-JM6i"
LIMS="-R90/110/-10/10"
PSFILE="sumatra.ps"
ETOP="../etop/ETOPO1_Ice.grd"
CPT="-C../cpt/topo3.cpt"
PLATE="../plate/usgs2015_plates.xy"

gmt pscoast $PROJ $LIMS -W1p -Di -N1/0.5p -A0/0/1 -K > $PSFILE
gmt grdimage $ETOP $PROJ $LIMS $CPT -K -O >> $PSFILE

gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE

gmt psscale $PROJ $LIMS -Dg91/-7.8+w5c/0.2c+jTL+h -Bx40+l"Earthquake Depth [km]" -C../cpt/dep.cpt --LABEL_FONT_SIZE=14 -K -O >> $PSFILE
# R95/96.5/4/6

echo "94.9 6.5 16,0 LM Aceh" | gmt pstext $PROJ $LIMS -F+f+j -K -O >> $PSFILE
printf "95 4\n96.5 4\n96.5 6\n95 6\n95 4" | gmt psxy $PROJ $LIMS -W3p,blue -K -O >>$PSFILE

awk '{print $1,$2,$3,$4*$4*$4*$4/20000}' ../json/85.110.-15.15.mag6.1976-2020.xy | gmt psxy $PROJ $LIMS -Sci -W0.5p -C../cpt/dep.cpt -K -O >> $PSFILE

#gmt psmeca fiji_mt.dat $PROJ $LIMS -Sm0.2i -Zdep.cpt -W0.5p -T -K -O >> $PSFILE

gmt psbasemap $PROJ $LIMS -Bxa5 -Bya5 -BWeSn -O >> $PSFILE
gmt psconvert $PSFILE -Tf -A+m1c