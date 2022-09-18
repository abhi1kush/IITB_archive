//ex9
#include <linux/io.h>
#include <linux/slab.h>
#include <linux/delay.h>
#include <linux/mm.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>
#include <linux/timer.h>
#include<linux/slab.h>
#include <asm/page.h>
#include <asm/current.h>
#include <linux/sched.h>
#include <linux/kobject.h>
#include<asm/uaccess.h>
#include<asm/segment.h>
#include<linux/buffer_head.h>
#include<linux/version.h>
#include<linux/string.h>
#include <linux/string.h>
#include <linux/sysfs.h>
#include<linux/device.h>
#include<linux/rcupdate.h>
#include <linux/init.h>
#include<linux/fs_struct.h>
#include <linux/dcache.h>
#include <linux/fdtable.h>
#include <linux/fs.h>
#include <linux/path.h>

char filename[50];
int pid=-1;
char output[500];
int fs_details(char *,int );

static ssize_t filename_show(struct kobject *kobj, struct kobj_attribute *attr,char *buf)
{
      return sprintf(buf, "%s\n", filename);
      printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
}

static ssize_t filename_store(struct kobject *kobj, struct kobj_attribute *attr,const char *buf, size_t count)
{
      sscanf(buf, "%s", filename);
      printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
      return count;
}

static ssize_t pid_show(struct kobject *kobj, struct kobj_attribute *attr,char *buf)
{     
      return sprintf(buf, "%d\n",pid);
      printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
}
static ssize_t pid_store(struct kobject *kobj, struct kobj_attribute *attr,const char *buf, size_t count)
{
      sscanf(buf, "%d",&pid);
    
      if(pid != -1)
         fs_details(filename,pid);
      printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
      return count;
}

static ssize_t foutput_show(struct kobject *kobj, struct kobj_attribute *attr,char *buf)
{
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
	return sprintf(buf,"%s\n",output);
}

static ssize_t foutput_store(struct kobject *kobj, struct kobj_attribute *attr,const char *buf, size_t count)
{
      printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
      return count;
}

static struct kobj_attribute pid_attribute =
  __ATTR(pid, 0664, pid_show, pid_store);
static struct kobj_attribute filename_attribute =
  __ATTR(filename, 0664, filename_show, filename_store);
static struct kobj_attribute foutput_attribute =
  __ATTR(output, 0664, foutput_show, foutput_store);

static struct attribute *fo_attrs[] = {
    &foutput_attribute.attr,
    NULL, /* need to NULL terminate the list of attributes */
};

static struct attribute *attrs[] = {
    &filename_attribute.attr,
    &pid_attribute.attr,
    NULL, /* need to NULL terminate the list of attributes */
};
static struct attribute_group fo_attr_group = {
    .attrs = fo_attrs,
};

static struct attribute_group attr_group = {
    .attrs = attrs,
};

static struct kobject *finput;
static struct kobject *foutput;

/********************************************************************/

int fs_details(char *filename,int pid)
{
  int i =0;
  struct inode *ind;
  struct task_struct *ts;
  struct fdtable *fdt;
  struct path files_path;
  struct file f;
  char *cwd;
  char *buf = (char *)kmalloc(GFP_KERNEL,100*sizeof(char));
  memset(buf,0,100);
  memset(output,0,500);
  ts = pid_task(find_vpid((pid_t)pid), PIDTYPE_PID);
  // locking
  fdt = files_fdtable(ts->files); //ts->files->fdt;  
  rcu_read_lock();
  while(fdt->fd[i] !=NULL)
  {
      files_path = fdt->fd[i]->f_path;
      cwd= d_path(&files_path,buf,100*sizeof(char));
     printk("path %s, filename %s",cwd,kbasename(cwd));
    //if(strcmp(fdt->fd[i]->f_path.dentry->d_name.name,filename)==0)
    if(strcmp(kbasename(cwd),filename)==0)
    {
      ind = fdt->fd[i]->f_path.dentry->d_inode;
      sprintf(output,"file fd: %d\n Path : %s \n Acess time %ld \n Modified Time %ld \n blocks %ld \n Size in bytes %ld \n Consumed bytes %ld \n No ofopen instances %ld \n inode no %ld \n offset %ld \n open function address %p \n relese function address %p \n",i,cwd,ind->i_atime.tv_nsec,ind->i_mtime.tv_nsec,ind->i_blocks,ind->i_size,ind->i_bytes,fdt->fd[i]->f_count,ind->i_ino,fdt->fd[i]->f_pos,fdt->fd[i]->f_op->open,fdt->fd[i]->f_op->release);
      
      printk(KERN_INFO"file fd %d %s\n",i,cwd);
      ind = fdt->fd[i]->f_path.dentry->d_inode;
      printk(KERN_INFO"Acess time %ld\n",ind->i_atime.tv_nsec);
      printk(KERN_INFO"MOdified time %ld\n",ind->i_mtime.tv_nsec);
      printk(KERN_INFO"blocks %ld\n",ind->i_blocks);
      printk(KERN_INFO"size in bytes %ld\n",ind->i_size);
      printk(KERN_INFO"consumed bytes %ld\n",ind->i_bytes);
      printk(KERN_INFO"NO of open instances %ld\n",fdt->fd[i]->f_count);
      printk(KERN_INFO"inode no: %ld\n",ind->i_ino);
      printk(KERN_INFO"offset %ld\n",fdt->fd[i]->f_pos);
      printk(KERN_INFO"open function address %p\n",fdt->fd[i]->f_op->open);
      printk(KERN_INFO"release function address %p\n",fdt->fd[i]->f_op->release);
     break;
    
     }
    i++;
  }
  rcu_read_unlock();
  printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
  return 0;
}
/***********************************************************************/

static int init(void)
{
  int retval;
  finput = kobject_create_and_add("finput", kernel_kobj);
  if (!finput)
    return -ENOMEM; //out of memory error
  retval = sysfs_create_group(finput, &attr_group);
  if (retval)
    kobject_put(finput);
   foutput = kobject_create_and_add("foutput", kernel_kobj);
  if (!foutput)
    return -ENOMEM; //out of memory error
  retval = sysfs_create_group(foutput, &fo_attr_group);
  if (retval)
    kobject_put(foutput);
  printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
  return 0;
}

static void  cleanup(void)
{
  kobject_put(finput);
  kobject_put(foutput);
  printk(KERN_INFO "lkm removed\n");
}

module_init(init);
module_exit(cleanup);
MODULE_AUTHOR("Abhishek Singh");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel tweaks");
