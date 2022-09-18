rm pidmemcs
sudo rmmod assg4
sudo insmod assg4.ko pid=$1
for i in {1..200}
do
sleep 1
cat /proc/my_proc_file | grep "1pid" | cut -d" " -f 2,4,6,8,10 >> pidaffcpucs
done 
