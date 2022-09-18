import sys
import re

def parse_variables(line):
    # type: (str) -> object
    id_index = [m.start() for m in re.finditer('id=',line)]
    var_list=[]
    for it in id_index:
        var_list.append(line[it+4])
    return var_list

list_of_if_var=[]
def if_denning(parent_if_list,line):
    #simple if
    if "orelse=" not in line:
        print "termination"
        return []
    ss = line.split("orelse=",1)
    if_half = ss[0]
    else_half = ss[1]
    temp = if_half.split("body=",1)
    if_condition = temp[0]
    if_body = temp[1]
    cond_var = parse_variables(if_condition)
    cond_var = cond_var + parent_if_list
    body_var = parse_variables(if_body)
    temp_list =[cond_var,body_var]
    list_of_if_var.append(temp_list)
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



################################### main ###########################################
with open(sys.argv[1], "r") as inputfile:
    data = inputfile.read().replace('\n', '').replace(' ','')

def target_of_assignment(line):
    #string->list
    targets_ptrn = r"targets=\[.*?\]"
    ctargets_ptrn = re.compile(targets_ptrn)
    temp_list=ctargets_ptrn.findall(line)
    ret = ''.join(temp_list)
    return ret




print target_of_assignment(data)

"""assign_pt1 = r'Assign.*?value=.*?[\d\)]\)\),'
cp1= re.compile(assign_pt1)
ll=cp1.findall(data)
for item in ll:
    print item


"""








