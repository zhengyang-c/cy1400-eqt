#!/bin/sh

PROJ="-JC15c"
LIMS="-R50/170/-10/70"
BLUE="50/100/255"
DRY="225/175/100"
PSFILE="asia.ps"
PNGFILE="asia.png"
gmt pscoast $PROJ $LIMS -G$DRY -S$BLUE -W1p -N1/0.25p -Dc -K > $PSFILE
gmt psbasemap $PROJ $LIMS  -Bxa10g10 -Bya5g5 -BWeSn -O >> $PSFILE
gmt psconvert $PSFILE -Tg -A