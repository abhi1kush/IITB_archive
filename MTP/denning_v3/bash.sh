echo "
###################### step 2 output ##############################" > line2 
echo "
###################### step 1 output ##############################" > line1 
for f in `ls copy*.py`;
do
	python astpp_dump.py $f > tmp_astppdump.txt
	python new_parse_AST.py tmp_astppdump.txt > tmp_out2 
	python ~/PycharmProjects/denning/new_parse_AST.py  tmp_astppdump.txt > tmp_out1 
	filename=`echo $f| cut -d"." -f 1`
	filename+="_with_Output.txt"
	cat $f line2 tmp_out2 line1 tmp_out1 | tee "$filename"
done

rm line linee tmp_astppdump.txt tmp_out tmp_outt 
