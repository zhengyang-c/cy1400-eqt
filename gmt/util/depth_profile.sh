PROJ="-JM6i"
LIMS="-R95/96.75/4/6"

# LIMS=
# PROJ="-JOc96/5///15c"

#LIMS="-R-122.25/-122.24/37.87/37.89"

ETOP="/home/zy/gmt/etop/GMRTv3_9_20210325topo_61m.grd"
CPT="-C/home/zy/gmt/cpt/colombia.cpt"
#PLATE="/home/zy/gmt/plate/usgs2015_plates.xy"
PLATE="/home/zy/gmt/plate/sumatran_fault_ll.xy"

DEPCPT="-C/home/zy/gmt/cpt/dep.cpt"
STATION_FILE=/home/zy/cy1400-eqt/new_station_info.dat

#SOURCE_FILE=~/cy1400-eqt/real_postprocessing/hypoDD.reloc
#PSFILE=aceh_5jul_after
#
#

SOURCE_FILE=$1
PSFILE=$2

# SOURCE_FILE=~/cy1400-eqt/real_postprocessing/aug5_hypoDD_1.reloc
# PSFILE=aceh_7jul_after_dp


gmt makecpt -Crainbow -I -T0/40/5 -Z > temp.cpt

gmt begin $PSFILE ps
	gmt set PS_MEDIA A4
	gmt set FORMAT_GEO_MAP D


	cat <<- EOF > fault.txt
	96.5    4.5
	95.5    5.5
	EOF

	gmt subplot begin 2x1 -Fs15c/9c -M1c 
		gmt subplot set 0,0
		gmt basemap $PROJ $LIMS -BWeSn -Bxa0.2 -Bya0.2 -LjTC+c5+w20+f+o0/-1c+l[km]

		gmt grdimage $ETOP $PROJ $LIMS $CPT
		gmt plot $PROJ $LIMS -W2p,blue fault.txt
		gmt plot $PROJ $LIMS -Sc0.25c -Gblue fault.txt

		

		# PLOT STATIONS

		awk '{print $2,$3}' $STATION_FILE | gmt plot $PROJ $LIMS -Gwhite -St0.1i -W0.5p
		awk '{print $2,$3,$1}' $STATION_FILE | gmt text $PROJ $LIMS -F+f6p,0+jRB -D-0.2c/0

		# FAULT LINE
		gmt plot $PLATE $PROJ $LIMS -W1p

		# PROJECT
		awk '{print $3, $2, $4, $23 }' $SOURCE_FILE | gmt project -C95.5/5.5 -E96.5/4.5 -W-0.1/0.15 -L-2/4 > binned.txt
		
		#awk -F, '{printf "%.5f %.5f %.5f %.5f\n",$3,$2,$4,$6}' $SOURCE_FILE | gmt project -C95.5/5.5 -E96.5/4.5 -L-2/4 -W-0.2/0.2 > binned.txt
		# C: origin of projection
		# E: end of projection
		# W: width range
		# L: length range



		# PLOT EVENTS
		awk '{print $1, $2, $3}' binned.txt | gmt plot $PROJ $LIMS -Ctemp.cpt -Sc0.05i -W0.5p

		
		
		# gmt project: xyz --> pqrs, pq are coordinates of projection, (r,s) is the projeced position on the profile
		# q is distance from the profile, p is length along the profile
		# 
		# 
		


		gmt basemap $PROJ $LIMS -BWeSn -Bxg0.25 -Byg0.25
		gmt colorbar -Ctemp.cpt -Dg95.5/4.5+w5c/0.5c+jTC+h -Bx5+lDepth $PROJ $LIMS
		

		gmt subplot set 1,0 

		PROFILE_R="-R4/6/-40/0"
		PROFILE_J="-Jx-15c/0.25c"

		gmt basemap $PROFILE_J $PROFILE_R -BWS -Bxa0.1+l"Latitude (profile projection) [deg]" -By+l"Depth [km]"


		awk '{print $8, $3 * -1, $4 * 0.5}' binned.txt | gmt plot $PROFILE_J $PROFILE_R -Sci -W0.5p

		# the latitude of the projected position (on the line), the depth (negative), and then the rms


	gmt subplot end
gmt end

gmt psconvert ${PSFILE}.ps -Tg -A+m1c
gmt psconvert ${PSFILE}.ps -Tf -A+m1c
