
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/sched.h>
 #include <linux/init.h>
 #include <linux/module.h>
 #include <linux/proc_fs.h>
 #include <linux/mutex.h>
 #include <linux/kfifo.h>
#define FIFO_SIZE      1024 
#define PROC_FIFO       "bytestream-fifo"
static DEFINE_MUTEX(read_lock);
static DEFINE_MUTEX(write_lock);
#if 0
#define DYNAMIC
#endif
  
#ifdef DYNAMIC
static struct kfifo test;
#else
static DECLARE_KFIFO(test, unsigned char, FIFO_SIZE);
#endif
  

static void consumer(void)
{
   unsigned char i;
   if (kfifo_peek(&test, &i))
                  printk(KERN_INFO "%d\n", i);
   while (kfifo_get(&test, &i)) 
   {
               printk(KERN_INFO "pid = %d\n", i);
   }
   
}
static int __init testfunc(void)
{
   int i;
   char	buf[100];
   for (i = 0; i != 10; i++)
              kfifo_put(&test, i); 
  kfifo_in(&test, "hello", 5); 
  for (i = 0; i < 10; i++) {
		memset(buf, 'a' + i, i + 1);
		kfifo_in(&test, buf, i + 1);
	}
  consumer();
   return 0;
}


 static ssize_t fifo_write(struct file *file, const char __user *buf,
                                                 size_t count, loff_t *ppos)
 {
         int ret;
         unsigned int copied;
 
         if (mutex_lock_interruptible(&write_lock))
                 return -ERESTARTSYS;

         ret = kfifo_from_user(&test, buf, count, &copied);
 
         mutex_unlock(&write_lock);
 
         return ret ? ret : copied;
 }
 
 static ssize_t fifo_read(struct file *file, char __user *buf,
                                                 size_t count, loff_t *ppos)
 {
         int ret;
         unsigned int copied;
 
         if (mutex_lock_interruptible(&read_lock))
                return -ERESTARTSYS;
 
         ret = kfifo_to_user(&test, buf, count, &copied);
 
         mutex_unlock(&read_lock);
 
        return ret ? ret : copied;
 }
 
 static const struct file_operations fifo_fops = {
         .owner          = THIS_MODULE,
         .read           = fifo_read,
         .write          = fifo_write,
         .llseek         = noop_llseek,
 };
 
 static int __init example_init(void)
 {
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
        if (testfunc() < 0) {
#ifdef DYNAMIC
                kfifo_free(&test);
 #endif
                 return -EIO;
         }
 
         if (proc_create(PROC_FIFO, 0, NULL, &fifo_fops) == NULL) {
 #ifdef DYNAMIC
                kfifo_free(&test);
 #endif
                 return -ENOMEM;
         }
         return 0;
 }
 
 static void __exit example_exit(void)
{
         remove_proc_entry(PROC_FIFO, NULL);
 #ifdef DYNAMIC
         kfifo_free(&test);
 #endif
 }
 
 module_init(example_init);
 module_exit(example_exit);
 MODULE_LICENSE("GPL");
 MODULE_AUTHOR("Stefani Seibold <stefani@seibold.net>");
