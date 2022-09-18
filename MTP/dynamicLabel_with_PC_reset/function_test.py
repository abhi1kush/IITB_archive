a = b
b = z + c
def fun1(b):
    global b
    global a
    i = b
    j = a
    a = k
    return a

def fun2(b):
    global b
    global a
    ii = b
    jj = a
    a = kk
    fun1(jj)

fun1(a)
fun2(b)

