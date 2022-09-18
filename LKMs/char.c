#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/mutex.h>
#include <linux/kfifo.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/sched.h>
#include <linux/tty.h>
#include <linux/init.h>
#include <linux/string.h>
#include <linux/module.h>
#include <linux/fs.h> 
#include <asm/uaccess.h>
#include <linux/cdev.h>
#include <linux/semaphore.h>
#include <linux/spinlock.h>

#define FIFO_SIZE      4096
#define FIFO_TYPE char


struct semaphore sem,s;

static DEFINE_KFIFO(c_queue,FIFO_TYPE,FIFO_SIZE);

static int proc_readings(struct seq_file *, void *);
void consumer(char * );
int proc_open(struct inode *, struct file *);

int ret,buffer_count=0;
char data[50],stat[50];
int pos;
int major_number;
int read_count =0, write_count =0;
long unsigned int queue_head=(long unsigned int) &c_queue;
long unsigned int initial_head_pos = (long unsigned int) &c_queue;
struct proc_dir_entry *assi3_proc_file;

struct file_operations proc_file_operations ={
	.owner = THIS_MODULE,
	.open = proc_open,
	.read = seq_read,
	.release = single_release
};

int proc_open(struct inode *pinode, struct file *pfile)
{
	return single_open(pfile,proc_readings,NULL);
}

void consumer(char * buffer)
{
   char data_to_user[1];
   if(down_interruptible(&s)!=0)
   {
	printk(KERN_ALERT"ERROR: not able to acquire lock in consumer function");
   }
   if(kfifo_is_empty(&c_queue))
   {
   	printk(KERN_ALERT"cqueue underflow");
	return ;
   }
   while (kfifo_out(&c_queue, data_to_user,1)) 
   {
	   //console_output(data_to_user);
	   ret =put_user(data_to_user[0],buffer++);//copy_to_user(buffer,data_to_user,buffer_count);
	   if(ret<0)
	   {
	   	printk(KERN_ALERT"ERROR : unable to copy to user");
	   }
	   if(queue_head - initial_head_pos >= 4095)
		   queue_head = initial_head_pos;
	   else
		   queue_head--;
   }
   up(&s);
}


ssize_t char_read(struct file *pfile, char __user *buffer, size_t length, loff_t *offset)
{
	printk(KERN_INFO "READING FROM KERNEL USING CHAR DEVICE\n");
	consumer(buffer);
	write_count++;
	return 0;

}
ssize_t char_write(struct file *pfile, const char __user *buffer, size_t length, loff_t *offset)
{	
	int i=0;
	memset(data,0,50);
	printk(KERN_INFO "WRITING TO DEVICE\n");
	while(length-- > 0)
	{
		data[i]=buffer[i];
		i++;
	}
	/**************************************/
	if(down_interruptible(&s)!=0)
	{
		printk(KERN_ALERT"ERROR: not able to acquire lock in producer function");
	}
	ret=kfifo_in(&c_queue,data,strlen(data));
	if(ret<0)
	printk("Error insertion in c_queue is not successful ");
	//kfifo_in(&c_queue,task->comm, 5);
	read_count++;
	
	if(queue_head - initial_head_pos >= 4095)
		queue_head = initial_head_pos;
	else
		queue_head+=strlen(data);
	up(&s);
	/*************************************/
	return 0;

}

int char_open(struct inode *pinode, struct file *pfile)
{ 	
	if(down_interruptible(&sem)!=0)
	{
		printk(KERN_ALERT"ERROR: NOT ABLE TO OPEN DEVICE");
	}
	printk(KERN_INFO "DEVICE OPENED SUCCESSFULY");
	return 0;
}

int char_release(struct inode *pinode, struct file *pfile)
{
	printk(KERN_INFO "inside the char_release function\n");
	return 0;

}

int char_close(struct inode *pinode,struct file *pfile)
{	
	up(&sem);
	printk(KERN_INFO "DEVICE CLOSED\n");
	return 0;

}

/****** file operations to be performed on devic *******/
struct file_operations char_file_operations ={
	.owner= THIS_MODULE,
	.open = char_open,
	.read = char_read,
	.write = char_write,
	.release = char_close
};

static int proc_readings(struct seq_file * sfile, void * any)
{
	seq_printf(sfile,"No of Reads: %d\nNo of Writes: %d\n Queue_head x0%lu\n",read_count,write_count,queue_head);
	return 0;
}

static int init(void)
{
	sema_init(&sem,1);
	sema_init(&s,1);
	memset(data,0,50);
	assi3_proc_file = proc_create("my_proc_file",0,NULL,&proc_file_operations);
	if(assi3_proc_file == NULL)
	{
		proc_remove(assi3_proc_file);
		printk(KERN_ALERT"ERROR : failed to create /proc/my_proc_file \n");
		return -1;
	}
	read_count=0;
	write_count=0;
	//printk("No of Writes : %d\n No of Reads : %d\n",write_count,read_count);
	printk(KERN_INFO"proc entry created \n");	
	ret=register_chrdev(0,"my_char_device",&char_file_operations);
	printk(KERN_INFO"major_number %d\n",ret);
	printk(KERN_INFO "make node using : \"mknod /dev/my_char_device c %d 0\" for device file",ret);
	return 0;
}

static void cleanup(void)
{
	unregister_chrdev(major_number,"my_char_device");
	proc_remove(assi3_proc_file);
}

module_init(init);
module_exit(cleanup);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("abhishek");
