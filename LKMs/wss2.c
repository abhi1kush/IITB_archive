#include <linux/mm.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>

MODULE_AUTHOR("Abhishek Singh");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel tweaks");

static int pid;
module_param(pid, int,0);

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
  pte = pte_offset_map(pmd, addr);
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

int wss_marking(struct task_struct *ts)
{
  struct mm_struct *mm=NULL;
	struct vm_area_struct *vma=NULL;
  pte_t *page_entry=NULL;
	
  if (ts != NULL)
  {
    mm = ts->mm;
		vma = mm->mmap;
    for ( vma=mm->mmap; vma;vma=vma->vm_next)
		{
			/*printk(KERN_INFO "Starting address: 0x%lx \n",vma->vm_start);*/
			if(follow_pte(mm,vma->vm_start,page_entry)==1) //==> implicitly assigning page_entry in pte_follow()
      {
			  /*printk(KERN_INFO "PAGE Exist");*/
        pte_set_flags(*page_entry,_PAGE_PROTNONE);
        pte_clear_flags(*page_entry, _PAGE_PRESENT);
      }
			/*else if(follow_pte(mm,vma->vm_start,page_entry)==-1)
			printk(KERN_INFO "Page DOES NOT Exist");*/
			else if(follow_pte(mm,vma->vm_start,page_entry)==-2)
			printk(KERN_INFO "ERROR problem in translation ");
		}
  }
  return 0;
}

static int start(void)
{
  struct task_struct *ts=NULL;
  ts = pid_task(find_vpid((pid_t)pid), PIDTYPE_PID);
  if(ts!=NULL && ts->pid==pid)
  {
    printk(KERN_INFO "process name: %s pid : %d\t parent pid :%d\n",ts->comm,ts->pid,ts->parent->pid);
    return wss_marking(ts);
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
