import ast
import sys

# making string from file
f = open(sys.argv[-1],'r')
ss = ''	
ss = ''.join(line for line in f)
f.close()

#parse
t = ast.parse(ss)

# astdump file name
filename = "astdump_of_"+sys.argv[-1]+".txt"
# redirect to file
opstream = sys.stdout
sys.stdout = open(filename,'w')

print ast.dump(t)

sys.stdout = opstream
print ast.dump(t)

