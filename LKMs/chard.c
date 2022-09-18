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
#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h> /*For the character device driver support */

#define FIFO_SIZE      4096
#define PROC_FIFO "int-fifo"

static DEFINE_KFIFO(c_queue,int,FIFO_SIZE);



ssize_t char_read(struct file *pfile, char __user *buffer, size_t length, loff_t *offset)
{
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	return 0;

}
ssize_t char_write(struct file *pfile, const char __user *buffer, size_t length, loff_t *offset)
{
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	return 0;

}
int char_open(struct inode *pinode, struct file *pfile)
{
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	return 0;
}
int char_release(struct inode *pinode, struct file *pfile)
{
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	return 0;

}
int char_close(struct inode *pinode,struct file *pfile)
{
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	return 0;

}

/*to hold file operations to be performed on devic*/
struct file_operations char_file_operations ={
	.owner= THIS_MODULE,
	.open = char_open,
	.read = char_read,
	.write = char_write,
	.release = char_close,
};


static int init(void)
{
	printk(KERN_INFO"INside the %sfunction\n",__FUNCTION__);
	/*Register with the kernel and indicate that we are registering a character device driver */
	register_chrdev(240/*Major Number*/,"Simple Char Drv"/*Driver Name*/,&char_file_operations /*File Oprn*/);
	return 0;
}

static int exit(void)
{
	printk(KERN_INFO"Inside the %s function\n",__FUNCTION__);
	/*Unregister the character device driver*/
	unregister_chrdev(600,"simple");
	return 0;
}

module_init(init);
module_exit(exit);
