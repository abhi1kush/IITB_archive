count=0
for i in {0..10}
do
sudo rmmod assg4
sudo insmod assg4.ko
sleep 60
echo $count >>temp1
cat /proc/my_proc_file2 >> temp1
for j in {0..10}
do
((count++))
gnome-terminal -e "./a.out"
done
done


