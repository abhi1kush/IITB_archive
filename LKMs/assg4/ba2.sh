sudo rmmod assg4
sudo insmod assg4.ko
for i in {0..100}
do
sleep 5
cat /proc/my_proc_file2 | grep "*:" | cut -d" " -f 6,8,10,12 >>newrq2
done


