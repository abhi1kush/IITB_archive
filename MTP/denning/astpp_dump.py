import ast
import astpp
import sys

if len(sys.argv) != 2:
	print "Error: Pass filename as argu"
	sys.exit()
# making string from file
f = open(sys.argv[-1],'r')
ss = ''	
ss = ''.join(line for line in f)
f.close()

#parse
t = ast.parse(ss)

# astdump file name
filename = "astppdump_of_"+sys.argv[-1]+".txt"
# redirect to file
opstream = sys.stdout
sys.stdout = open(filename,'w')

print astpp.dump(t)

sys.stdout = opstream
print astpp.dump(t)

