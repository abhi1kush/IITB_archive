for f in `ls astppdump*.txt`;
do
	python $1 $f > /dev/null 
done


