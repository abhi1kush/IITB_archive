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

low <= s0
low <= s1
x + s0 <=  s0
x + s1 <=  s1
s0 <= s0
low <= y
s1 <=  s1
s1 <= s1
low <= y
s0 <=  s0
