#include <linux/list.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/slab.h>


static void __init init(void)
{
	struct task_struct *tsk,*ts=NULL;
	
	printk(KERN_INFO "\nTraversing the list using list_for_each()\n");
  
}
	


static void __exit cleanup(void)
{
 printk(KERN_INFO "\n lkm removed \n");
}
module_init(init);
module_exit(cleanup);
MODULE_LICENSE("GPL");

