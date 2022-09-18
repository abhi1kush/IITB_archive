#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>

static int pid;
module_param(pid, int,0);

static int __init parent_hry(void)
   {
     struct task_struct *ts=NULL,*pr=NULL,*temp=NULL;
     ts = pid_task(find_vpid((pid_t)pid), PIDTYPE_PID);
     pr=current->parent;
     printk(KERN_INFO "Parent herarchy:");
     for(temp=current;temp!=&init_task;temp->parent)
     {
     if(temp!=NULL)
     {
       printk(KERN_INFO "%s -> \n",temp->comm);
     }
     else {
 			      printk(KERN_INFO "sorry the process is not found\n");
     }
     return 0;

      
    }
   }



static int  __exit end(void)
   {  
    printk(KERN_INFO "config_exit executed with sucess\n");
    return 0;
   }

module_init(parent_hry);
module_exit(end);
MODULE_AUTHOR("Abhishek Singh"); 
MODULE_LICENSE("Dual BSD/GPL"); 
MODULE_DESCRIPTION("testing for module.");
