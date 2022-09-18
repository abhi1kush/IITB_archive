st=`date +%s`
for i in {1..1000..1}
do
	bash run.sh dirty_new_parse_AST.py
done
ft=`date +%s`
t=$(( $ft - $st))
echo $t

