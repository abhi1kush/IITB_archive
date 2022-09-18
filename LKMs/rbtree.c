#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/sched.h>
#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/mutex.h>
#include <linux/kfifo.h>
#include <linux/rbtree.h>
#include <linux/tty.h>

char buffer[50];
struct rb_root rbtree = RB_ROOT;

int console_output(char *str) 
{    
	struct tty_struct *tty;
	tty = get_current_tty();
	if(tty != NULL) 
	{
		(tty->driver->ops->write) (tty, str, strlen(str));
    	}
	else
        printk("tty is NULL");
	return 0;
}

static int init(void)
{
   struct task_struct *ts=NULL;
   struct mm_struct *mm=NULL;
   struct vm_area_struct *vma;
   struct rb_node *rnode;
   unsigned long start,end;
   for_each_process(ts)
   {
	if(ts!=NULL)
        mm=ts->mm;
        if(mm!=NULL)
         {
		 vma=mm->mmap;
	   	 for(rnode=&vma->vm_rb;rnode;rnode=rb_next(rnode))
               	 {
	          start=rb_entry(rnode, struct vm_area_struct, vm_rb)->vm_start;
                  sprintf(buffer,"vma_start=x0%ld\n\r",start);
                  console_output(buffer);

		  end=rb_entry(rnode, struct vm_area_struct, vm_rb)->vm_end;
	          sprintf(buffer,"vma_end=x0%ld\n\r",end);
                  console_output(buffer);
               	 }
            
          } 
    }
  
   return 0;
}

static void exit(void)
{
  printk(KERN_INFO"lkm removed");
}


module_init(init);
module_exit(exit);
MODULE_AUTHOR("Abhishek");
MODULE_LICENSE("GPL");
