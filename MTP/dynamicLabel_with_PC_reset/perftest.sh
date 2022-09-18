st=`date +%s`
for i in {1..1000..1}
do
	python dynamicPCreset.py $1 $2 > /dev/null
done
ft=`date +%s`
t=$(( $ft - $st))
echo $t

