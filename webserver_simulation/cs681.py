#!/usr/bin/python

import random
import Queue
import heapq
import time
import sys
############ global var  and default value#############
thread_queue_size = 1000
no_of_clients = 20
timeout_min = 15
timeout_period = timeout_min
timeout_lambda = 0.6
context_switch = 1
size_of_threadpool=1000
servicetime_option =2 #1 for uniform-----2 for exponential------3 for constant###
a=2 # for uniform distribution
b=10 # for uniform distribution
servicetime_lambda =0.5
simulation_time_per=500
no_of_cores = 4
global_quantum_size=2
seedd=2
thinktime_constant=5
thinktime_a=3
thinktime_b=12

########################################
response_out = open("response.txt","a")
through_out = open("through_out.txt","a")
drop_out=open("drop_out.txt","a")
util_out=open("util_out.txt","a")
#########taking input from file#########
with open("sim_input.txt","r") as inputfile:
    for lline in inputfile:
                line=lline.split()
                if len(line) == 0 or len(line) ==1:
                    continue
                if line[0] == "simulation_time_per":
                    simulation_time_per=float(line[1])
                if line[0] == "seed":
                    seedd=int(line[1])
                if line[0] == "thread_queue_size":
                    thread_queue_size=int(line[1])
                elif line[0] == "no_of_clients":
                    no_of_clients=int(line[1])
                elif line[0] == "timeout_min":
                    timeout_min = float(line[1])
                elif line[0] == "timeout_lambda":
                    timeout_period = float(line[1])
                elif line[0] == "context_switch":
                    context_switch=float(line[1])
                elif line[0] == "size_of_threadpool":
                    size_of_threadpool=int(line[1])
		elif line[0] == "thinktime_a":
                    thinktime_a=int(line[1])
		elif line[0] == "thinktime_b":
                    thinktime_b=int(line[1])
                elif line[0] == "thinktime_constant":
                    thinktime_constant=int(line[1])
                elif line[0] == "servicetime_option":
                    servicetime_option =int(line[1])
                elif servicetime_option ==1 and line[0] == "a":
                    a=float(line[1])
                elif servicetime_option ==1 and line[0] == "b":
                    b=float(line[1])
                elif servicetime_option ==2 and line[0] == "servicetime_lambda":
                    servicetime_lambda=float(line[1])
                elif servicetime_option ==3 and line[0] == "servicetime_lambda":
                    servicetime_lambda=float(line[1])
                elif line[0] == "quantum_size":
                    global_quantum_size=float(line[1])
                elif line[0] == "no_of_cores":
                    no_of_cores=int(line[1])

######## timeout distribution ############
def timeout_per():
    timeout_period = random.expovariate(timeout_lambda)
    if timeout_period < timeout_min:
        timeout_period = timeout_min
    return timeout_period

def thinktime():
    if thinktime_constant == -1:
        return random.uniform(thinktime_a,thinktime_b)
    else:
        return thinktime_constant
############ stats class #################################
class stats:
	response_start =0
	response_end =0
	response_time =0
	response_count=0
	throughput =0
	goodput=0
	badput = 0
	droprate=0
	server_utilization=0
        present=0
        last_departure=0
        drop=0
        arrived=0

################### event class ################## 
class event:
	eventqueue=Queue.PriorityQueue()
	def addintoqueue(self,timestamp,object_req,event_type):
		event.eventqueue.put((timestamp,object_req,event_type))

################## cores class ####################
class cores:
    temp=0
    def __init__(self,qntm_size=2):
        self.core_id = cores.temp + 1
        cores.temp += 1
        self.q=Queue.Queue() # queue for thread
        self.quantum_time = qntm_size
	self.utilization=0
	self.startU=0
	self.endU=0
	self.total=0

########################### server class ##############

class server:
    response=0
    response_count=0
    threadpool= {}
    k=1
    for x in range(0,size_of_threadpool):
        threadpool[x] = 0
    thread_queue=Queue.Queue(thread_queue_size)

    def allocate_thread(self,req_obj):
        self.flag=0
        self.thread_id = -1
        for key in server.threadpool:
            if server.threadpool[key] == 0:
                self.flag=1
                self.thread_id = key
                break
        if(self.flag == 1):
            server.threadpool[self.thread_id] = req_obj.req_id
            req_obj.thread_id = self.thread_id
            return self.thread_id
        else:
            return -1
############################### request class #####################
class request:
	temp=1
        time = 0
	def __init__(self,ts):
		self.req_id = request.temp
		request.temp += 1
                self.timeout_done=0
		#self.thinktime = thinktime_lambda #this is user input...constant think time
                #request.time += self.thinktime
                self.timestamp = ts 
                self.thread_id = -1
                self.core = -1
                self.depart = -1
		self.timeout_counter=0
		if servicetime_option == 1: 		# for uniform distribution
                	self.total_servicetime = random.uniform(a,b)
		elif servicetime_option == 2: 		# for exponential distribution
                	self.total_servicetime = random.expovariate(servicetime_lambda)
		else:					# for constant service time
			self.total_servicetime = servicetime_lambda
		self.remaining_service_time = self.total_servicetime
	
        def departed(self):
                self.depart = 1
        def isdeparted(self):
                return self.depart
        def assign_core(self,core_obj):
            self.core = core_obj
        def ret_coreobj(self):
            return self.core
	#def response(departure_time):
        #	return departure_time - self.timestamp 
	
################################## request class end ######################
clock=0
current_event="nothing"
current_req_id=-1
current_thread_id=-1
server_obj=server()#call to class to server...which only initialize obs object

#creating four core objects 
core= {}
i=0
for x in range(1,no_of_cores + 1):
    core[x]= cores(global_quantum_size) # quantum size as an arg

# function to find minimum core queue size to dynamically alocate core.
def min_corequeue():
    minn=core[1].q.qsize()
    # index of least busy core
    min_core = 1
    for key in core:
        temp = core[key].q.qsize()
        if minn > temp :
            minn = temp
            min_core = key
    return min_core
###############################

def setevent(req_obj):
	if(req_obj.remaining_service_time <= req_obj.core.quantum_time):
		event_obj.addintoqueue(clock+req_obj.remaining_service_time+context_switch,req_obj,"depar")
		req_obj.remaining_service_time=0
		#set departure event and add into queue
	else:
		ts=clock+req_obj.core.quantum_time+context_switch
		event_obj.addintoqueue(ts,req_obj,"qdone")
		req_obj.remaining_service_time-=req_obj.core.quantum_time
		#set quantum_done event and add into queue




def arrival(req_obj):
        stats.arrived+=1
	if server_obj.thread_queue.full():
                stats.drop+=1
		return -1
	else:
            # check for availablity of thread
            thread_no = server_obj.allocate_thread(req_obj)
            if thread_no != -1:
		ret = min_corequeue()
                #find core object(k's core object) of any core
		req_obj.core=core[ret]#inititalize req_obj.core
		req_obj.thread_id=thread_no#iititalize req_obj.thread_id
		#check that core_obj's queue==empty
		if core[ret].q.empty():
			#call that_function1
			core[ret].startU=clock
			setevent(req_obj)
		#put req_obj into queue of core_obj
		core[ret].q.put(req_obj)
	    else:
		#put req_obj into thread's queue
		server_obj.thread_queue.put(req_obj)

def processreq(req_obj):
	ret = min_corequeue()
        #find core object(k's core object) of any core
	req_obj.core=core[ret] #inititalize req_obj.core
	#check that core_obj's queue==empty
	if core[ret].q.empty():
		#call that_function2
		setevent(req_obj)
	#put req_obj into queue of core_obj
	core[ret].q.put(req_obj)



def departure(core_obj,req_obj):
	stats.present-=1
	if stats.present == 0:
		exit
        if req_obj.timeout_done == 1:
            stats.badput+=1
        else:
            stats.goodput+=1
        stats.last_departure=clock
        #server_obj.release_thread(thread_id)
	server_obj.threadpool[req_obj.thread_id] = 0
	#give this thread to next req waiting in thread_queue
	if not server_obj.thread_queue.empty():
		thr_obj=server_obj.thread_queue.get()
                thr_obj.thread_id=req_obj.thread_id
                #print core_obj.endU,core_obj.startU
		server_obj.threadpool[req_obj.thread_id]=thr_obj.req_id
		processreq(thr_obj)
        req_obj.thread_id = -1
        if not core_obj.q.empty():
            myobj=core_obj.q.get()#get the first departed event and discard it
	    core_obj.endU=clock
	    core_obj.total+=(core_obj.endU-core_obj.startU)
	    stats.response_time+=clock - myobj.timestamp
	    #server.response+=(clock-myobj.response_start[myobj.req_id])#strores end time of departed request 
	    stats.response_count += 1
        if not core_obj.q.empty():
  		temp_obj=list(core_obj.q.queue)[0]
		core_obj.startU=clock
		#call that_fucntion3
	    	setevent(temp_obj)
        req_obj.depart = 1
	thinktimee = thinktime()
	next_arrival = request(clock + thinktimee)
        event_obj.addintoqueue(clock + thinktimee,next_arrival,"arriv")
        event_obj.addintoqueue(clock + thinktimee + timeout_per() ,next_arrival,"timeo")


def quantum_done(core_obj,req_obj):
        #dequeue from core queue and add at the end
        if not core_obj.q.empty():
            temp_obj=core_obj.q.get()
	    core_obj.q.put(temp_obj)
        if not core_obj.q.empty():
            first_obj=list(core_obj.q.queue)[0]
            #print "inside quantumdone : ",req_obj.req_id,"remaining_service_time : ",req_obj.remaining_service_time
	    #call that_fucntion4
	    setevent(first_obj)

def timeout_handler(req_obj):
        if req_obj.depart == 1:
            return 1
        else:
            req_obj.timeout_done=1
            #client sends request again
            req_obj.timeout_counter+=1
            #req_obj.timestamp = clock
            req_obj.remaining_service_time=req_obj.total_servicetime
            event_obj.addintoqueue(clock,req_obj,"arriv")
            event_obj.addintoqueue(clock + timeout_per() ,req_obj,"timeo")
	    stats.present+=1
            stats.arrived+=1


print "request_id | clock | total service time | remaining sevice time | thread queue size | core "

event_obj=event()#Add request into queue
clock=0
random.seed(seedd)
for x in range(1,no_of_clients+1):
    thinktimee = thinktime()
    req_obj=request(thinktimee)			#For request Generation
    event_obj.addintoqueue(clock + thinktimee,req_obj,"arriv")
    event_obj.addintoqueue(clock + thinktimee + timeout_per() ,req_obj,"timeo")
    stats.present+=1
while clock < simulation_time_per:
        flag = 1
        if event_obj.eventqueue.qsize() > 0:
            event_l = event_obj.eventqueue.get()
            clock=event_l[0]
            req_obj=event_l[1]
            current_event=event_l[2]
            rem_servicetime = req_obj.remaining_service_time
            if current_event == "timeo" and req_obj.depart == 1:
                flag = 0
        else:
            print "event list empty"
            break
        if current_event == "arriv":
            arrival(req_obj)       #for ARRIVAL
        elif current_event == "depar":
            departure(req_obj.core,req_obj) #for DEPARTURE
            req_obj.departed()
        elif current_event == "qdone":	    # for quantum done
            quantum_done(req_obj.core,req_obj)
        elif current_event == "timeo":      # for timeout
            timeout_handler(req_obj)
        #if flag == 1:
            #print current_event,":",req_obj.req_id," | ",clock," | ",req_obj.total_servicetime," | ",rem_servicetime,"|",server_obj.thread_queue.qsize(),
            #if req_obj.core != -1:
            #    print "|",req_obj.core.core_id
            #else:
            #    print "| waiting in thread queue"
response_out.write(str(stats.response_time/stats.response_count)+"\n")
#print stats.goodput,stats.badput
through_out.write(str(stats.goodput/stats.last_departure)+"\t") 
through_out.write(str(stats.badput/stats.last_departure)+"\n")
#print stats.response_time/stats.response_count,"hi"
drate = float(stats.drop)/stats.arrived
drate = drate * 100
drop_out.write(str(stats.drop)+"\t")
drop_out.write(str(stats.arrived)+"\t")
drop_out.write(str(drate)+"\n")
sum1=0
for x in range(1,no_of_cores+1):
	sum1=sum1+((float(core[x].total)/simulation_time_per)*100)
        #print sum1,core[x].total
avgU=float(sum1)/no_of_cores
#print "avg utilization : ", avgU
util_out.write(str(avgU)+"\n")
util_out.close()
response_out.close()
through_out.close()
drop_out.close()

