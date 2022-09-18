#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/moduleparam.h>
#include <linux/sched.h>

extern struct task_struct;
struct task_struct *t;
int p_id;
module_param(p_id,int,0);

static void __init start(void){
  if (t->pid==p_id)
    printk(KERN_ALERT "state %d",t->state);
}

static void __exit end(void){
	printk("lkm removed !!\n");
}

module_init(start);
module_exit(end);
MODULE_AUTHOR("Abhishek");
MODULE_LICENSE("Dual BSD/GPL");
MODULE_DESCRIPTION("testing for module");


