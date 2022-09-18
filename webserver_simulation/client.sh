if [ -f resp_client.txt ];then
	rm resp_client.txt
fi
if [ -f through_client.txt ];then
	rm through_client.txt
fi
if [ -f drop_client.txt ];then
	rm drop_client.txt
fi
if [ -f util_client.txt ];then
	rm util_client.txt
fi
for i in  {100..2000..100}
do
	sed -i -r -e "s/[ \t]*no_of_clients[ \t]*[0-9()*+]+/no_of_clients $i/" sim_input.txt	
	bash bash.sh 
	echo $i
done

#####calculating confidence interval #################
cat resp_client.txt | awk '{print $1-1.55*sqrt($2/10),$1+1.55*sqrt($2/10)}'
