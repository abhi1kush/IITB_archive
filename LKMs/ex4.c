#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>

static int pid;
module_param(pid, int, 0 );
//MODULE_PARM_DESC(pid," Process id ");

void task_info(struct task_struct * ts)
{
	printk("processor %d\n",ts->processor);
	printk("session %d\n",ts->session);

}

/*int vm_area( struct vm_area_struct *mm )
	{ 

	printk(KERN_INFO "Entered in vm_area function\n");
	 if (ts == NULL)
		{ return 0; }
		else
		 {
		struct vm_area_struct *vma_pntr = NULL;
		int count = 0;
		
		for ( vma_pntr = mm->mmap; vma_pntr ; vma_pntr = vma_pntr -> vm_next)
		{   	++count;
			printk(KERN_INFO "starting address is 0x%lx \n",vma_pntr->vm_start);
			printk(KERN_INFO "ending address is 0x%lx \n",vma_pntr->vm_end);
		
		}

		printk(KERN_INFO "Total no. of  vm areas are %d , but counted areas : %d\n",mm->mm_count,count);
		printk(KERN_INFO "\n code start at = 0x%lx, end at = 0x%lx \n",mm->start_code,mm->end_code);
		printk( "data seg start at = 0x%lxend at = 0x%lx\n",mm->start_data,mm->end_data); 
		//printk("stack seg start = 0x%lx\n",mm->start_stack);
		return 0;
		}

	}

*/
static int __init start(void)
   {     
         struct task_struct *ts=NULL;
	 ts = pid_task(find_vpid((pid_t)pid), PIDTYPE_PID);   
	 struct mm_struct *mm = ts->mm;
         
	if(ts->pid==pid)
           { 
        	printk(KERN_INFO "process name is %s ; pid= %d	; parent pid=%d\n",ts->comm,ts->pid,ts->parent->pid);
		
		task_info(ts);
		//vm_area(mm);
		
            
           }
          else
		printk(KERN_ALERT "ERROR code not found \n");
         return 0;      
   }



static void __exit end(void)
   {  
    printk(KERN_INFO "lkm removed \n");
   }

module_init(start);
module_exit(end);
MODULE_AUTHOR("Abhishek"); 
MODULE_LICENSE("Dual BSD/GPL"); 
MODULE_DESCRIPTION("testing module.");
