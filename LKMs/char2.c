#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/mutex.h>
#include <linux/kfifo.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/sched.h>
#include <linux/tty.h>
#include <linux/init.h>
#include <linux/string.h>
#include <linux/module.h>
#include <linux/fs.h> /*For the character device driver support */
#include <asm/uaccess.h>
#include <linux/cdev.h>
#include <linux/semaphore.h>
#include <linux/spinlock.h>

#define FIFO_SIZE      4096
#define PROC_FIFO "int-fifo"
#define FIFO_TYPE char


struct semaphore sem,s;

static DEFINE_KFIFO(c_queue,FIFO_TYPE,FIFO_SIZE);
static void console_output(char *);

int ret,buffer_count=0;
char data[50];
int major_number;
dev_t device_number;

int producer(char data[50])
{
	if(down_interruptible(&s)!=0)
	{
		printk(KERN_ALERT"ERROR: not able to acquire lock in producer function");
	}
	kfifo_in(&c_queue,data,1);
	//kfifo_in(&c_queue,task->comm, 5);
	up(&s);
   	return 0;
}

void consumer(char * buffer)
{
   char data_to_user[50];
   if(down_interruptible(&s)!=0)
   {
	printk(KERN_ALERT"ERROR: not able to acquire lock in consumer function");
   }
   while (kfifo_out(&c_queue, data_to_user,1)) 
   {
	   console_output(data_to_user);
	   ret =put_user(data_to_user,buffer);//copy_to_user(buffer,data_to_user,buffer_count);
	   if(ret<0)
	   {
	   	console_output("ERROR : unable to copy to user");
	   }
   }
   up(&s);
}


ssize_t char_read(struct file *pfile, char __user *buffer, size_t length, loff_t *offset)
{
	printk(KERN_INFO "READING FROM KERNEL USING CHAR DEVICE\n");
	consumer(buffer);
	return 0;

}
ssize_t char_write(struct file *pfile, const char __user *buffer, size_t length, loff_t *offset)
{	
	char data_from_user;
	printk(KERN_INFO "WRITING TO DEVICE\n");
	get_user(data_from_user,buffer);
	if(down_interruptible(&s)!=0)
	{
		printk(KERN_ALERT"ERROR: not able to acquire lock in producer function");
	}
	kfifo_in(&c_queue,data_from_user,1);
	//kfifo_in(&c_queue,task->comm, 5);
	up(&s);
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
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	return 0;

}
int char_close(struct inode *pinode,struct file *pfile)
{	
	up(&sem);
	printk(KERN_INFO "DEVICE CLOSED\n");
	return 0;

}

/*to hold file operations to be performed on devic*/
struct file_operations char_file_operations ={
	.owner= THIS_MODULE,
	.open = char_open,
	.read = char_read,
	.write = char_write,
	.release = char_close
};

static void console_output(char *str) 
{
	struct tty_struct *tty;
	tty = get_current_tty();
	if(tty != NULL) 
	{ 
		(tty->driver->ops->write) (tty, str, strlen(str));
    	}

    else
        printk("tty is NULL ");
}

static int init(void)
{
	/*ret = alloc_chrdev_region(&device_number,0,1,"my_char_device");
	if(ret<0)
	{
		printk(KERN_INFO"ERROR: failed to allocate no.");
		return ret;
	}*/
	//major_number=MAJOR(device_number);
	//printk(KERN_INFO"Major no of my char device is %d",major_number);
	ret=register_chrdev(0,"my_char_device",&char_file_operations);
	printk(KERN_INFO"major_number %d\n",ret);
	printk(KERN_INFO "make node using : \"mknod /dev/my_char_device c %d 0\" for device file",ret);
	return 0;
}

static void cleanup(void)
{
	unregister_chrdev(major_number,"my_char_device");
}
module_init(init);
module_exit(cleanup);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("abhi");
