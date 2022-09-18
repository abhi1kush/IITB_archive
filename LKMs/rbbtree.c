#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/sched.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/mutex.h>
#include <linux/kfifo.h>
#include <linux/rbtree.h>
#include <linux/tty.h>

struct rb_root mytree = RB_ROOT;
char buf[100];
static void printString(char *string) {

    struct tty_struct *tty;

    tty = get_current_tty();

    if(tty != NULL) {

        (tty->driver->ops->write) (tty, string, strlen(string));
    }

    else
        printk("tty equals to zero");
}

static int __init example_init(void)
{
   struct task_struct *task=NULL;
   struct mm_struct *mm=NULL;
   struct vm_area_struct *va;
   struct rb_node rnode,*node;
   for_each_process(task)
   {
	if(task!=NULL)
        mm=task->mm;
        if(mm)
         {
           va=mm->mmap;
	   rnode=va->vm_rb;
 		node=&rnode;
               while(node)
               {
                  sprintf(buf,"vm_start=%ld vm_end=%ld\n\r", rb_entry(node, struct vm_area_struct, vm_rb)->vm_start,rb_entry(node,struct vm_area_struct,vm_rb)->vm_end);
                  printString(buf);
                  node=rb_next(node);
               }
            
          } 
    }
  
   return 0;
}

static void __exit example_exit(void)
{
  sprintf(buf,"EXITED\n\r");
  printString(buf);  
}


module_init(example_init);
module_exit(example_exit);
MODULE_LICENSE("GPL");
