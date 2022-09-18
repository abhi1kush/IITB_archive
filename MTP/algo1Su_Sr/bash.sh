for f in `ls copy*.py`;
do
	python astpp_dump.py $f > tmp_astppdump.txt
	python new_parse_AST.py tmp_astppdump.txt > tmp_out 
	bsname=`echo $f| cut -d"." -f 1`
	bsname+="_with_Output.txt"
	cat $f tmp_out > $basename 
done

