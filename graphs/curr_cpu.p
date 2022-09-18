set title "cpu mapping distribution of a memory intensive process"
set xlabel "time (ms)"
set ylabel "CPU id"

set xrange [0:10000]
set yrange [0:3]

set xtic 1000
set ytic 1
set grid

set terminal png 
set output "memcurr_cpu.png" ; 
plot "dem" using 1:2 title "cpu id" with linespoints lt rgb "red";
set term x11
