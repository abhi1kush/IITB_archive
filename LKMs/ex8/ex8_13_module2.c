#include <linux/io.h>
#include <linux/slab.h>
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
#include <linux/sched.h>

#define VMALLOC 0
#define KMALLOC 1

pte_t *pt=NULL,*pt2=NULL;

extern char * virt_addr;
extern char * virt_addr2;

int page_walk(unsigned long addr,int flag)
{
	pgd_t *pgd;
	pud_t *pud;
	pmd_t *pmd;
	pte_t *pte;
	if(current != NULL && current->mm != NULL)
	{
		pgd = pgd_offset(current->mm,addr);
		if (pgd_none(*pgd) || pgd_bad(*pgd))
		   return -1;
		pud = pud_offset(pgd, addr);
		if (pud_none(*pud) || pud_bad(*pud))
		  return -2;
		pmd = pmd_offset(pud, addr);
		if (pmd_none(*pmd) || pmd_bad(*pmd))
		  return -3;
		pte = pte_offset_kernel(pmd, addr);
		if(pte!=NULL)
		{
			if(flag==VMALLOC )
				pt2=pte;
			else if(flag == KMALLOC )
				pt=pte;
			return 1;

		}
	}
	return -4;
}

void kmalloc_demo(void)
{
	long unsigned int phy,phy2,phy3;
	if(virt_addr!=NULL)
	printk(KERN_INFO"virtual addr ------------- : x0%lu\n",(unsigned long)virt_addr);
	if(virt_addr!=NULL)
	{
		/******* physical address using page walk *********************/
		page_walk((unsigned long )virt_addr,KMALLOC);
		printk(KERN_INFO"Physical Address --------- : x0%lu",(unsigned long)pt);
		/**************************************************************/
		phy=virt_to_phys(virt_addr);
		printk(KERN_INFO"Physical addr virt_to_phys : x0%lu\n",(unsigned long)phy);
		phy2=__pa(virt_addr);
		printk(KERN_INFO"Physical addr using __pa() : x0%lu\n",(unsigned long)phy2);
		//memcpy(phy,"this is kernel",15);
	}
	/*******physical addresss using page walk *********************
	phy3=slow_virt_to_phys(virt_addr);
	printk(KERN_INFO"Physical (page walk using slow_virt_to_phys): x0%lu\n",(unsigned long)phy3);
	***************************************************************/
}

void vmalloc_demo(void)
{
	long unsigned int phy,phy2,phy3;
	if(virt_addr2!=NULL)
	printk(KERN_INFO" virtual addresss -------- : x0%lu\n",(unsigned long)virt_addr2);
	if(virt_addr2!=NULL)
	{
		/******* physical address using page walk*********************/
		page_walk((unsigned long )virt_addr2,VMALLOC);
		printk(KERN_INFO"Physical Address --------  : x0%lu",(unsigned long)pt2);
		/**************************************************************/
		phy=virt_to_phys(virt_addr2);
		printk(KERN_INFO"Physical addr virt_to_phys : x0%lu\n",(unsigned long)phy);
		phy2=__pa(virt_addr2);
		printk(KERN_INFO"Physical addr using __pa() : x0%lu\n",(unsigned long)phy2);
		//memcpy(phy,"this is kernel",15);
	}
	/*******physical addresss using page walk **********************
	phy3=slow_virt_to_phys(virt_addr2);
	printk(KERN_INFO"Physical (page walk using slow_virt_to_phys): x0%lu\n",(unsigned long)phy3);
	***************************************************************/
}


static int init(void)
{
  printk(KERN_INFO"\n################## MODULE 2 STARTING ###################\n");
  printk(KERN_INFO"\n******* Kmalloc *******\n");
  kmalloc_demo();
  printk(KERN_INFO"\n******* vmalloc *******\n");
  vmalloc_demo();
  printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
  return 0;
}

static void  cleanup(void)
{ 
  printk(KERN_INFO "lkm removed\n");
}

module_init(init);
module_exit(cleanup);
MODULE_AUTHOR("Abhishek Singh");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel tweaks");
