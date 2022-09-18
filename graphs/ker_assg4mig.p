set title "Load vs No of migration of a process with nice value 20 across cpus"
set xlabel "Time sec (load increasing per 10 second)"
set ylabel "NO of Migration"

set xtic 100
set ytic 1
set grid

set terminal png 
set output "miglow.png" ; 
plot "migrlowg" using 1:2 title "No of Migration" with linespoints lt rgb "blue";
set term x11
