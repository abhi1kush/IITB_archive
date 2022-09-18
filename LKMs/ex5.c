#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/slab.h>

struct mylist
{
  volatile long state;
  int pid;
  char (*name)[16];
  int processor;
  //unsigned long dec_flt; // page fault count of the last time
  struct mylist *prev;
  struct mylist *next;
}*head=NULL;

void add_task_data(struct task_struct *ts)
{
  struct mylist *new,*tmp;
  new=(struct mylist *)kmalloc(sizeof(struct mylist),GFP_KERNEL);
  new->state=ts->state;
  new->pid=ts->pid;
  new->name=ts->comm;
  new->processor=ts->on_cpu;
  //new->dec_flt=ts->dec_flt;
  tmp=head;
  if(head==NULL)
  {
    head=new;
    head->prev=head->next=NULL;
  }
  else
  {
    while(tmp->next!=NULL)
      tmp=tmp->next;
    new->next=NULL;
    tmp->next=new;
    new->prev=tmp;
  }
}


static void init(void)
{
  struct task_struct *ts;
  for_each_process(ts)
  {
    add_task_data(ts);
  }
}

static void cleanup(void)
{
  struct mylist *ptr;
  ptr=head;
  while(ptr->next!=NULL)
  {
    printk(KERN_INFO"PID:%d  NAME :%s ON_CPU_CORE : %d\n",ptr->pid,ptr->name,ptr->processor);
    ptr=ptr->next;
  }
  printk(KERN_INFO "lkm removed \n");
}

module_init(init);
module_exit(cleanup);
MODULE_AUTHOR("Abhishek"); 
MODULE_LICENSE("GPL"); 
MODULE_DESCRIPTION("loadable kernel module.");
