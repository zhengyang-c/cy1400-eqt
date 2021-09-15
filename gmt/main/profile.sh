gmt set PS_MEDIA=A4
# E: 85 - 110
# N: -15 - 15

# variables
#PSFILE="sumatra_bin0.ps"
LIMS="-R"
PROJ="-JX6i/6i"
LIMS="-R50/350/-100/10"
ETOP="../etop/ETOPO1_Ice.grd"
CPT="-C../cpt/topo_custom.cpt"
PLATE="../plate/usgs2015_plates.xy"
SLAB="../slab/sum_slab2_dep_02.23.18.grd"
INSETLIM="-R97/105/-7/3"
INSETPROJ="-JM4i"

PROFILE="sumatra_1.binned/profile"
BINFILE="sumatra_1.binned/bin"
ROTATEDBINFILE="sumatra_1.binned/rotated/bin"


# BEGIN PROCESSING
# bin and rotate beachballs.
# then print profile endpoints
python3 ../xy_binning.py sumatra_1.xy sumatra_1.binned 5 100 0 103 -5
# 99 3.5 105 -5

# take profile endpoints and get points along them
for f in sumatra_1.binned/profile*.temp
do
	#echo $f
	cat $f | gmt sample1d -I0.1 > "${f%.temp}.xy"
done

#rm sumatra_1.binned/*.temp

#get bathymetry values at those points
# get slab values at those points and overwrite the .xy file 

for f in sumatra_1.binned/profile*.xy
do
	echo $f
	gmt grdtrack $f -G$SLAB > "${f%.xy}.axy"
	python3 ../rel_dist.py "${f%.xy}.axy" "${f%.xy}.bxy" 100 0 103 -5 5 $f
	gmt grdtrack $f -G$ETOP > "${f%.xy}.pretopxy"
	python3 ../rel_dist.py "${f%.xy}.pretopxy" "${f%.xy}.topxy" 100 0 103 -5 5 $f
done

#rm sumatra_1.binned/*.temp
# END PROCESSING

for f in {0..4}
do
	# plot slab
	gmt psxy "sumatra_1.binned/profile${f}.bxy" $LIMS $PROJ -V -K > "${PROFILE}${f}.ps"
	# plot bathymetry
	awk '{print $1, $2/1000}' "sumatra_1.binned/profile${f}.topxy" | gmt psxy $LIMS $PROJ -K -O >> "${PROFILE}${f}.ps"
	awk '{print $1 * 111.1, $2*-1, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12}' "${ROTATEDBINFILE}${f}.xy" | gmt psmeca $PROJ $LIMS -Sm0.2i -Z../cpt/dep.cpt -W0.5p -T -K -O >> "${PROFILE}${f}.ps"


	#inset shit idk
	gmt psbasemap $LIMS $PROJ -Bxa100+l"Distance (km)" -Bya20+l"Depth (km)" -BWeSn -K -O >> "${PROFILE}${f}.ps"

	gmt psbasemap $INSETLIM $INSETPROJ -X6.5i -Y0.5i -Bxa2 -Bya1 -BWeSn -K -O >> "${PROFILE}${f}.ps"
	gmt grdimage $ETOP $INSETPROJ $INSETLIM $CPT -K -O >> "${PROFILE}${f}.ps"
	gmt psxy "${PROFILE}${f}.xy" $INSETPROJ $INSETLIM -W1p -Cred -K -O >> "${PROFILE}${f}.ps"
	gmt psxy $PLATE $INSETPROJ $INSETLIM -V -W1p -Cred -K -O >> "${PROFILE}${f}.ps"
	awk '{print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12}' "${BINFILE}${f}.zxy" | gmt psmeca $INSETPROJ $INSETLIM -Sm0.1i -Z../cpt/dep.cpt -W0.5p -T -K -O>> "${PROFILE}${f}.ps"
	gmt grdcontour $SLAB $INSETPROJ $INSETLIM -C25 -W0.5p,grey50 -K -O >> "${PROFILE}${f}.ps"
	gmt grdcontour $SLAB $INSETPROJ $INSETLIM -C100 -W2p -A100 -Gd4c -K -O >> "${PROFILE}${f}.ps"
	gmt pscoast $INSETPROJ $INSETLIM -W1p -Di -N1/0.5p -A0/0/1 -O >> "${PROFILE}${f}.ps"

	# draw the map with the binned line
	gmt psconvert "${PROFILE}${f}.ps" -Tg -A+m1c
done
# kill me now

