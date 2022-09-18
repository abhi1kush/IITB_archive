#include<linux/module.h>
#include<linux/kernel.h>
#include<linux/fs.h>
#include<linux/cdev.h>
#include<asm/uaccess.h>
#include<linux/semaphore.h>
#include<linux/kfifo.h>
#include<linux/proc_fs.h>
#define FIFO_SIZE       128
/* name of the proc entry */
#define PROC_FIFO       "record-fifo"

/* lock for procfs read access */
static DEFINE_MUTEX(read_lock);

/* lock for procfs write access */
static DEFINE_MUTEX(write_lock);

/*
 * define DYNAMIC in this example for a dynamically allocated fifo.
 *
 * Otherwise the fifo storage will be a part of the fifo structure.
 */
#if 0
#define DYNAMIC
#endif

/*
 * struct kfifo_rec_ptr_1 and  STRUCT_KFIFO_REC_1 can handle records of a
 * length between 0 and 255 bytes.
 *
 * struct kfifo_rec_ptr_2 and  STRUCT_KFIFO_REC_2 can handle records of a
 * length between 0 and 65535 bytes.
 */

#ifdef DYNAMIC
struct kfifo_rec_ptr_1 test;

#else
typedef STRUCT_KFIFO_REC_1(FIFO_SIZE) mytest;

static mytest test;
#endif

MODULE_LICENSE("DUAL BSD/GPL"); 
int t;
static struct proc_dir_entry *example_dir,*foo_file;

static int dev_open(struct inode *,struct file *); 
static int dev_release(struct inode *,struct file *); 
static ssize_t dev_read(struct file *,char *, size_t ,loff_t *); 
static ssize_t dev_write(struct file *,const char *,size_t ,loff_t *); 
int read_proc(struct file *,char *,size_t,loff_t * );
struct chardevice{
      char data[100];
      struct semaphore sem;
}device;
int len,temp,reads,writes;
char msg[100];
static struct proc_dir_entry *proc_entry;
static short readPos=0;
struct file_operations dev_ops = {
    .owner = THIS_MODULE,
    .read = dev_read,
    .write = dev_write,
    .open = dev_open,
    .release = dev_release
};
/////Proc/sys/            ///////////////// Code
struct file_operations proc_fops = {
    .owner=THIS_MODULE,
    .read = read_proc
   
};

int read_proc(struct file *filp,char *buf,size_t count,loff_t *offp )
{

if(count>temp)
{
count=temp;
}
sprintf(msg,"writes# %d\nreads# %d\n",reads,writes);
temp=temp-count;
copy_to_user(buf,msg, count);
if(count==0)
temp=len;

return count;
}




int init_module(void)
{
   int rv;
   proc_entry = proc_create("myDev", 0, NULL,&proc_fops);
   reads=writes=0;
   sprintf(msg,"writes# %d\nreads# %d\n",reads,writes);
   printk(KERN_INFO "mesg=%s",msg); 
   len=strlen(msg);
   temp=len;
  printk(KERN_INFO " myDev  proc created \n");

   t=register_chrdev(0,"myDev",&dev_ops);
   printk(KERN_INFO "%d",t);
    if(t<0)
    printk(KERN_ALERT "Device registration failed \n");
    else
    printk(KERN_ALERT "Device registered ..\nmknod /dev/myDev c %d 0",t);
    sema_init(&device.sem,1);
    memset(device.data,'\0',100);
	
#ifdef DYNAMIC
        int ret;

        ret = kfifo_alloc(&test, FIFO_SIZE, GFP_KERNEL);
        if (ret) {
                printk(KERN_ERR "error kfifo_alloc\n");
                return ret;
        }
#else
        INIT_KFIFO(test);
#endif
     
   return 0;
}

void cleanup_module(void)
{
   remove_proc_entry("myDev", NULL);
   unregister_chrdev(t,"myDev");
#ifdef DYNAMIC
        kfifo_free(&test);
#endif

}
 

static int dev_open(struct inode *inode,struct file *fil)
{
   printk(KERN_INFO "device opened\n");
    if(down_interruptible(&device.sem)!=0)
    {
         printk(KERN_INFO "mychardevice:could not lock device during open\n");
         return -1;
    }

    return 0;
}


static ssize_t dev_read(struct file *filp,char *buff,size_t len,loff_t *off)
{
 int ret;
 int readPos=0;
 if(kfifo_is_empty(&test)) {
   printk(KERN_INFO "list empty\n");
     return -1;
}
else
{
                
           ret = kfifo_out(&test, device.data, sizeof(device.data));
 
           device.data[ret] = 0;
           printk(KERN_INFO "item = %.*s\n", ret,device.data);
  
}

  printk(KERN_INFO "device read\n");
  while((device.data[readPos]!=0))
  {  
     printk(KERN_INFO "%c\n",device.data[readPos]);
     put_user(device.data[readPos],buff++);
     len--;
     readPos++;
  }
  

  writes++;
  return 0;
}
static ssize_t dev_write(struct file *filp,const char *buff,size_t len,loff_t *off)
{
   int ret;
   short count=0;
   memset(device.data,0,100);
   readPos=0;
   printk(KERN_INFO "device: write\n");
   while(len>0)
   {
      device.data[count]=buff[count];
      count++;
      len--;
   }
   ret=kfifo_in(&test,device.data,strlen(device.data));
   printk("ret at insertion %d\n",ret);

   reads++;
   return 1;
}

static int dev_release(struct inode *inod,struct file *fil)
{
   up(&device.sem);
   printk(KERN_ALERT "Device Closed\n");
   return 0;
}

