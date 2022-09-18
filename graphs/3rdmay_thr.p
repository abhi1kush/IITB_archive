set title "Throughput vs No of client"
set xlabel "No of clients"
set ylabel "Throughput"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "3rdmay_thr.png" ; 
plot "gthrough_client.txt" using 1:2 title "throughput" with linespoints lt rgb "blue";
set term x11
