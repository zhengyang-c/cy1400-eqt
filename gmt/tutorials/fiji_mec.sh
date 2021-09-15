gmt set PS_MEDIA=A4

# variables
PROJ="-JM9i"
LIMS="-R160/190/-25/-10"
PSFILE="fiji_mec.ps"
ETOP="../etop/ETOPO1_Ice.grd"
CPT1="../cpt/dep.cpt"
CPT2="-C../cpt/topo2.cpt"
PLATE="../plate/usgs2015_plates.xy"

gmt makecpt -T0/200/1 -Cmagma -D -I > $CPT1


gmt pscoast $PROJ $LIMS -W1p -Di -N1/0.5p -A0/0/1 -K > $PSFILE
gmt grdimage $ETOP $PROJ $LIMS $CPT2 -K -O >> $PSFILE

#USGS plate boundaries
gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE

# plot with (strike dip rake)
#gmt psmeca fiji_mec.dat $PROJ $LIMS -Sa0.2i -Zdep.cpt -W0.5p -K -O >> $PSFILE
# plot with moment tensor 
gmt psmeca fiji_mt.dat $PROJ $LIMS -Sm0.2i -Z$CPT1 -W0.5p -T -K -O >> $PSFILE
#note the -Sm. the differences in the beachball represents deviations from the simple fault-slip source
# -T: fault plane
# -Z: colour the compressive parts of the beachball, usually with depth

gmt psbasemap $PROJ $LIMS -Bxa5 -Bya5 -BWeSn -O >> $PSFILE
gmt psconvert $PSFILE -Tg -A+m1c