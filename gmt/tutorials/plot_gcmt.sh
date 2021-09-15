gmt set PS_MEDIA=A2
PSFILE="samerica.ps"
PROJ="-JM3.4i"
LIMS="-R-86/-64/-40/10"
ETOP="../etop/ETOPO1_Ice.grd"
CPT="-C../cpt/topo2.cpt"
gmt pscoast $PROJ $LIMS -W1p -Dl -K > $PSFILE
gmt grdimage $ETOP $PROJ $LIMS $CPT -K -O >> $PSFILE
awk '{print $2, $3,$5*$5*$5/3000} ' gcmt.dat | gmt psxy $PROJ $LIMS -W0.5p -Sci -Gred -K -O >> $PSFILE
awk '{print $2,$3,"16,0", "RM", substr($1,1,4), $5' gcmt.dat | gmt pstext $PROJ $LIMS -F+f+j -K -O -D-0.12i/0i >> $PSFILE
# -F+f+j: flag, font, justification. rm == right-middle justified
# -D: shift text

#gmt grdcontour sam_slab.grd $PROJ $LIMS -C25 -W0.5p,grey50 -K -O >> $PSFILE
#gmt grdcontour sam_slab.grd $PROJ $LIMS -C100 -W2p -A100 -Gd4c -K -O >> $PSFILE

# use multiple times to have more control over how the map looks
#gmt pscoast $PROJ $LIMS -Dl -W0.5p -N1/1p -K -O >> $PSFILE
gmt psbasemap $PROJ $LIMS -Bxa5 -Bya5 -BWeSn -O >> $PSFILE
gmt psconvert $PSFILE -Tg -A+m1c