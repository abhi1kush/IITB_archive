set title "No of Context Switch of a cpu intensive process with core affinity"
set xlabel "time sec"
set ylabel "No of context switch"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "csaff.png" ; 
plot "dem1g" using 1:2 title "cpu id" with linespoints lt rgb "red";
set term x11
