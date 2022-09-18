set title "resp"
set xlabel "clients"
set ylabel "resp"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "3may_resp.png" ; 
plot "g3may_resp.txt" using 1:2 title "resp" with linespoints lt rgb "blue";
set term x11
