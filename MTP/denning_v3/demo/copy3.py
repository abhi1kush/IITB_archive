#copy3 synchronization flow
import thread
import time
import threading

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

thread.start_new_thread(thread1,())
thread.start_new_thread(thread2,())
thread.start_new_thread(thread3,())

