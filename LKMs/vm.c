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


int vm_area( struct task_struct *ts )
	{ 

	printk(KERN_INFO "entered in vm_area\n");
	 if (ts == NULL)
		{ return 0; }
		else
		 {
	    struct mm_struct *mm = ts->mm;
		struct vm_area_struct *vma = NULL;
		
		int count=0;
		for ( vma=mm->mmap; vma;vma=vma->vm_next)
		{   ++count;
			printk(KERN_INFO "starting address is 0x%lx \n",vma->vm_start);
			printk(KERN_INFO "ending address is 0x%lx \n",vma->vm_end);
			
		}
		printk(KERN_INFO "the number of vm areas are %d and the number of areas counted are %d\n",mm->mm_count,count);
		printk(KERN_INFO "\nCode  Segment start = 0x%lx, end = 0x%lx \n"
                 "Data  Segment start = 0x%lx, end = 0x%lx\n"
                 "Stack Segment start = 0x%lx\n",
                 mm->start_code, mm->end_code,
                 mm->start_data, mm->end_data,
                 mm->start_stack);
		return 0;
		}

	}


static int __init config_init(void)
   {     
       
	struct task_struct *ts;
	ts = pid_task(find_vpid((pid_t)pid), PIDTYPE_PID);   
         if(ts!=NULL && ts->pid==pid)
           { 
        printk(KERN_INFO "the process name is %s and pid= %d\t parent pid=%d\n",ts->comm,ts->pid,ts->parent->pid);
           return vm_area(ts);
            
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
