#copy5
import thread
import time
import threading

x=1
y=7

def thread2():
    print "thr2"
    y=9
try:
    thread.start_new_thread(thread2,())

except:
    print "Error: unable to start thread"


i=100000000
while i>0:
    i=i-1

print "y=",y
