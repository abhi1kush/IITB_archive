#include<linux/module.h>
#include<asm/uaccess.h>
#include<linux/init.h>
#include<linux/sysfs.h>
#include<linux/slab.h>
#include<linux/fs.h>
#include<linux/mm.h>
#include<linux/kobject.h>
#include<linux/string.h>
#include<linux/ioctl.h>
#include<linux/version.h>
#include<linux/device.h>

#ifndef VM_RESERVED 
#define VM_RESERVED (VM_DONTEXPAND|VM_DONTDUMP) 
#endif

struct lock
{
	   int lock;
};

#define LOCK _IOWR('q',0,struct lock *) // 'q' stands for /dev/sequencer
#define UNLOCK _IOWR('q',1,struct lock *)
#define STATUS _IOWR('q',2,struct lock *)

static DEFINE_MUTEX(lock);

int major_no;
static int flag,size,count=0;
static struct kobject *kobj;
struct mmap_info
{
	char *data ;
};
struct mmap_info *mp_info;


static long _ioctl(struct dev_ioctl_args *ap) //ioctl man page 
{
	struct lock l;
	switch(ap->a_cmd)
	{
		case LOCK:
			if(mutex_lock_interruptible(&lock))
				return -ERESTARTSYS;
			break;
		case UNLOCK:
			mutex_unlock(&lock);
			break;
		case STATUS:
			if(copy_to_user((struct lock *)ap->data,&l,sizeof(struct lock)))
				return -EACCES;
			break;
		default:
			return -EINVAL;
	}
	return 0;
}

void mmap_open(struct vm_area_struct *vma)
{
	printk(KERN_INFO"inside mmap_open() \n");
	count++;
}

void mmap_close(struct vm_area_struct *vma )
{
	printk(KERN_INFO "inside mmap_close() \n");
	mutex_unlock(&lock);
	count-- ;
}

static int mmap_fault(struct vm_area_struct *vma,struct vm_fault *vmf)
{
	struct page *page; 
     	mp_info=((struct mmap_info *)vma->vm_private_data);
     	if(!mp_info->data)
     	{
		printk("Error : null pointer\n");
	     	return -1;
     	}
     	page=virt_to_page(mp_info->data);
     	get_page(page);
     	vmf->page=page;
	//printk(KERN_INFO " inside fault () \n");
     	return 0;
}
struct vm_operations_struct mmap_fops ={
	.open=mmap_open,
	.close=mmap_close,
	.fault=mmap_fault,
};

int mmap_mmap(struct file * pfile , struct vm_area_struct *vma)
{
	printk(KERN_INFO "inside mmap_mmap()\n");
	vma->vm_ops=&mmap_fops;
	vma->vm_flags|=VM_RESERVED;
	vma->vm_private_data=pfile->private_data;
	mmap_open(vma);
	printk(KERN_INFO "leaving mmap_mmap()\n");
	return 0;
}

int char_close(struct inode *inode , struct file *pfile)
{
	struct mmap_info *info = pfile->private_data;
	free_page((unsigned long) info->data);
	pfile->private_data=NULL;
	return 0;
}

int char_open(struct inode *inode , struct file *pfile)
{
	pfile->private_data=mp_info;
	return 0;
}

static const struct file_operations char_fops={
	.open=char_open,
	.release=char_close,
	.mmap=mmap_mmap,
	.unlocked_ioctl=_ioctl
};

static ssize_t flag_show(struct kobject *kobj, struct kobj_attribute * attr, char *buf)
{
	int var;
	if (strcmp(attr->attr.name, "flag") == 0)
		var = flag;
	else
		var = size;
	return sprintf(buf, "%d\n", var);
}

static ssize_t flag_store(struct kobject *kobj, struct kobj_attribute *attr,const char *buf, size_t count2)
{
	int var;
	sscanf(buf, "%du", &var);
        printk(KERN_INFO "inside flag_store()%s\n",buf);
        if(var==0)
        {    	
          if(count)
          {
            printk(KERN_INFO "%d Processes sharing memory\n",count);
            return count2;
          }     
              flag = var;
	}
        else
        {
             flag=var;
        }     
        return count2;
}



static ssize_t size_store(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count2)
{
        int tmp;
	sscanf(buf, "%du", &tmp);
        printk(KERN_INFO "inside store() %d\n",tmp);
        if(tmp>size&&!count)
        {
         if(size>0)
         {
          free_page((unsigned long)mp_info->data);
          kfree(mp_info);
         }
          size = tmp;
          mp_info=(struct mmap_info *)kmalloc(sizeof(struct mmap_info)*size,GFP_KERNEL);
          memcpy(mp_info->data,"Hello this is kernel.",21);
        }

        return count2;
}

static struct kobj_attribute flag_attribute =__ATTR(flag, 0664, flag_show, flag_store);
static struct kobj_attribute size_attribute =__ATTR(size, 0664, flag_show, size_store);

static struct attribute *attrs[] = {
        &flag_attribute.attr,
        &size_attribute.attr,
        NULL,
};

static struct attribute_group attr_group = {
        .attrs = attrs,
};

static int init(void)
{
	int ret;
   	kobj=kobject_create_and_add("ex7",kernel_kobj);
   	ret=sysfs_create_group(kobj,&attr_group);
  	if(ret)
		kobject_put(kobj);
	/****** Registering char device ****************************************/
  	major_no=register_chrdev(0,"my_char_device",&char_fops);
    	if(major_no<0)
  		printk(KERN_ALERT "ERROR : Unable to register \n");
  	else
  		printk(KERN_ALERT "\nmknod /dev/my_char_device c %d 0",major_no);
	
	printk(KERN_INFO "inside init()\n");
    	return ret;
}

static void cleanup(void)
{
	kobject_put(kobj);
  	printk(KERN_INFO "lkm removed\n");
   	unregister_chrdev(flag,"my_char_device");

}

module_init(init);
module_exit(cleanup);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("ABHI");

