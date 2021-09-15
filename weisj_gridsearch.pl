#!/usr/bin/perl

# Thickness         Vs                    Vp                  Density       Qs                    Qp

# 5.50       3.18      5.50      2.40    100.00    150.00

# 10.50      3.64      6.30      2.67    300.00    800.00

# 16.00      3.87      6.70      2.80    300.00    800.00

# 0.00       4.50      7.80      3.00    300.00    800.00

 
@p = `saclst t1 f *.HNZ`;

$min_lon = -122.33;

$max_lon = -122.25;

$min_lat = 38.17;

$max_lat = 38.25;

$dep     = 11;

$model_dir = "/net/titaia/nobackup/brecca_backup/shjwei/work/NoCal/2014_Mw6.0/graves/Profs1D";

for($lat=$min_lat;$lat<=$max_lat;$lat+=0.002){

  for($lon=$min_lon;$lon<=$max_lon;$lon+=0.002){

     open(SAC,"|sac >& saclog ") or die "can't open sac!\n";

       print SAC "r *HNZ\n";

       print SAC "ch evlo $lon\n ch evla $lat\n";

       print SAC "wh\nq\n";

     close(SAC);

     #@junk = `saclst dist t1 kstnm f *.HNZ`;

     @junk = `saclst dist t1 kstnm f NHC.HNZ 68150.HNZ VALB.HNZ N002.HNZ`;

     $err_all = 0;

     $index = 0;

     $weight_all = 0;

     foreach(@junk){

       (undef,$dist,$t1_data,$sta)=split; chomp($sta);

       @aaa = `/opt/seismo-util/bin/trav.pl p $model_dir/$sta\.1d\.fk $dep $dist`;

       die "no travel time available for $sta at $dist!\n" if @aaa < 1;

       (undef,$t1_syn,undef)=split(' ',$aaa[0]);

       $err[$index]=$t1_data - $t1_syn;

       # for relative relocation, one should find the calibration time shift from the table that is created by the calibration event

       $weight = 1/$dist;

       $err_all += $err[$index]*$weight;

       $index++;

       $weight_all+=$weight;

     }

     $dc = $err_all/$weight_all;

     $err_l1 = 0;

     $err_l2 = 0;

     #printf "dc=%8.4f  ",$dc;

     for($i=0;$i<@err;$i++){

        $err_l1 += abs($err[$i]-$dc);

     #   printf "%8.4f  ",$err[$i];

        $err_l2 += ($err[$i]-$dc)**2;

     }

     $err_l1/=$index;

     $err_l2=sqrt($err_l2/$index);

     printf "%9.4f %9.4f %9.4f %9.4f %9.4f\n",$lon,$lat,$dc,$err_l1,$err_l2;

   }

}