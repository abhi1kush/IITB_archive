#undef __KERNEL__
#define __KERNEL__
#undef __MODULE__
#define __MODULE__ 
#include <linux/mm.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>
#include <linux/delay.h>
#include <asm/page.h>


MODULE_AUTHOR("Abhishek Singh");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel tweaks");

int pid; 
int virt_page_count=0,phy_page_count=0;
module_param(pid, int ,0);


int follow_pte(struct mm_struct *mm, unsigned long addr)
{
  pgd_t *pgd;
  pud_t *pud;
  pmd_t *pmd;
  pte_t *pte;
  pgd = pgd_offset(mm, addr);
  if (pgd_none(*pgd) || pgd_bad(*pgd))
    return -2;
  pud = pud_offset(pgd, addr);
  if (pud_none(*pud) || pud_bad(*pud))
    return -2;
  pmd = pmd_offset(pud, addr);
  if (pmd_none(*pmd) || pmd_bad(*pmd))
    return -2;
  pte = pte_offset_map(pmd, addr);
  if (!pte)
    return -2;
  if (pte_present(*pte))
    return 1;
  else
    return -1;
}


int page_walk(struct mm_struct *mm,unsigned long addr1,unsigned long addr2)
{ 
  unsigned long i;
  for(i=addr1;i<=addr2;i+=4096)
  {
			if(follow_pte(mm,i)==1)
      {
			  //printk(KERN_INFO "ADDRESS : 0x%lx PAGE Exist\n",i);
        phy_page_count++;
      }
			else if(follow_pte(mm,i)==-1)
			;//printk(KERN_INFO "ADDRESS : 0x%lx  Page DOES NOT Exist\n",i);
			else if(follow_pte(mm,i)==-2)
			;//printk(KERN_INFO "ERROR problem in translation\n");
      virt_page_count++;
  }
  return 0;
}


int rss_assi2(struct task_struct *ts)
{
  struct mm_struct *mm=NULL;
	struct vm_area_struct *vma=NULL;

	if (ts != NULL)
  {
    mm = ts->mm;
		vma = mm->mmap;
    for ( vma=mm->mmap; vma;vma=vma->vm_next)
		{
			//printk(KERN_INFO "Starting address: 0x%lx \n",vma->vm_start);
			page_walk(mm,vma->vm_start,vma->vm_end);
			//printk(KERN_INFO "Ending address : 0x%lx \n",vma->vm_end);
		}
  printk(KERN_INFO "Total no Virtual pages : %d\n",virt_page_count);
  printk(KERN_INFO "RSS : %d \n",phy_page_count);
  }
  return 0;
}

static int start(void)
{
  int i=0;
  struct task_struct *ts=NULL;
  ts = pid_task(find_vpid((pid_t)pid), PIDTYPE_PID);
  if(ts!=NULL && ts->pid==pid)
  {
    printk(KERN_INFO "process name: %s pid : %d\t parent pid :%d\n",ts->comm,ts->pid,ts->parent->pid);
    while(i++<=20)
    {
      rss_assi2(ts);
      msleep(10000);
    }
  }
  else 
  {
    printk(KERN_INFO "ERROR unable to find process\n");
  }
  return 0;
}



static void endd(void)
{
  printk(KERN_INFO "lkm removed\n");
}

module_init(start);
module_exit(endd);
