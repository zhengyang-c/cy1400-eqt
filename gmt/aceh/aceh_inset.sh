gmt set PS_MEDIA=A2

PROJ="-JM6i"
LIMS="-R95/96.5/4/6"
PSFILE="station_inset.ps"
ETOP="../etop/GMRTv3_9_20210325topo_61m.grd"
CPT="-C../cpt/colombia.cpt"
PLATE="../plate/usgs2015_plates.xy"
SLAB="../slab/sum_slab2_dep_02.23.18.grd"

gmt pscoast $PROJ $LIMS -W1p -Df -N1/0.5p -A0/0/4 -Sblue -Ggreen -K > $PSFILE
gmt psbasemap $PROJ $LIMS -Bxa0.5 -Bya0.25 -BWeSn -K -O --FORMAT_GEO_MAP=D>> $PSFILE
gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE
gmt grdimage $ETOP $PROJ $LIMS $CPT -K -O >> $PSFILE
gmt grdcontour $SLAB $PROJ $LIMS -C10 -W0.5p,grey50 -K -O >> $PSFILE
gmt grdcontour $SLAB $PROJ $LIMS -C50 -W2p -A100 -Gd4c -K -O >> $PSFILE
awk '{print $2, $3}' station_info.dat | gmt psxy $PROJ $LIMS -St0.12i -W0.25p -Gred -I0.5 -K -O >> $PSFILE

gmt psscale $PROJ $LIMS -Dg95.75/4.20+w10c/0.5c+jTC+h -G-4000/4000 -Bx2000+l"Elevation" $CPT --LABEL_FONT_SIZE=14 -K -O >> $PSFILE

# inset box in blue and draw lines
printf "95.9 5\n95.95 5\n95.95 5.05\n95.9 5.05\n95.9 5" | gmt psxy $PROJ $LIMS -W3p,blue -K -O >>$PSFILE
printf "95.9 5.05\n96 6" | gmt psxy $PROJ $LIMS -W3p,blue -K -O >>$PSFILE
printf "95.95 5.0\n96.5 5.25" | gmt psxy $PROJ $LIMS -W3p,blue -K -O >>$PSFILE

INSETPROJ=-JX2i/3i
INSETLIMS=-R95.9/95.95/5/5.05
INSETPOS='-X4i -Y5i'
gmt psbasemap $INSETPROJ $INSETLIMS -K -O -Bxa0.02 -Bya0.02 -BWeSn --FORMAT_GEO_MAP=D $INSETPOS>>$PSFILE
gmt grdimage $ETOP $INSETPROJ $INSETLIMS $CPT -K -O >> $PSFILE
gmt grdcontour $SLAB $INSETPROJ $INSETLIMS -C10 -W0.5p,grey50 -K -O >> $PSFILE
gmt grdcontour $SLAB $INSETPROJ $INSETLIMS -C50 -W2p -A100 -Gd4c -K -O>> $PSFILE



awk '//{print $2, $3}' station_info.dat | gmt psxy $INSETPROJ $INSETLIMS -St0.15i -W0.25p -Gred -I0.5 -K -O>> $PSFILE
awk '/TA19/{print $2, $3}' station_info.dat | gmt psxy $INSETPROJ $INSETLIMS -St0.15i -W0.25p -Gred -K -O>> $PSFILE
awk '/TA19/{print $2, $3, $1}' station_info.dat | gmt pstext $INSETPROJ $INSETLIMS -D0.3i/0 -O>> $PSFILE
#awk '{print $2, $3, $1}' station_info.dat | gmt pstext $PROJ $LIMS -D0.5i/0 -O >> $PSFILE


# psbasemap -JM5i -Rminlon/maxlon/minlat/maxlat -K -P -B > psfile

#psbasemap -JX2i/3i -Rminx/maxx/miny/maxy -K -O -P -B  >> psfile

gmt psconvert $PSFILE -Tf -A+m1c