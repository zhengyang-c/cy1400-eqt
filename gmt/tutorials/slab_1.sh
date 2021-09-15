gmt set PS_MEDIA=A4
PSFILE="slab_1.ps"
PROJ="-JM5i"
LIMS="-R280/300/-35/-10"
gmt grdimage ETOPO5.grd $PROJ $LIMS -Ctopo3.cpt -K > $PSFILE
gmt grdcontour sam_slab.grd $PROJ $LIMS -C25 -W0.5p,grey50 -K -O >> $PSFILE
gmt grdcontour sam_slab.grd $PROJ $LIMS -C100 -W2p -A100 -Gd4c -K -O >> $PSFILE

# use multiple times to have more control over how the map looks
gmt pscoast $PROJ $LIMS -Dl -W0.5p -N1/1p -K -O >> $PSFILE
gmt psbasemap $PROJ $LIMS -Bxa10 -Bya5 -BWeSn -O >> $PSFILE
gmt psconvert $PSFILE -Tg -A+m1c