set title "Drop rate (%) vs No of clients "
set xlabel "No of Clients"
set ylabel "Drop rate (%)"

set xtic auto
set ytic auto
set grid

set terminal png
set output "drop.png" ; 
plot "gdrop_client.txt" using 1:2 title "Drop rate %" with linespoints lt rgb "blue";
set term x11
