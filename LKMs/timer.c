#include <linux/workqueue.h>
struct workqueue_struct * myqueue;
void dowork(struct work_struct *data);
DECLARE_DELAYED_WORK(mywork , dowork);

MODULE_AUTHOR("Abhishek Singh");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel tweaks");

void dowork(struct work_struct *data)
{
  printk("\n i am doing delayed work");
}

int __init init_module(void)
{
  myqueue=create_singlethread_workqueue("mywork");
  if(!queue_delayed_work(myqueue,&mywork,HZ*5))
      return -EBUSY;
  return 0;//success
}


void __exit cleanup_module(void)
{
  destroy_workqueue(myqueue);

}



module_init(init_module);
module_exit(cleanup_module);


