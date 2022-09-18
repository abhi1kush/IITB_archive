#include <linux/list.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/slab.h>

struct mylist
{
	struct list_head list;
	volatile long state;
	int pid;
  int processor;
	char *name;
	
};

static void __init init(void)
{
	struct mylist *temp,ptr;
	struct task_struct *tsk,*ts=NULL;
	struct list_head *pos;
	int i=0;
	INIT_LIST_HEAD(&ptr.list);
	for_each_process(tsk)
	{
		temp=(struct mylist *)kmalloc(sizeof(struct mylist),GFP_KERNEL);
		temp->state=tsk->state;
		temp->name=tsk->comm;
		temp->pid=tsk->pid;
    temp->processor=tsk->on_cpu;
    
    
		list_add_tail(&temp->list,&(ptr.list));
	}
  ts=&init_task;
	printk(KERN_INFO "\nTraversing the list using list_for_each()\n");
  list_for_each(pos,&(ptr.list))
  {
     ts=next_task(ts);
     temp=list_entry(pos,struct mylist,list);
     printk(KERN_INFO " mylist_Pid=%d\n task_pid=%d\n  state=%d\n name=%s, on_cpu %d\n",temp->pid,ts->pid,temp->state,temp->name,temp->processor);
  }
	
}

static void __exit cleanup(void)
{
 printk(KERN_INFO "\n lkm removed \n");
}
module_init(init);
module_exit(cleanup);
MODULE_LICENSE("GPL");

