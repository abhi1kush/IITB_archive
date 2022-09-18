set title "Window size vs Time"
set xlabel "Time"
set ylabel "Window size"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "mclab3_win.png" ; 
plot "win.tr" using 1:2 title "window size" with linespoints lt rgb "blue";
set term x11
