#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/mutex.h>
#include <linux/kfifo.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/sched.h>
#include <linux/init.h>
#include <linux/string.h>

#define FIFO_SIZE      1024
#define PROC_FIFO "int-fifo"
//static DECLARE_KFIFO_PTR(test,int);

static DEFINE_KFIFO(test,int,FIFO_SIZE);

static void consumer(void)
{	
   int i;
   int counter=0;
   if (kfifo_peek(&test, &i))
                  printk(KERN_INFO "%d \n",i);
   while (kfifo_get(&test, &i)) 
   {
	   if(!counter%2)
               printk(KERN_INFO "pid = %d \n",i);
	   else
	   	printk(KERN_INFO "name =%s\n",&i);
	   counter++;
   }
   
}
static int producer(void)
{
   struct task_struct *task=NULL;
   for_each_process(task)
   {	 
	   kfifo_in(&test,task->pid,1);
	   kfifo_in(&test,task->comm,1);
	   //kfifo_in(&test,task->comm, 5);
   } 
   return 0;
}

 static int __init init(void)
 {
	 /*int ret; 
         ret = kfifo_alloc(&test, FIFO_SIZE, GFP_KERNEL);
         if (ret) 
	 {
                printk(KERN_ERR "Error kfifo_alloc\n");
                return ret;
          }*/
	  producer();
	  consumer();
 
         return 0;
 }
 
 static void __exit exit(void)
{
         //remove_proc_entry(PROC_FIFO, NULL);
         //kfifo_free(&test);
 }
 
module_init(init);
module_exit(exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("abhi");
