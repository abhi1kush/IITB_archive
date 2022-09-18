echo "
###################### step 2 output ##############################" > line 
echo "
###################### step 1 output ##############################" > linee 
for f in `ls copy*.py`;
do
	python astpp_dump.py $f > tmp_astppdump.txt
	python new_parse_AST.py tmp_astppdump.txt > tmp_out 
	python ~/PycharmProjects/denning/new_parse_AST.py  tmp_astppdump.txt > tmp_outt 
	filename=`echo $f| cut -d"." -f 1`
	filename+="_with_Output.txt"
	cat $f line tmp_out linee tmp_outt | tee "$filename"
done

