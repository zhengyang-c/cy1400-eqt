gmt set PS_MEDIA=A2

PROJ="-JM6i"
LIMS="-R95/97/4/6"
PSFILE="stations.ps"
ETOP="../etop/GMRTv3_9_20210325topo_61m.grd"
CPT="-C../cpt/colombia.cpt"
PLATE="../plate/usgs2015_plates.xy"
SLAB="../slab/sum_slab2_dep_02.23.18.grd"

gmt pscoast $PROJ $LIMS -W1p -Df -N1/0.5p -A0/0/4 -Sblue -Ggreen -K > $PSFILE
gmt psbasemap $PROJ $LIMS -Bxa0.5 -Bya0.5 -BWeSn -K -O  --FORMAT_GEO_MAP=D>> $PSFILE
gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE
gmt grdimage $ETOP $PROJ $LIMS $CPT -K -O >> $PSFILE
gmt grdcontour $SLAB $PROJ $LIMS -C10 -W0.5p,grey50 -K -O >> $PSFILE
gmt grdcontour $SLAB $PROJ $LIMS -C50 -W2p -A100 -Gd4c -K -O >> $PSFILE
awk '{print $2, $3}' station_info.dat | gmt psxy $PROJ $LIMS -St0.2i -W0.25p -Gred -O >> $PSFILE
#awk '{print $2, $3, $1}' station_info.dat | gmt pstext $PROJ $LIMS -D0.5i/0 -O >> $PSFILE

gmt psconvert $PSFILE -Tg -A+m1c

# gmt set PS_MEDIA=A2

# PROJ="-JM6i"
# LIMS="-R95.9/95.95/5/5.07"
# PSFILE="TA01-TA19.ps"
# ETOP="../etop/ETOPO1_Ice.grd"
# CPT="-C../cpt/topo2.cpt"
# PLATE="../plate/usgs2015_plates.xy"

# gmt pscoast $PROJ $LIMS -W1p -Df -N1/0.5p -A0/0/4 -Sblue -Ggreen -K > $PSFILE
# gmt psbasemap $PROJ $LIMS -Bxa0.05 -Bya0.01 -BWeSn -K -O  >> $PSFILE
# gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE
# #gmt grdimage $ETOP $PROJ $LIMS $CPT -K -O >> $PSFILE
# awk '{print $2, $3}' station_info.dat | gmt psxy $PROJ $LIMS -St0.3i -W0.25p -Gred -K -O >> $PSFILE
# awk '{print $2, $3, $1}' station_info.dat | gmt pstext $PROJ $LIMS -D0.5i/0 -O >> $PSFILE

# gmt psconvert $PSFILE -Tg -A+m1c
