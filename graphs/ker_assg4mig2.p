set title "Load vs No of process migration across cpus"
set xlabel "Time sec (after each 50 second one cpu intensive process increases)"
set ylabel "NO of Migration"

set xtic 50

set grid

set terminal png 
set output "mig2.png" ; 
plot "migr2g" using 1:2 title "No of Migration" with linespoints lt rgb "blue";
set term x11
