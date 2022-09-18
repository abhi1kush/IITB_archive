#include <linux/mm.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>

MODULE_AUTHOR("Abhishek Singh");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel tweaks");

static int pid,wss_size;
module_param(pid, int,0);

extern int (*page_fault_check)(struct mm_struct *, unsigned long addr,int );

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

/*int rss_assi2(struct task_struct *ts)
{
  int virt_page_count=0,phy_page_count=0;
  struct mm_struct *mm=NULL;
	struct vm_area_struct *vma=NULL;
  pte_t *page_entry=NULL;
	
  if (ts != NULL)
  {
    mm = ts->mm;
		vma = mm->mmap;
    for ( vma=mm->mmap; vma;vma=vma->vm_next)
		{
			printk(KERN_INFO "Starting address: 0x%lx \n",vma->vm_start);
			if(follow_pte(mm,vma->vm_start,page_entry)==1)
      {
			  printk(KERN_INFO "PAGE Exist");
        pte_set_flags(*page_entry,_PAGE_PROTNONE);
        phy_page_count++;
      }
			else if(follow_pte(mm,vma->vm_start,page_entry)==-1)
			printk(KERN_INFO "Page DOES NOT Exist");
			else if(follow_pte(mm,vma->vm_start,page_entry)==-2)
			printk(KERN_INFO "ERROR problem in translation ");
			printk(KERN_INFO "Ending address : 0x%lx \n",vma->vm_end);
      virt_page_count++;
			
		}
  printk(KERN_INFO "Total no Virtual pages : %d",virt_page_count);
  printk(KERN_INFO "Total no Physical pages and RSS : %d ",phy_page_count);
  }
  return 0;
}
*/

int page_check(struct mm_struct *mm,unsigned long address,int pidd)
{
  pte_t *page_entry=NULL;
  if(pid==pidd)
  {
    if(follow_pte(mm,address,page_entry)==1)
    {
      if(pte_flags(*page_entry) & _PAGE_PRESENT)
        if(pte_flags(*page_entry) & _PAGE_PROTNONE)
        {
          wss_size++;
          pte_set_flags(*page_entry, _PAGE_PROTNONE);
          pte_clear_flags(*page_entry,_PAGE_PRESENT); 
        }
    }
  }
  return 0;
}


static int start(void)
{
  /**********passing pointer for hook*****************/
  page_fault_check=page_check;
  /***************************************************/
  
  /*ts = pid_task(find_vpid((pid_t)pid), PIDTYPE_PID);
  if(ts!=NULL && ts->pid==pid)
  {
    printk(KERN_INFO "process name: %s pid : %d\t parent pid :%d\n",ts->comm,ts->pid,ts->parent->pid);
  }
  else 
  {
    printk(KERN_INFO "ERROR unable to find process\n");
  }*/
  return 0;
}



static void end(void)
{
  printk(KERN_INFO "lkm removed\n");
}

module_init(start);
module_exit(end);
