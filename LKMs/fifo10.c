#include <linux/kernel.h>
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

#define FIFO_SIZE      4096
#define PROC_FIFO "int-fifo"
//static DECLARE_KFIFO_PTR(test,int);

static DEFINE_KFIFO(test,int,FIFO_SIZE);

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

static void consumer(void)
{	
   int i;
   char buffer[20];
   struct task_struct *ts=NULL,*tsk=NULL;
   if (kfifo_peek(&test, &i))
                  printk(KERN_INFO "%d \n",i);
   
   ts= &init_task;
   while (kfifo_get(&test, &i)) 
   {		
	       printk(KERN_INFO "pid = %d   ",i);
	       sprintf(buffer,"pid = %d \n",i);
	       console_output(buffer);
	       sprintf(buffer,"task->pid is %d\n",ts->pid);
	       console_output(buffer);
	       if(tsk=next_task(ts) != &init_task)
		       ts=tsk;
   }
   
}
static int producer(void)
{
   struct task_struct *task=NULL;
   for_each_process(task)
   {	 
	   kfifo_put(&test,task->pid);
	   //kfifo_in(&test,task->comm, 5);
   } 
   return 0;
}

 static int __init init(void)
 {
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
