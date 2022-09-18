sudo rmmod assg4
sudo insmod assg4.ko pid=$1
for i in {1..10000}
do
cat /proc/my_proc_file | grep "curr_cpu" | cut -d" " -f 2 >> memcurr_cpu
done
