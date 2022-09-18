set title "Distribution of RQ length over CPUs"
set xlabel "Time (0..505)secs"
set ylabel "Running Queue Length"

set xrange [0:510]
set yrange [0:7]

set ytics 1
set grid

set terminal png 
set output "rqlength2.png" ; 
plot "newrq2g" using 1:2 title "cpu0" with linespoints lt rgb "blue","newrq2g" using 1:3 title "cpu1" with linespoints lt rgb "green","newrq2g" using 1:4 title "cpu2" with linespoints lt rgb "black","newrq2g" using 1:5 title "cpu3" with linespoints lt rgb "red";
set term x11
