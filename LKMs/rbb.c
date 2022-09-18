#include <linux/mm.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>
#include <linux/timer.h>
#include <asm/page.h>
#include <asm/current.h>
#include <linux/delay.h>

#define ITERATION 50
#define PAGES 1000

MODULE_AUTHOR("Abhishek Singh");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel tweaks");

static int pid,wss_size;
module_param(pid, int,0);

extern void (*page_fault_check)(struct task_struct *, unsigned long ,int );

int follow_pte(struct mm_struct *mm, unsigned long addr,pte_t *page_entry)
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
  pte = pte_offset_kernel(pmd, addr);
  if (!pte)
    return -2;
  if (pte_present(*pte))
  {
    page_entry=pte;
    return 1;
  }
  else
    return -1;
}

void page_check(struct task_struct *ts,unsigned long address,int pidd)
{
  pte_t *page_entry=NULL;
  struct mm_struct *mm=NULL;
  if(pid==pidd)
  { 
    mm=ts->mm;
    if(follow_pte(mm,address,page_entry)==1)
    { 
      if((pte_flags(*page_entry) & _PAGE_PRESENT) && !(pte_flags(*page_entry) & _PAGE_PROTNONE))
        {
          printk(KERN_INFO"inside hook");
          wss_size++;
          set_pte(page_entry,pte_set_flags(*page_entry, _PAGE_PROTNONE));
          set_pte(page_entry,pte_clear_flags(*page_entry,_PAGE_PRESENT)); 
        }
    }
  }
}



int wss_marking(struct task_struct *ts)
{
  struct mm_struct *mm=NULL;
	struct vm_area_struct *vma=NULL;
  pte_t *page_entry=NULL;
  unsigned long page_addr=0;

  if (ts != NULL)
  {
    mm = ts->mm;
		vma = mm->mmap;
    for ( vma=mm->mmap; vma;vma=vma->vm_next)
		{
		for(page_addr=vma->vm_start;page_addr<=vma->vm_end;page_addr+=PAGE_SIZE)
      {
		
      
      printk(KERN_INFO "Starting address: 0x%lx \n",page_addr);
			if(follow_pte(mm,page_addr,page_entry)==1) //==> implicitly assigning page_entry in pte_follow()
      {
			  printk(KERN_INFO "PAGE Exist");
        set_pte(page_entry,pte_set_flags(*page_entry,_PAGE_PROTNONE));
        set_pte(page_entry,pte_clear_flags(*page_entry, _PAGE_PRESENT));
      }
			//else if(follow_pte(mm,vma->vm_start,page_entry)==-1)
			//printk(KERN_INFO "Page DOES NOT Exist");
			//else if(follow_pte(mm,vma->vm_start,page_entry)==-2)
			printk(KERN_INFO "ERROR problem in translation ");
		  }
    }
  }
  return 0;
}

static int __init start(void)
{ 
  int i=0;
  struct task_struct *ts=NULL;
  page_fault_check=page_check;
  ts = pid_task(find_vpid((pid_t)pid), PIDTYPE_PID);
  if(ts!=NULL && ts->pid==pid)
  {
    printk(KERN_INFO "process name: %s pid : %d\t parent pid :%d\n",ts->comm,ts->pid,ts->parent->pid);
    while(i++ < 60)
    {
      wss_marking(ts);
      printk(KERN_INFO "WSS : %d",wss_size);
      msleep(10000);
    }
  }
  else 
  {
    printk(KERN_INFO "ERROR unable to find process\n");
  }
  return 0;
}

static void __exit cleanup(void)
{
  page_fault_check=NULL;
}

module_init(start);
module_exit(cleanup);
