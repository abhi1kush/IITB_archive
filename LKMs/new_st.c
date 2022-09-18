#include <linux/version.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/slab.h>
#include <linux/mm.h>

#define PAGES 16

int major_number;
/**/
static char *kmalloc_area;
static void *kmalloc_ptr;

static int char_open(struct inode *inode, struct file *filp)
{
	return 0;
}

static int char_release(struct inode *inode, struct file *filp)
{
	return 0;
}

int char_mmap(struct file *filp, struct vm_area_struct *vma)
{
	int ret;
	unsigned long size = vma->vm_end - vma->vm_start;
	if (size > PAGES * PAGE_SIZE)
	{
		printk(KERN_ALERT"DEMAND for Allocation is out of limit");
		return -EIO;
	}
	if ((ret = remap_pfn_range(vma,vma->vm_start,virt_to_phys((void *)kmalloc_area) >> PAGE_SHIFT,size,vma->vm_page_prot)) < 0) 
	{
		return ret;
	}
	return 0;
}

static struct file_operations char_mmap_fops = {
	.owner = THIS_MODULE,
	.open = char_open,
	.release = char_release,
	.mmap = char_mmap,
};

static int __init init(void)
{
	int ret = 0;
	unsigned long i,end;
	int count=1;
	char buffer[50],*ptr;
	if ((kmalloc_ptr = kmalloc((PAGES + 2) * PAGE_SIZE, GFP_KERNEL)) == NULL) 
	{
		ret = -ENOMEM;
		return ret;
	}
	
	/* round it up to the page bondary */
	kmalloc_area = (char *)((((unsigned long)kmalloc_ptr) + PAGE_SIZE - 1) & PAGE_MASK);
	
	major_number=register_chrdev(0,"my_char_device",&char_mmap_fops);
	if(major_number==0)
	{
		printk(KERN_ALERT"ERROR in registering device\n");
		return 0;
	}
	printk(KERN_INFO"major_number %d\n",major_number);
	printk(KERN_INFO "make node using : \"mknod /dev/my_char_device c %d 0\" for device file",major_number);
 	end=(unsigned long )kmalloc_area + PAGES*PAGE_SIZE ;
	/* mark the pages reserved */
	for (i = 0; i < PAGES * PAGE_SIZE; i+= PAGE_SIZE) 
	{	
		SetPageReserved(virt_to_page(((unsigned long)kmalloc_area) + i));
	}
	
	for (i = (unsigned long) kmalloc_area ; i < end ; i+=PAGE_SIZE) 
	{
		sprintf(buffer,"This is kernel : writing on page %d",count++);
		ptr=(char *)i;
		memset(ptr,0,PAGE_SIZE);
		memcpy(ptr,buffer,50);
	}
	return ret;
}

static void __exit cleanup(void)
{
	char *ptr;
	unsigned long i,end;
	end=(unsigned long )kmalloc_area + PAGES*PAGE_SIZE ;
	for (i = (unsigned long ) kmalloc_area; i < end ; i += PAGE_SIZE) 
	{
		ptr=(char *)i;
		printk(KERN_INFO"kernel printk o/p :%s",ptr);
	}
	
	unregister_chrdev(major_number,"my_char_device");

	/*unreserve the pages */
	for (i = 0; i < PAGES * PAGE_SIZE; i+= PAGE_SIZE) 
	{
		SetPageReserved(virt_to_page(((unsigned long)kmalloc_area) + i));
	}
	 
	/*free the memory areas */
	
	kfree(kmalloc_ptr);
}

module_init(init);
module_exit(cleanup);
MODULE_DESCRIPTION("learning kernel prog");
MODULE_AUTHOR("abhishek");
MODULE_LICENSE("GPL");

