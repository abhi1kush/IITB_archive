if [ -f response.txt ];then
	rm response.txt
fi
if [ -f through_out.txt ];then
	rm through_out.txt
fi
if [ -f temp.txt ];then
	rm temp.txt
fi
if [ -f gresponse.txt ];then
	rm gresponse.txt
fi
if [ -f drop_out.txt ];then
	rm drop_out.txt
fi
if [ -f util_out.txt ];then
	rm util_out.txt
fi
#######################
seed=10
#######################
for (( i=2; i<=$seed*2;i+=2 ))
do
	sed -i -r -e "s/[ \t]*seed[ \t]*[0-9()*+]+/seed $i/" sim_input.txt	
	python cs681.py > /dev/null
done
resp_mean=`cat response.txt | awk '{line += 1;sum += $1} END {print sum/line}'`

start=1
end=10
for (( c=$start;c<=$end;c++ ))
do
	echo $resp_mean
done >temp.txt
paste -d" " response.txt temp.txt > gresponse.txt
resp_var=`cat gresponse.txt | awk '{var+=($1-$2)*($1-$2);l+=1}END{print var/(l-1)}'`
echo `cat through_out.txt|awk '{good+=$1;bad+=$2;l+=1}END{print good/l,bad/l}'` >> through_client.txt
echo `cat drop_out.txt | awk '{sum+=$3;line+=1}END{print sum/line}'`>>drop_client.txt
echo $resp_mean $resp_var >> resp_client.txt
echo `cat util_out.txt | awk '{sum+=$1;line+=1}END{print sum/line}'`>>util_client.txt

