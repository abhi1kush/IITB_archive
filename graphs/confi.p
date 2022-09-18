set title "Confidence interval of Response time vs No of Clients"
set xlabel "No of Clients"
set ylabel "Confidence interval of response time 95%"

set xtic auto
set ytic auto
set grid

set terminal png 
set output "confi.png" ; 
set style fill transparent solid 0.2 noborder
plot "gfinal_confi" using 1:2:3 title "Response time 95% confidence" with filledcurves lt rgb "blue";
set term x11
