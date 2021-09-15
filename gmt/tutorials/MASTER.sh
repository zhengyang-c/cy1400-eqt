# set bigger for stonks and then constrain it
gmt set PS_MEDIA=A2

# variables
PROJ="-JM6i"
LIMS="-R80/110/0/35"
PSFILE="earthquake.ps"
ETOP="../etop/ETOPO1_Ice.grd"
CPT="-C../cpt/topo2.cpt"
PLATE="../plate/usgs2015_plates.xy"


# makecpt: make colour table
#gmt makecpt -I -T0/120/10 > age.cpt

# INTERPOLATION to make contours/ surfaces
#gmt surface eq_gps.dat $LIMS -I0.02 -Gdisp.grd 


#xyz2grd:

# xyz2grd temperature.xyz –Gtemps.grd –R0/360/-90/90 –I1/1
# -G: output
# input file (temperature: )
# - lat / lon / time
# -I : spacing between x and y grid points



#pscoast 
gmt pscoast $PROJ $LIMS -W1p -Di -N1/0.5p -A0/0/1 -K > $PSFILE
#D: resolution
#N: 1: national 2: state boundary in usa 3: marine boundaries a: all
#A: specific parts of the coastlines, 1 is for top level (only ocean/land boundary)

# pscoast with clipped .grd wtih grdimage
# START CLIP
gmt pscoast -JM5i -R138/144/35/42 -Di -Gc -K -O >> gps_1.ps 
#Gc: clipping mask, need start and end
gmt grdimage disp.grd -JM5i -R138/144/35/42 -C../cpt/disp.cpt -K -O >> gps_1.ps
gmt pscoast -Q -K -O >> gps_1.ps # -Q ends sthe clipping

#grd image
gmt grdimage $ETOP $PROJ $LIMS $CPT -K -O >> $PSFILE

#USGS plate boundaries
gmt psxy $PLATE $PROJ $LIMS -W1p -K -O >> $PSFILE

#scale
gmt psscale $PROJ $LIMS -Dg85/3+w5c/0.5c+jTC+h -Bx100+l"title" -Crainbow.cpt -K -O >> $PSFILE


# psxy: plotting xy points
awk '{print $2, $3,$5*$5*$5/3000} ' gcmt.dat | gmt psxy $PROJ $LIMS -W0.5p -Sci -Gred -K -O >> $PSFILE
gmt psxy stars.xy $PROJ $LIMS -Sa0.3i -W0.25p -Gred -K -O >> $PSFILE
gmt psxy eqs1.xy $PROJ $LIMS -Sci -W0.5p -Crainbow.cpt -O >> $PSFILE
# S: symbols, Sa star, sc circle, S*i : convert values to suitable sizes, 4th column? :). colour: 3rd column it seems?
# -C: 3rd column (depth)
# -S: 4th column (size)


# plot with (strike dip rake)
#gmt psmeca fiji_mec.dat $PROJ $LIMS -Sa0.2i -Zdep.cpt -W0.5p -K -O >> $PSFILE
# plot with moment tensor 
gmt psmeca fiji_mt.dat $PROJ $LIMS -Sm0.2i -Zdep.cpt -W0.5p -T -K -O >> $PSFILE
#note the -Sm. the differences in the beachball represents deviations from the simple fault-slip source
# -T: fault plane
# -Z: colour the compressive parts of the beachball, usually with depth


# psxy vectors:

awk '{print $1, $2, $3, $4 * 0.75}' tohoku2011.dat | gmt psxy $PROJ $LIMS -SV6p+jb+e+a40+n0.12 -W1p,blue -Gblue -K -O >> $PSFILE

# format: lat lon angle magnitude
# SV: vectors
# 6p: thickness
# +jb starts at the point , "justified beginnign"
# +e: draw the thing 
# +a40: angle of arrow
# +n0.12: scale down stuff smaller than 0.12
# colour the thing with -G

# add a vector scale:
echo 143 34 90 1.50 | gmt psxy $PROJ $LIMS -SV6p+jb+e+a40+n0.12 -W1p,blue -Gblue -K -O >> $PSFILE
echo 143 34 12,0,blue LB 2 m | gmt pstext $PROJ $LIMS -F+f+j -D0/0.1i -N -K -O >> $PSFILE



# basemap
gmt psbasemap $PROJ $LIMS -Bxa2 -Bya2 -BWeSn -O >> $PSFILE
gmt psbasemap $PROJ $LIMS -Bxa10g10 -Bya5g5 -BWeSn -K -O >> $PSFILE



# pstext
awk '{print $2,$3,"16,0", "RM", substr($1,1,4), $5' gcmt.dat | gmt pstext $PROJ $LIMS -F+f+j -K -O -D-0.12i/0i >> $PSFILE
# -F+f+j: flag, font, justification. rm == right-middle justified
# -D: shift text
# -N: do NOT clip

# plot contour lines: plot multiple for stonks
gmt grdcontour sam_slab.grd $PROJ $LIMS -C25 -W0.5p,grey50 -K -O >> $PSFILE
gmt grdcontour sam_slab.grd $PROJ $LIMS -C100 -W2p -A100 -Gd4c -K -O >> $PSFILE
# C:
# A: 
# G: 


gmt psconvert $PSFILE -Tg -A+m1c
# -Tg: png.
# -Tgf for png + pdf
# -A: tight, then 1 cm boundary