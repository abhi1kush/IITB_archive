set title "Througput vs Time"
set xlabel "Time"
set ylabel "Througput"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "mclab3_thr.png" ; 
plot "thr.txt" using 1:2 title "Througput" with linespoints lt rgb "red";
set term x11
