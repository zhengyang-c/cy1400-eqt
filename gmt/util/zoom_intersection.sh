PROJ="-JM6i"
LIMS="-R95.75/96.25/4.75/5.25"
#
#

# LIMS=
# PROJ="-JOc96/5///15c"

#LIMS="-R-122.25/-122.24/37.87/37.89"

ETOP="/home/zy/gmt/etop/GMRTv3_9_20210325topo_61m.grd"
CPT="-C/home/zy/gmt/cpt/colombia.cpt"
#PLATE="/home/zy/gmt/plate/usgs2015_plates.xy"
PLATE="/home/zy/gmt/plate/sumatran_fault_ll.xy"

DEPCPT="-C/home/zy/gmt/cpt/dep.cpt"
STATION_FILE=/home/zy/cy1400-eqt/station_info.dat

#SOURCE_FILE=~/cy1400-eqt/real_postprocessing/hypoDD.reloc
SOURCE_FILE=~/cy1400-eqt/real_postprocessing/aug5_hypoDD_1.reloc
PSFILE=zoom_intersection_7jul



gmt makecpt -Cinferno -T0/35/5 -Z > temp.cpt

gmt begin $PSFILE ps
	gmt set PS_MEDIA A4
	gmt set FORMAT_GEO_MAP D


	cat <<- EOF > fault.txt
	96.5    4.5
	95.5    5.5
	EOF

	gmt subplot begin 2x1 -Fs15c/9c -M1c 
		gmt subplot set 0,0
		gmt basemap $PROJ $LIMS -BWESN -Bxa0.1 -Bya0.1

		gmt grdimage $ETOP $PROJ $LIMS $CPT
		gmt plot $PROJ $LIMS -W2p,blue fault.txt
		gmt plot $PROJ $LIMS -Sc0.25c -Gblue fault.txt

		awk '{print $3, $2, $4, $23 }' $SOURCE_FILE | gmt project -C95.5/5.5 -E96.5/4.5 -W-0.1/0.15 -L0/3 > binned.txt


		# gmt project: xyz --> pqrs, pq are coordinates of projection, (r,s) is the projeced position on the profile
		# q is distance from the profile, p is length along the profile
		# 
		# 
		
		awk '{print $1, $2, $3}' binned.txt | gmt plot $PROJ $LIMS -Ctemp.cpt -Sc0.05i -W0.5p

		# PLOT STATIONS

		awk '{print $2,$3}' $STATION_FILE | gmt plot $PROJ $LIMS -Gwhite -St0.1i -W0.5p
		awk '{print $2,$3,$1}' $STATION_FILE | gmt text $PROJ $LIMS -F+f6p,0+jRB -D-0.2c/0

		gmt basemap $PROJ $LIMS -Bxg0.05 -Byg0.05
		gmt colorbar -Ctemp.cpt -Dg95.9/4.8+w5c/0.5c+jTC+h -Baf $PROJ $LIMS
		
		gmt plot $PLATE $PROJ $LIMS -W1p
		


		gmt subplot set 1,0 

		PROFILE_R="-R4.75/5.25/-35/0"
		PROFILE_J="-Jx-30c/0.25c"

		gmt basemap $PROFILE_J $PROFILE_R -BWSen -Bxa0.1+l"Latitude (profile projection) [deg]" -By+l"Depth [km]"


		awk '{print $8, $3 * -1, $4 * 0.5}' binned.txt | gmt plot $PROFILE_J $PROFILE_R -Sci -W0.5p


	gmt subplot end
gmt end

gmt psconvert ${PSFILE}.ps -Tg -A+m1c
gmt psconvert ${PSFILE}.ps -Tf -A+m1c