gmt set PS_MEDIA=A2
# E: 85 - 110
# N: -15 - 15

#profile start/end
#r_i = np.array([95, 10] )
#r_f = np.array([110, -5])

# variables
PROJ="-JM6i"
LIMS="-R88/110/-15/15"
PSFILE="sumatra_slab_test2.ps"
ETOP="../etop/ETOPO1_Ice.grd"
CPT="-C../cpt/topo_custom.cpt"
PLATE="../plate/usgs2015_plates.xy"
SLAB="../slab/sum_slab2_dep_02.23.18.grd"

gmt pscoast $PROJ $LIMS -W1p -Di -N1/0.5p -A0/0/1 -K > $PSFILE
gmt grdimage $ETOP $PROJ $LIMS $CPT -K -O >> $PSFILE

gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE

# plot slab

gmt grdcontour $SLAB $PROJ $LIMS -C25 -W0.5p,grey50 -K -O >> $PSFILE
gmt grdcontour $SLAB $PROJ $LIMS -C100 -W2p -A100 -Gd4c -K -O >> $PSFILE

gmt psscale $PROJ $LIMS -Dg109/-12.5+w5c/0.2c+jTR+h -Bx40+l"Depth" -C../cpt/dep.cpt --LABEL_FONT_SIZE=12 -K -O >> $PSFILE

# psmeca
awk '{print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10}' sumatra_test_rotated.xy | gmt psmeca $PROJ $LIMS -Sm0.2i -Z../cpt/dep.cpt -W0.5p -K -O >> $PSFILE
#awk '{print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10}' sumatra_test_rotated.xy | gmt psmeca $PROJ $LIMS -Sm0.2i -Z../cpt/dep.cpt -W0.5p -K -O >> $PSFILE

#awk '{print $1,$2,$3,$4*$4*$4/3000}' 1976_2020_sumatra_M6.xy | gmt psxy $PROJ $LIMS -Sci -W0.5p -C../cpt/dep.cpt -K -O >> $PSFILE

gmt psbasemap $PROJ $LIMS -Bxa5 -Bya5 -BWeSn -O >> $PSFILE
gmt psconvert $PSFILE -Tg -A+m1c