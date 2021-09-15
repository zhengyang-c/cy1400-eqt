#!/usr/bin/perl -w
# compute p/s arrival time from a velocity model

@ARGV > 2 or die "Usage: trav.pl [p | s]  model_file source_depth distances\n";

($ps, $model, $s_depth, @dist) = @ARGV;

#$r0=6371.;	# radius of the earth, set it to a big number if
		# no earth flattening wanted
$r0=10000000;
$sss = $r0-$s_depth;
$r = $r0;

open(MODEL,"< $model") or die "could not open $model\n";

for ($i=0;<MODEL>;$i++) {
   ($hh, $ss, $kk) = split;
   $kk = $kk*$ss if $kk < 1.5;
   $ss = $kk if $ps eq "p";
   $r -= $hh;
   $flat = $r0/($r + 0.5*$hh);
   $th[$i] = $hh*$flat;
   $v[$i] = $ss*$flat;
   $dd = $flat*($sss-$r);
   if ($dd > 0.) {
      $th[$i] -= $dd;
      $i++;
      $th[$i] = $dd;
      $v[$i] = $v[$i-1];
      $sss = 0;
      $iss=$i;
   }
}
close(MODEL);

#open(REFL,"|/opt/seismo-util/source/fk1.0/trav 2> /home/shjwei/null")
open(REFL,"| /home/zy/fk/trav 2> /dev/null")
  or die "couldn't run trav\n";
printf REFL "$i $iss 0\n";
for ($j=0;$j<$i;$j++) {
   printf REFL "%11.4f %11.4f\n",$th[$j],$v[$j];
}
printf REFL "%d\n",$#dist + 1;
foreach $ddd (@dist) {
    printf REFL "%10.4f\n",$ddd;
}
close(REFL);


exit(0);
