set title "Context Switches with priority:process 1 has nice value 20 & 2 has -20"
set xlabel "Time"
set ylabel "NO of Context switches"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "wopriosched.png" ; 
plot "prio1gg" using 1:2 title "cpu0" with linespoints lt rgb "blue","prio1gg" using 1:3 title "cpu1" with linespoints lt rgb "green","prio1gg" using 1:4 title "cpu2" with linespoints lt rgb "black","prio1gg" using 1:5 title "cpu3" with linespoints lt rgb "red","prio1gg" using 1:6 title "total" with linespoints lt rgb "purple";
set term x11
