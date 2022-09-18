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

# define PAGES 10
# define SIZE 10

#ifndef VM_RESERVED
# define  VM_RESERVED   (VM_DONTEXPAND | VM_DONTDUMP)
#endif

//struct mmap_info 
//{
//	char *data;	/* the data */
//	int reference;       /* how many times it is mmapped */  	
//};

//struct mmap_info * array[PAGES];

int major_number;

int char_open(struct inode *pinode, struct file *pfile)
{ 	
	
	printk(KERN_INFO "DEVICE OPENED SUCCESSFULY");
	return 0;
}

/*int char_release(struct inode *pinode, struct file *pfile)
{
	printk(KERN_INFO "inside the char_release function\n");
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	return 0;

}*/


/* keep track of how many times it is mmapped */
void mmap_open(struct vm_area_struct *vma)
{
	//struct mmap_info *info = (struct mmap_info *)vma->vm_private_data;
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	//info->reference++;
}

void mmap_close(struct vm_area_struct *vma)
{
	//struct mmap_info *info = (struct mmap_info *)vma->vm_private_data;
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	//info->reference--;
}



struct vm_operations_struct mmap_vm_ops = {
	.open =     mmap_open,
	.close =    mmap_close,
};

int static char_mmap(struct file *pfile, struct vm_area_struct * vma)
{
	int ret;
	//struct page *page=NULL;
	//unsigned long pfn;
	//size=sizeof(struct mmap_info)*PAGES;
	//info=kmalloc(size,GFP_KERNEL);
	//page=virt_to_page(vma->vm_start);
	//pfn=page_to_pfn(page);
        ret=remap_pfn_range(vma,vma->vm_start,vma->vm_pgoff,vma->vm_end - vma->vm_start,vma->vm_page_prot);
	if(!ret)
		return -EAGAIN;
	vma->vm_ops = &mmap_vm_ops;
	//pfile->private_data=page;
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	memcpy((char *)vma->vm_start, "hello from kernel this is file: ", 32);
	memcpy((char *)vma->vm_start + 32, pfile->f_dentry->d_name.name, strlen(pfile->f_dentry->d_name.name));
	return 0;
}

int char_close(struct inode *pinode,struct file *pfile)
{
	//struct mmap_info *info = pfile->private_data;
	/* obtain new memory */
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	//free_page((unsigned long)pfile->private_data);
	//kfree(info);
	//pfile->private_data = NULL;
	printk(KERN_INFO "DEVICE CLOSED\n");
	return 0;
}

/****** file operations to be performed on devic *******/
struct file_operations char_file_operations ={
	.owner= THIS_MODULE,
	.open = char_open,
	.release = char_close,
	.mmap = char_mmap
};

static int init(void)
{	
	int ret;
	ret=register_chrdev(0,"my_char_device",&char_file_operations);
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
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
	unregister_chrdev(major_number,"my_char_device");
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
}

module_init(init);
module_exit(cleanup);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("abhishek");
