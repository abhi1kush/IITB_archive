#copy6
import thread
import time
import threading
import sys

x= 5
z=1
sum=23
y= 0

def copy6():
    global z
    global sum
    global y

    z = 0
    sum = 0
    y = 0

    while z == 0 :
        sum = sum + x
        y = y + 1

thread.start_new_thread(copy6,())

