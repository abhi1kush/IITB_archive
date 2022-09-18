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
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

extern int (*context_counter)(struct task_struct *,struct task_struct *,int,unsigned long);
extern int (* rq_size)(int,unsigned int,unsigned long);
extern int (* per_pid_stats)(struct task_struct *);
extern int (* current_pc)(void *);
int pid,prio,curr_cpu;
void *pcvalue;

module_param(pid, int, 0);
//module_param(prio, int, 0);

static unsigned long  sched_counter[4],per_pid_switch_counter[4],total_time;
static long grqsize[4];
static int gcpu,prio1,prio2,prio3,prio4;
static unsigned int entryy,exitt,total;
static unsigned long migration,tot,switches[4];
/***********************proc file section start *************************************************************/
struct proc_dir_entry *assi4_proc_file;
struct proc_dir_entry *assi4_proc_file2;
int proc_open2(struct inode *, struct file *);
int proc_open(struct inode *, struct file *);
static int proc_readings(struct seq_file * , void * );
static int proc_readings2(struct seq_file *, void *);

struct file_operations proc_file_operations ={
	.owner = THIS_MODULE,
	.open = proc_open,
	.read = seq_read,
	.release = single_release
};

struct file_operations proc_file_operations2 ={
	.owner = THIS_MODULE,
	.open = proc_open2,
	.read = seq_read,
	.release = single_release
};

int proc_open(struct inode *pinode, struct file *pfile)
{
	return single_open(pfile,proc_readings,NULL);
}

int proc_open2(struct inode *pinode, struct file *pfile)
{
	return single_open(pfile,proc_readings2,NULL);
}

static int proc_readings(struct seq_file * sfile, void * any)
{
	/*seq_printf(sfile,"1pid %d cpu0 %ld cpu1 %ld cpu2 %ld cpu3 %ld total %d\n",pid,per_pid_switch_counter[0],per_pid_switch_counter[1],per_pid_switch_counter[2],per_pid_switch_counter[3],per_pid_switch_counter[0]+per_pid_switch_counter[1]+per_pid_switch_counter[2]+per_pid_switch_counter[3]);
	seq_printf(sfile,"2pid %d prio %d static_prio %d normal_prio %d rt_priority %d\n",pid,prio1,prio2,prio3,prio4);
	seq_printf(sfile,"curr_cpu %d \n",curr_cpu);
	seq_printf(sfile,"Total time spent on cpu %d \n",total_time);*/
	seq_printf(sfile,"pc value %p \n",pcvalue);
	return 0;
}

static int proc_readings2(struct seq_file * sfile, void * any)
{
	seq_printf(sfile,"#: No of CS: cpu0 %ld cpu1 %ld cpu %ld cpu %ld\n",switches[0],switches[1],switches[2],switches[3]);
	seq_printf(sfile,"&: No of CS: cpu0 %ld cpu1 %ld cpu %ld cpu %ld\n",sched_counter[0],sched_counter[1],sched_counter[2],sched_counter[3]);
	seq_printf(sfile,"*: Length of RQ: cpu0 %ld cpu1 %ld cpu2 %ld cpu3 %ld\n",grqsize[0],grqsize[1],grqsize[2],grqsize[3]);
	seq_printf(sfile,"@@ NO_of_migration %ld \n",migration);
	return 0;
}
/******************************** proc file section end **************************************************************/

/******************************* *hook section start ***************************************************************/
int hk_context_counter(struct task_struct *next,struct task_struct *prev,int cpu,unsigned long switchh)
{
	sched_counter[cpu]++;
	if(next->pid == pid)
	{
		per_pid_switch_counter[cpu]++;
		curr_cpu=cpu;
		//entryy = tv_nsec;
	}
	else if(prev->pid == pid)
	{
		//exitt= tv_nsec;
		//total+= tv_nsec;
	}
	return 0;
}

int hk_current_pc(void *pc)
{
  if(current->pid == pid)
    pcvalue=pc;
}
int hk_rq_size(int cpu,unsigned int rqsize,unsigned long nr_switches)
{
	gcpu=cpu;
	grqsize[cpu]=rqsize;
	switches[cpu]=nr_switches;
	return 0;
}

int hk_per_pid_stats(struct task_struct *prev)
{	
	if(prev->pid == pid)
	{	
		tot = prev->se.sum_exec_runtime;
		migration = prev->se.nr_migrations;
		prio1 = prev->prio;
		prio2 =prev->static_prio;
		prio3= prev->normal_prio;
		prio4= prev->rt_priority;
		total_time=prev->se.sum_exec_runtime; 
	}
	return 0;
}

/*************************************** hook section end ***************************************************/

/************************************* init(void) and cleanup section start ******************************/
static int init(void)
{
	assi4_proc_file = proc_create("my_proc_file",0,NULL,&proc_file_operations);
	if(assi4_proc_file == NULL)
	{
		proc_remove(assi4_proc_file);
		printk(KERN_ALERT"ERROR : failed to create /proc/my_proc_file \n");
		return -1;
	}
	assi4_proc_file2 = proc_create("my_proc_file2",0,NULL,&proc_file_operations2);
	if(assi4_proc_file2 == NULL)
	{
		proc_remove(assi4_proc_file2);
		printk(KERN_ALERT"ERROR : failed to create /proc/my_proc_file2 \n");
		return -1;
	}
	printk(KERN_INFO"proc entry created \n");
	// asgining hook pointer
	context_counter = hk_context_counter;
	rq_size=hk_rq_size;  	
	per_pid_stats=hk_per_pid_stats;
	printk(KERN_INFO "inside the %s function\n", __FUNCTION__);
  	return 0;
}

static void  cleanup(void)
{
  	rq_size=NULL;
  	context_counter=NULL;
	per_pid_stats=NULL;
	proc_remove(assi4_proc_file);
	proc_remove(assi4_proc_file2);
  	printk(KERN_INFO "lkm removed\n");
}
/*********************************************init() cleanup() section end *******************************/

module_init(init);
module_exit(cleanup);
MODULE_AUTHOR("Abhishek Singh");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel tweaks");
