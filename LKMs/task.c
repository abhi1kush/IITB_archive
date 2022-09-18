#undef __KERNEL__
#define __KERNEL__
#undef __MODULE__
#define __MODULE__ 
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>
static int pid;
module_param(pid, int,0);

static int __init config_init(void)
   {     
       
	struct task_struct *ts=NULL;
	ts = pid_task(find_vpid((pid_t)pid), PIDTYPE_PID);   
         if(ts!=NULL && ts->pid==pid)
           { 
        	printk(KERN_INFO "the process name is %s and pid= %d\t parent pid=%d\n",ts->comm,ts->pid,ts->parent->pid);
        	printk(KERN_INFO "State %lu ,Min Fault %lu , start time %d \n",ts->state,ts->min_flt,ts->start_time);
           	return 0;
            
           }
          else {
 			printk(KERN_INFO "sorry the process is not found\n");
          }
                     
           

      return 0;

      
    }



static void __exit config_exit(void)
   {  
    printk(KERN_INFO "config_exit executed with sucess\n");
        return ;

    }

module_init(config_init);
module_exit(config_exit);
MODULE_AUTHOR("Abhishek Singh"); 
MODULE_LICENSE("Dual BSD/GPL"); 
MODULE_DESCRIPTION("testing for module.");
