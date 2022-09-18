#copy5
import thread
import time
import threading
import sys

x= 5
z=1
sum=23
y= 0

def copy6():
    print "thr1"

    global z
    global sum
    global y

    z = 0
    sum = 0
    y = 0

    while z == 0 :
        try:
            sum = sum + x
        except OverflowError:
            print "sum overflow :", sum
        y = y + 1


try:
    thread.start_new_thread(copy6,())


except:
    print "Error: unable to start thread"


i=100000000
while i>0:
    i=i-1

print "y",y,"Max/y=",sys.maxint/y, "sum :",sum
