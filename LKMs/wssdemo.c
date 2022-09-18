#include <linux/delay.h>
#include <linux/mm.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>
#include <linux/timer.h>
#include <asm/page.h>
#include <asm/current.h>
#include "../arch/x86/include/asm/pgtable_types.h"
#include "../arch/x86/include/asm/pgtable.h"

#define ITERATION 50
#define PAGES 1000

MODULE_AUTHOR("Abhishek Singh");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel tweaks");

//static int counter;
//static int i,virt_page_count,phy_page_count;
//static struct timer_list my_timer;
//pte_t array[PAGES];

static int pid;
int wss=0;
module_param(pid, int, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);
MODULE_PARM_DESC(pid, "int");

extern void (*page_fault_check)(struct task_struct *, unsigned long addr,int);

/*int follow_pte(struct mm_struct *mm, unsigned long addr,pte_t *page_entry)
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
}*/

void page_check(struct task_struct *ts,unsigned long addr,int pidd)
{
  struct mm_struct *mm=NULL;
  pgd_t *pgd;
  pud_t *pud;
  pmd_t *pmd;
  pte_t *pte;
  //printk(KERN_INFO "INSIDE PAGE CHECK\n");
  if(ts!=NULL && ts->pid==pid )
{  
  mm=ts->mm;
  pgd = pgd_offset(mm, addr);
  if (pgd_none(*pgd) || pgd_bad(*pgd))
    return ;
  pud = pud_offset(pgd, addr);
  if (pud_none(*pud) || pud_bad(*pud))
    return ;
  pmd = pmd_offset(pud, addr);
  if (pmd_none(*pmd) || pmd_bad(*pmd))
    return ;
  pte = pte_offset_kernel(pmd, addr);
  if (!pte)
    return ;
  if( pte_present(*pte) && (pte_flags(*pte) & _PAGE_PROTNONE) ) //&& !(pte_flags(*pte) & _PAGE_PRESENT))
  {
      printk(KERN_INFO "inside long if condition");
      wss++;
			set_pte(pte,pte_clear_flags(*pte,_PAGE_PRESENT));
      set_pte(pte,pte_set_flags(*pte,_PAGE_PROTNONE));
   }   
  }
}

int wss_marking(struct task_struct *ts)
{
  struct mm_struct *mm=NULL;
  struct vm_area_struct *vma=NULL;
  unsigned long page_addr=0;
        
  pgd_t *pgd;
  pud_t *pud;
  pmd_t *pmd;
  pte_t *pte;
  
	
  if (ts != NULL)
  {
    mm = ts->mm;
    vma = mm->mmap;
    for ( vma=mm->mmap; vma;vma=vma->vm_next)
    {
      for(page_addr=vma->vm_start;page_addr<=vma->vm_end;page_addr+=PAGE_SIZE)
      {
        pgd = pgd_offset(mm, page_addr);
        if (pgd_none(*pgd) || pgd_bad(*pgd))
          return -2;
        pud = pud_offset(pgd, page_addr);
        if (pud_none(*pud) || pud_bad(*pud))
          return -2;
        pmd = pmd_offset(pud, page_addr);
        if (pmd_none(*pmd) || pmd_bad(*pmd))
          return -2;
        pte = pte_offset_kernel(pmd,page_addr);
        if (!pte)
          return -2;
        if (pte_present(*pte))
        {
              set_pte(pte,pte_clear_flags(*pte,_PAGE_PRESENT));
              set_pte(pte,pte_set_flags(*pte,_PAGE_PROTNONE));
        }
		  }
    }
  }
  return 0;
}

static int start(void)
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
      printk(KERN_INFO " second %d \n WSS : %d",i,wss);
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
  //int j=0;
  /*for(;j<=i;j++)
  {
    pte_clear_flags(array[j],_PAGE_PROTNONE);
    pte_set_flags(array[j], _PAGE_PRESENT);
  }
  printk(KERN_INFO "lkm removed\n");*/
}

module_init(start);
module_exit(cleanup);
