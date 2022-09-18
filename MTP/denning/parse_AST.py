import sys
import re

def extract_variavle_name(startpos,line):
    #string->string
    var=""
    while line[startpos] != "'":
        var+=line[startpos]
        startpos=startpos+1
    return var

def make_lub_string(llist): #assumption list containing string elemnts
    if len(llist) == 1:
        return llist[0]
    tmp = set(llist)
    uniq_list = list(tmp)
    if len(uniq_list) == 1:
        return uniq_list[0]
    ret=""
    ret+=uniq_list[0]
    i=1
    while i < len(uniq_list):
        ret+=" "+u"\u2295"+" "
        ret+=uniq_list[i]
        i=i+1
    return ret

def make_glb_string(llist): #assumption list containing string elemnts
    # type: (list) -> string
    if len(llist) == 1:
        return llist[0]
    tmp = set(llist)
    uniq_list = list(tmp)
    if len(uniq_list) == 1:
        return uniq_list[0]
    ret=""
    ret+=uniq_list[0]
    i=1
    while i < len(uniq_list):
        ret+=" "+u"\u2297"+" "
        ret+=uniq_list[i]
        i=i+1
    return ret

def assign_denning(line):  # applying dennigs model on assignments
    ss = line.split("value")
    left = extract_variavle_name(0,ss[0].split("id='")[1])
    print "lvalue", left," ",
    id_index = [m.start() for m in re.finditer('id=',ss[1])] # list of starting index of variables in string line
    rvalue =[]
    if len(id_index) == 0:
        rvalue.append("low")
    else:
        for it in id_index:
            startpos = it+4
            rvalue.append(extract_variavle_name(startpos,ss[1]))
    print "= rvalues",rvalue
    ret=""
    if len(rvalue) == 1:
            ret= rvalue[0] + " "+ u"\u2264"+" "+left
    else:
        inx = 0
        while inx < len(rvalue):
            ret+=str(rvalue[inx])
            ret+=" "+ u"\u2295"+" "
            inx=inx+1
        ret+= " "+ u"\u2264"+" "+left
    print ret

def target_of_assignment(line):
    #string->list
    targets_ptrn = r"targets=\[.*?\]"
    ctargets_ptrn = re.compile(targets_ptrn)
    temp_list=ctargets_ptrn.findall(line)
    ret = ''.join(temp_list) #converting to string
    return ret

def parse_variables(line):
    # type: (str) -> object
    id_index = [m.start() for m in re.finditer('id=',line)]
    var_list=[]
    for it in id_index:
        var_list.append(extract_variavle_name(it+4,line))
    return var_list

list_of_if_var=[]
def if_denning(parent_if_list,line):
    # type: (list, string) -> dummylist
    if "orelse=" not in line:
        #print "termination",line
        if line[0:2] == "[]":        # absence of else part
            return []
        else:                        # handling else part
            else_var = parse_variables(target_of_assignment(line))
            list_of_if_var.append([parent_if_list,else_var])
            return []
    ss = line.split("orelse=",1)
    if_half = ss[0]
    else_half = ss[1]
    temp = if_half.split("body=",1)
    if_condition = temp[0]
    if_body = temp[1]
    cond_var = parse_variables(if_condition)
    cond_var = cond_var + parent_if_list
    body_var = parse_variables(target_of_assignment(if_body))
    list_of_if_var.append([cond_var,body_var]) # appending list of lists [cond_var,body_var]
    return if_denning(cond_var,else_half)

def assign_string(startpos,str):
    counter=1
    i=startpos+1
    while counter>=1:
        if data[i] == "(":
            counter = counter + 1
        if data[i] == ")":
            counter = counter -1
        i=i+1
    endpos=i
    return data[startpos:endpos]

def process_unnested_if_var_list( ll ):
#ll is of list of lists of lists containing two list elements
# [ { [[cond_var],[body_var]] , [[cond_var],[body_var]] , [[cond_var],[body_var]] }, { [[cond_var],[body_var]] } ]
    for ifladder in ll:
        for ifs in ifladder:
            print make_lub_string(ifs[0])+" "+ u"\u2264"+" "+make_glb_string(ifs[1])

def remove_prefix(text, prefix):
    return re.sub(r'^{0}'.format(re.escape(prefix)), '', text)

while_index=[]
def search_next(while_index,pos):
    for it in while_index:
        if pos <= it:
            return it
    return -1

def make_while_list(pos,str,while_list,while_index):
    if "While" not in str[pos:]:
        return []
    else:
        pos = search_next(while_index,pos)
        temp=assign_string(pos+5,str)
        pos+=(len(temp)+5)
        while_list.append(temp[:])
        return make_while_list(pos,str,while_list,while_index)

list_of_while_var = []
def while_denning(parent_while_list, line):
        # type: (list, string) -> dummylist
        count = 1
        i = 1
        while count > 0 and i < len(line):
            if line[i] == "(":
                count +=1
            if line[i] == ")":
                count -= 1



################################### main #############################################
with open(sys.argv[1], "r") as inputfile:
    data = inputfile.read().replace('\n', '').replace(' ','')

assign_index=[m.start() for m in re.finditer('Assign',data)]
if_index = [m.start() for m in re.finditer(',If',data)] # used ,If for parsing non nested ifs

assign_list = []
if_list =[]
for item in assign_index:
    assign_list.append(assign_string(item+6,data))
for item in if_index:
    if_list.append(assign_string(item+3,data))
#variables of all distinct(not nested) if
unnested_if_var_list=[]

for it in if_list:
    if_denning([],it) #producing output in global list list_of_if_var
    unnested_if_var_list.append(list_of_if_var[:])  ## list_of_if_var call by refrence  list_of_if_var[:] call by value
    del list_of_if_var[:]
#print unnested_if_var_list

#print "denning's rule for if else"
#process_unnested_if_var_list(unnested_if_var_list)
while_index = [m.start() for m in re.finditer("While", data)]
#making while list
while_list=[]
make_while_list(0,data[:],while_list,while_index)
for it in while_list:
    print it

unnested_while_var_list=[]
for it in while_list:
    while_denning([],it) #producing output in global list list_of_if_var
    unnested_while_var_list.append(list_of_while_var[:])  ## list_of_if_var call by refrence  list_of_if_var[:] call by value
    del list_of_while_var[:]
#print unnested_if_var_list


#######################################################################################
#for i in assign_list:
#    print i
"""for i in if_list:
    print i"""

"""for it in assign_list:
    assign_denning(it)"""

"""assign_pt1 = r'Assign.*?value=.*?[\d\)]\)\),'
cp1= re.compile(assign_pt1)
ll=cp1.findall(data)
for item in ll:
    print item


"""








