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

pte_t *pt=NULL;
struct dummy_struct 
{
	char array[4096];
};

struct dummy_struct * pointer,*pointer2;
char * virt_addr; 
char * virt_addr2; 

EXPORT_SYMBOL(virt_addr);
EXPORT_SYMBOL(virt_addr2);

int page_walk(unsigned long addr)
{
	pgd_t *pgd;
	pud_t *pud;
	pmd_t *pmd;
	pte_t *pte;
	if(current !=NULL && current->mm!=NULL)
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
			pt=pte;
			return 1;

		}
	}
	return -4;
}

int allocate_kmalloc(void)
{
	pointer = (struct dummy_struct *) kmalloc(sizeof(struct dummy_struct),GFP_KERNEL); 
	if(pointer == NULL)
	{
		return -1;
	}
	virt_addr=&pointer->array; // to export virt address
	return 1;
}

int allocate_vmalloc( void )
{
	pointer2 = (struct dummy_struct *)vmalloc(sizeof(struct dummy_struct));
	if(pointer2 ==NULL)
	{
		return -1;

	}
	virt_addr2= &pointer2->array;
	return 1;
}

void kmalloc_demo(void)
{
	unsigned long int phy,phy2,phy3;
	if(allocate_kmalloc()==-1)
	{
		printk(KERN_ALERT"kmalloc failed to allocate memory\n");
		return ;
	}
	printk(KERN_INFO"allocated page using kmalloc succesfully\n");
		printk(KERN_INFO"Virtual address ----------      : x0%lu\n",(unsigned long )&pointer->array);
	if(pointer != NULL)
	{
		/******* physical address using page walk *********************/
		page_walk(( unsigned long )&pointer->array);
		printk(KERN_INFO"physical addr (using page walk) : x0%lu\n",(unsigned long)pt);
		/**************************************************************/
		phy=(unsigned long int)virt_to_phys(&pointer->array);
		printk(KERN_INFO"Physical virt_to_phys           : x0%lu\n",phy);
		phy2=(unsigned long int)__pa(&pointer->array);
		printk(KERN_INFO"Physical addr using __pa()      : x0%lu\n",phy2);
		//memcpy(phy,"this is kernel",15);
	}
	/*******physical addresss using slow virt2phys **********************
	phy3=(unsigned long )slow_virt_to_phys(&pointer->array);
	printk(KERN_INFO"Physical (using slow_virt2phys) : x0%lu\n",phy3);
	***************************************************************/
}


void vmalloc_demo(void)
{
	unsigned long int phy,phy2,phy3;
	if(allocate_vmalloc()==-1)
	{
		printk(KERN_ALERT"kmalloc failed to allocate memory\n");
		return ;
	}
	printk(KERN_INFO"allocated page using vmalloc succesfully\n");
		printk(KERN_INFO"virtual address -----------------    : x0%lu",(unsigned long) &pointer2->array);
	if(pointer2 != NULL)
	{
		/******* physical address using page walk *********************/
		page_walk(( unsigned long )&pointer2->array);
		printk(KERN_INFO" physical address (using page walk)  : x0%lu\n",(unsigned long)pt);
		/**************************************************************/
		phy=(unsigned long)virt_to_phys(&pointer2->array);
		printk(KERN_INFO"Physical address virt_to_phys -----  : x0%lu\n",(unsigned long)phy);
		phy2=__pa(&pointer2->array);
		printk(KERN_INFO"Physical address using __pa() macro  : x0%lu\n",(unsigned long)phy2);
		//memcpy(phy,"this is kernel",15);
	}
	/*******physical addresss using slow virt2phys **********************
	phy3=(unsigned long)slow_virt_to_phys(&pointer2->array);
	printk(KERN_INFO"Physical (using slow_virt_to_phys)   : x0%lu\n",phy3);
	***************************************************************/
}

static int init(void)
{
  printk("################## MODULE 1 starting ##################\n");
  printk("\n*** Kmalloc ***\n");
  kmalloc_demo();
  printk("\n*** vmalloc ***\n");
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
