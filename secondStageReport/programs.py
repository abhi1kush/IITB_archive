###############################################
#Procedure copy1
#z=0
#y=0
if x == 0:
	z=1
if z==0:
	y=1

###############################################
# Procedure copy2
z = 1
y = -1
while z == 1:
	y = y + 1
	if y == 0:
		z = x
	else:
		z = 0

###############################################
#copy3 synchronization flow
import thread
import time
import threading

#x=7
#y=6
#def copy3(x,y):     # copy x to y
s0 = threading.Event()
s1 = threading.Event()

def thread1():
    global x
    if x==0:
        s0.set()
    else:
        s1.set()

def thread2():
    global y
    s0.wait()
    s0.clear()
    y=1
    s1.set()

def thread3():
    global y
    s1.wait()
    s1.clear()
    y=0
    s0.set()

try:
    thread.start_new_thread(thread1,())
    thread.start_new_thread(thread2,())
    thread.start_new_thread(thread3,())
except:
    print "Error: unable to start thread"

###############################################
#copy4 Global flow in concurrent programs
import thread
import time
import threading


def thread1():
    global x
    global e0
    global e1
    if x==0:
        e0 = False
    else:
        e1 = False

def thread2(): 
    global e0
    global e1
    global y
    while e0:
        pass

    y = 1
    e1 = False

def thread3():
    global e1
    global e0
    global y
    while e1:
        pass
    y = 0
    e0 = False

try:
    thread.start_new_thread(thread1,())
    thread.start_new_thread(thread2,())
    thread.start_new_thread(thread3,())
except:
    print "Error: unable to start thread"


#copy5
y = 0
while x==0 :
	pass
y = 1

###############################################
#copy 6
z = 0
sum = 0
y = 0
while z == 0 :
	sum = sum + x       
        y = y + 1

###############################################
#dynamic label
def fun(x, y, z):
    a = x
    y = a
    a = z
fun(x, y, z)
