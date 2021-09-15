#gmt surface eq_gps.dat -R138/144/35/42 -I0.02 -Gdisp.grd # i: for 

gmt psbasemap -JM5i -R138/144/35/42 -Bxa1 -Bya1 -BWesN -K > gps_1.ps
#gmt psxy eq_gps.dat -JM5i -R138/144/35/42 -Sc0.1i -W0.5p -C../cpt/disp.cpt -K -O >> gps_0.ps  
# interpolation. create .grd file 
gmt psscale -JM5i -R138/144/35/42 -Dg143.5/38.2+w8c/0.5c+jTC+m -Bx1+l"Hor. Displacement (m)" -C../cpt/disp.cpt -K -O >> gps_1.ps
gmt pscoast -JM5i -R138/144/35/42 -N1/0.5p -W1p -K -O -Di >> gps_1.ps
gmt pscoast -JM5i -R138/144/35/42 -Di -Gc -K -O >> gps_1.ps 
#Gc: clipping mask, need start and end
gmt grdimage disp.grd -JM5i -R138/144/35/42 -C../cpt/disp.cpt -K -O >> gps_1.ps
gmt pscoast -Q -K -O >> gps_1.ps # -Q ends sthe clipping
gmt psxy japan.xy -JM5i -R138/144/35/42 -Sa0.3i -W0.25p -Gred  -O >> gps_1.ps
gmt psconvert gps_1.ps -Tg -A+m2c