#!/bin/sh
gmt set PS_MEDIA=A4
PSFILE="topo_2.ps"
PROJ="-JM8i"
LIMS="-R-130/-60/20/55"

gmt grdimage ETOPO5.grd $PROJ $LIMS -Ctopo2.cpt -K > $PSFILE
gmt pscoast $PROJ $LIMS -Dl -W1p -N1/1p -K -O >> $PSFILE
gmt psbasemap $PROJ $LIMS -Bxa10 -Bya5 -BWeSn -O >> $PSFILE
gmt psconvert $PSFILE -Tg -A+m1c