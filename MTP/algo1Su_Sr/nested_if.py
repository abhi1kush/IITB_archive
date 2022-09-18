a=1
b=8
c=6
if a>b:
	if b>c:
		print "c is smallest"
	else: # a>b and c>b
		print "b is smallest"
else:
	if a>c:
		print "c is smallest"
	else: # b>a and c>a
		print "a is smallest"
