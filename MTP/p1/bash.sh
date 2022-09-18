echo "
####################################################" > line
for f in `ls copy*.py`;
do
	python ~/Dropbox/pythoncode/ast.dump\(\).py $f > tmp_astppdump.txt
	filename=`echo $f| cut -d"." -f 1`
	lb="label"$filename".txt"
	filename+="_with_Output.txt"
	python $1 tmp_astppdump.txt $lb > tmp_out 
	printf "\n------------- next file ----------------\n"
	cat $f line tmp_out | tee "$filename"
done

rm line tmp_astppdump.txt tmp_out 
