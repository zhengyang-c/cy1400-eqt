# set bigger for stonks and then constrain it
gmt set PS_MEDIA=A2

# variables
PROJ="-JM6i"
LIMS="-R135/145/33/44"
PSFILE="japan2011.ps"
ETOP="../etop/ETOPO1_Ice.grd"
CPT="-C../cpt/topo2.cpt"

gmt pscoast $PROJ $LIMS -W1p -A0/0/1 -Di -K > $PSFILE
awk '{print $1, $2, $3, $4 * 0.75}' tohoku2011.dat | gmt psxy $PROJ $LIMS -SV6p+jb+e+a40+n0.12 -W1p,blue -Gblue -K -O >> $PSFILE

# add a scale:
echo 143 34 90 1.50 | gmt psxy $PROJ $LIMS -SV6p+jb+e+a40+n0.12 -W1p,blue -Gblue -K -O >> $PSFILE
echo 143 34 12,0,blue LB 2 m | gmt pstext $PROJ $LIMS -F+f+j -D0/0.1i -N -K -O >> $PSFILE

gmt psbasemap $PROJ $LIMS -Bxa2 -Bya2 -BWeSn -O >> $PSFILE
# format: lat lon angle magnitude
# SV: vectors
# 6p: thickness
# +jb starts at the point , "justified beginnign"
# +e: draw the thing 
# +a40: angle of arrow
# +n0.12: scale down stuff smaller than 0.12
# colour the thing with -G




# SV: counterclockwise from x-axis
# Sv: clockwise from x-axis



gmt psconvert $PSFILE -Tg -A+m1c