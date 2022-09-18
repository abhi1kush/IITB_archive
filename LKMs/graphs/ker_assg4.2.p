set title "No ofContext Switches of a memory intensive process with core affinity"
set xlabel "Time sec"
set ylabel "NO of Context switches"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "memlast2.png" ; 
plot "lastg" using 1:2 title "cpu0" with linespoints lt rgb "blue","lastg" using 1:3 title "cpu1" with linespoints lt rgb "green","lastg" using 1:5 title "cpu3" with linespoints lt rgb "red";
set term x11
