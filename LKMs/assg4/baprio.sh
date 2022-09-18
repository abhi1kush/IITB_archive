sudo rmmod assg4
sudo insmod assg4.ko
for i in {1..50}
do
sleep 1
cat /proc/my_proc_file2 >> prio
done


