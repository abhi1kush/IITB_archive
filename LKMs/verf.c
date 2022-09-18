#include <linux/list.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/slab.h>

static void __init init(void)
{
	struct task_struct *tsk,*ts=NULL;
	for_each_process(tsk)
	{
	  printk(KERN_INFO"task_struct->pid:%d \nmtask_struct->comm:%s,\ntask_struct->state:%d\n,task_struct->on_cpu,%d\n",tsk->pid,tsk->comm,tsk->state,tsk->on_cpu);	
	}
  
}
	

static void __exit cleanup(void)
{
 printk(KERN_INFO "\n lkm removed \n");
}
module_init(init);
module_exit(cleanup);
MODULE_LICENSE("GPL");

