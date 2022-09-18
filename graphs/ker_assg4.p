set title "Load vs Context Switches"
set xlabel "Load: No. of CPU intensive processes"
set ylabel "NO of Context switches"

set xtic auto
set ytic auto
set grid

set terminal pdf 
set output "loadvscs.pdf" ; 
plot "sched_counterg" using 1:2 title "cpu0" with linespoints lt rgb "blue","sched_counterg" using 1:3 title "cpu1" with linespoints lt rgb "green","sched_counterg" using 1:4 title "cpu2" with linespoints lt rgb "black","sched_counterg" using 1:5 title "cpu3" with linespoints lt rgb "red","sched_counterg" using 1:6 title "total" with linespoints lt rgb "purple";
set term x11
