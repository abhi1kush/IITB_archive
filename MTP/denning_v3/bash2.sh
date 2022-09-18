for f in `ls copy*.py`;
do
	python astpp_dump.py $f > tmp_astppdump.txt
	python new_parse_AST.py tmp_astppdump.txt > tmp_out
	no=`cat tmp_out | wc -l`
	sed -i "1i$no" tmp_out
	filename=`echo $f| cut -d"." -f 1`
	filename+="_constraints.txt"
	cat tmp_out | tee "$filename"
done

rm tmp_astppdump.txt tmp_out
