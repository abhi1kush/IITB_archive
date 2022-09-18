set title "Context Switches of particular pid"
set xlabel "Time"
set ylabel "NO of Context switches"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "pidcpucs.png" ; 
plot "pidcpucsg" using 1:2 title "cpu0" with linespoints lt rgb "blue","pidcpucsg" using 1:3 title "cpu1" with linespoints lt rgb "green","pidcpucsg" using 1:4 title "cpu2" with linespoints lt rgb "black","pidcpucsg" using 1:5 title "cpu3" with linespoints lt rgb "red","pidcpucsg" using 1:6 title "total" with linespoints lt rgb "purple";
set term x11
