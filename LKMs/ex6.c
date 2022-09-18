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

#ifndef VM_RESERVED
# define VM_RESERVED (VM_DONTEXPAND | VM_DONTDUMP)
#endif

struct mmap_info 
{
	char *data;	
	int reference;     	
};

char * global_var=NULL;

int major_number;

void mmap_open(struct vm_area_struct *vma)
{
	struct mmap_info *info = (struct mmap_info *)vma->vm_private_data;
	info->reference++;
}

void mmap_close(struct vm_area_struct *vma)
{
	struct mmap_info *info = (struct mmap_info *)vma->vm_private_data;
	info->reference--;
}

static int mmap_fault(struct vm_area_struct *vma, struct vm_fault *vmf)
{
	struct page *page;
	struct mmap_info *info;
	info = (struct mmap_info *)vma->vm_private_data;
	if (!info->data) 
	{
		printk("no data\n");
		return 0;	
	}
	page = virt_to_page(info->data);
	get_page(page);
	vmf->page = page;					
	return 0;
}

struct vm_operations_struct mmap_vm_ops = {
	.open =     mmap_open,
	.close =    mmap_close,
	.fault =    mmap_fault,
};
int char_open(struct inode *pinode, struct file *pfile)
{ 	
	struct mmap_info *info = kmalloc(sizeof(struct mmap_info)*3, GFP_KERNEL);
	info->data = (char *)get_zeroed_page(GFP_KERNEL);
	global_var= info->data;
	memcpy(info->data, "hello from kernel on page 1: ", 32);
	memcpy(info->data + 32, pfile->f_dentry->d_name.name, strlen(pfile->f_dentry->d_name.name));
	memcpy(info->data + PAGE_SIZE , "hello from kernel on page 2: ", 32);
	memcpy(info->data + PAGE_SIZE + 32, pfile->f_dentry->d_name.name, strlen(pfile->f_dentry->d_name.name));
	pfile->private_data = info;
	printk(KERN_INFO "DEVICE OPENED SUCCESSFULY");
	return 0;
}

int char_release(struct inode *pinode, struct file *pfile)
{
	printk(KERN_INFO "inside the char_release function\n");
	return 0;
}


int char_mmap(struct file *pfile, struct vm_area_struct *vma)
{
	vma->vm_ops = &mmap_vm_ops;
	vma->vm_flags |= VM_RESERVED;
	/* assign the file private data to the vm private data */
	vma->vm_private_data = pfile -> private_data;
	mmap_open(vma);
	return 0;
}

int char_close(struct inode *pinode,struct file *pfile)
{
	struct mmap_info *info = pfile->private_data;
	printk(KERN_INFO"Kernel rading shared memory : %s",global_var);
	/* free memory */
	free_page((unsigned long)info->data);
	kfree(info);
	pfile->private_data = NULL;
	printk(KERN_INFO "DEVICE CLOSED\n");
	return 0;
}

/****** file operations to be performed on devic *******/
struct file_operations char_file_operations ={
	.owner= THIS_MODULE,
	.open = char_open,
	.release = char_close,
	.mmap = char_mmap,
};

static int init(void)
{	
	int ret;
	ret=register_chrdev(0,"my_char_device",&char_file_operations);
	if(ret==0)
	{
		printk(KERN_ALERT"ERROR in registering device\n");
		return 0;
	}
	printk(KERN_INFO"major_number %d\n",ret);
	printk(KERN_INFO "make node using : \"mknod /dev/my_char_device c %d 0\" for device file",ret);
	return 0;
}

static void cleanup(void)
{
	printk(KERN_INFO"Kernel rading shared memory : %s",global_var);
	unregister_chrdev(major_number,"my_char_device");
}

module_init(init);
module_exit(cleanup);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("abhishek");
