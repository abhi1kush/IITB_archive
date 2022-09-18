set title " Utilization (%) vs No of clients"
set xlabel "No of Clients"
set ylabel "Utilization (%)"

set xtic auto
set ytic auto
set grid

set terminal png
set output "3rdmay_util.png" ; 
plot "gutil_client.txt" using 1:2 title "Utilization (%)" with linespoints lt rgb "blue";
set term x11
