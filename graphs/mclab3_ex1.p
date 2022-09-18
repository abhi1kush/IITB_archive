set title "Routing Overhead vs Time"
set xlabel "Time"
set ylabel "No of Routing message exchanged"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "mclab3_ex1.png" ; 
plot "ex1.txt" using 1:2 title "No. of Routing Msg" with linespoints lt rgb "red";
set term x11
