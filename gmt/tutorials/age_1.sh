#!/bin/sh
gmt set PS_MEDIA=A4
PSFILE="age_1.ps"
PROJ="-JM6i"
LIMS="-R-40/10/-40/0"

gmt makecpt -I -T0/120/10 > age.cpt
gmt grdimage ocean_age.nc $PROJ $LIMS -Cage.cpt -K > $PSFILE
gmt psscale $PROJ $LIMS -Dg0/-45+w10c/0.5c+jTC+h -Bx10+l"Age" -Cage.cpt -K -O >> $PSFILE
gmt pscoast $PROJ $LIMS -Dl -W1p -N1/1p -K -O >> $PSFILE
gmt psbasemap $PROJ $LIMS -Bxa5 -Bya5 -BWeSn -O >> $PSFILE
gmt psconvert $PSFILE -Tg -A+m1c

# +l in psscale --> label