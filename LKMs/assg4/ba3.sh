sudo rmmod assg4 
sudo insmod assg4.ko pid=$1
for i in {1..1000}
do
if (( $i % 10 == 0 )); then
	gnome-terminal -e "./a.out"
fi
cat /proc/my_proc_file2 | grep "@@" | cut -d" " -f 3  >>migr3
done


