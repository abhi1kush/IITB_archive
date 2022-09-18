set title "Throughput vs No of client"
set xlabel "No of clients"
set ylabel "Throughput"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "thr.png" ; 
plot "gthrough_client.txt" using 1:2 title "Goodput" with linespoints lt rgb "blue","gthrough_client.txt" using 1:3 title "Badput" with linespoints lt rgb "green","gthrough_client.txt" using 1:4 title "Througput" with linespoints lt rgb "black";
set term x11
