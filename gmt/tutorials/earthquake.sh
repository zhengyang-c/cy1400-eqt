#!/bin/sh
gmt set PS_MEDIA=A2
PROJ="-JM20c"
LIMS="-R80/110/0/35"
PSFILE="earthquake.ps"
gmt makecpt -T1/700 > rainbow.cpt
gmt pscoast $PROJ $LIMS -W1p -Di -N1/0.5p -K > $PSFILE
gmt psscale $PROJ $LIMS -Dg85/3+w5c/0.5c+jTC+h -Bx100 -Crainbow.cpt -K -O >> $PSFILE
gmt psbasemap $PROJ $LIMS -Bxa10g10 -Bya5g5 -BWeSn -K -O >> $PSFILE
gmt psxy stars.xy $PROJ $LIMS -Sa0.3i -W0.25p -Gred -K -O >> $PSFILE
gmt psxy eqs1.xy $PROJ $LIMS -Scc -W0.5p -Crainbow.cpt -O >> $PSFILE
gmt psconvert $PSFILE -Tg -A+m1c

# S: symbols, Sa star, sc circle
# N: boundaries, n1: political
# -C: 3rd column
# -S: 4th column