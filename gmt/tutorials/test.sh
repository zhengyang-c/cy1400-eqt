#!/bin/sh
#gmt psbasemap -JM10c -R80/110/0/35 -Bxa10g10 -Bya5g5 -BWesN -P > map1e.ps
#gmt psconvert map1e.ps -Tg -A
#gmt coast -R19.42/22.95/59.71/60.56 -JM6i -W0.1p,black -Gdarkseagreen2 -Scornflowerblue -png archi_sea
gmt pscoast -JM10c -R80/110/0/35 -W1p -K -L87/3+c3+w1000k+u -G255/255/0 -S50/100/255 -N1/0.25p > map2a.ps
gmt psbasemap -JM10c -R80/110/0/35 -Bxa10g10 -Bya5g5 -BWesN -O >> map2a.ps
gmt psconvert map2a.ps -Tg -A