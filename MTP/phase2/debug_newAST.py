import sys
import re

def parse_keyword(i,data):
    # checking for
    if i+5 < len(data)-1 and data[i:i+6] == 'Assign':
        return "Assign"
    if i+2 < len(data)-1 and data[i:i+2]=='If':
        return "If"
    if i+4 < len(data)-1 and data[i:i+5]=='While':
        return "While"
    return "none"

def parse_square_br(i,data):
    ret ="["
    count=1
    i+=1
    while count > 0 and i< len(data) -1:
        if data[i] == '[':
            count +=1
        if data[i] == ']':
            count -=1
        ret += data[i]
        i+=1
    return [ret,i]


def parse_parenthesis(i,data):
    ret ="("
    count=1
    i+=1
    while count > 0 and i< len(data) -1:
        if data[i] == '(':
            count +=1
        if data[i] == ')':
            count -=1
        ret += data[i]
        i+=1
    return [ret,i]

def extract_variavle_name(startpos,line):
    #string->string
    var=""
    while line[startpos] != "'":
        var+=line[startpos]
        startpos=startpos+1
    return var

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


def assign_denning(parent_list,assign_str):  # applying dennig's model on assignments
    ss = assign_str.split("value")
    left = extract_variavle_name(0,ss[0].split("id='")[1])
    print "lvalue", left," ",
    id_index = [m.start() for m in re.finditer('id=',ss[1])] # list of starting index of variables in right part of string
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

def if_denning(parent_list,if_str):
    print if_str

ww = 1
gbody_str =""

def while_denning(parent_list,while_str):
    compare = parse_parenthesis(13,while_str)[0]
    i = parse_parenthesis(13,while_str)[1]
    print "inside while_denning value of i after compare",i
    parent_list += parse_variables(compare)
    print parent_list

    #body processing
    body_onward_str = while_str[i:]
    #print body_onward_str                               ### Asumption : Compare string always followed by body=[...] imediatly
    #setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    print "inside while_denning value of i after body_onward", i
    tmp = parse_square_br(i,body_onward_str)
    body_str = tmp[0]
    i = tmp[1]
    print "inside while_denning value of i after body_str", i
    print body_str[i:]
    #print body_str
    global gbody_str
    gbody_str=body_str
    continuous_parse(parent_list,0,body_str)
    print "END!!!!! of while_denning"

cc=1
def continuous_parse(parent_list,i,data):
    global cc
    print "In Continuos Parse", cc, "value of i",i
    cc+=1
    if len(parent_list) >0:
        print "nested",parent_list
    else:
        print "Not nested",parent_list
    length = len(data)
    while i < length-1:
        print "value of i",i
        #checking for keyword
        if parse_keyword(i,data) == "Assign":
            i+=6
            tmp = parse_parenthesis(i,data)
            assign_str = tmp[0]
            i= tmp[1]
            assign_denning(parent_list,assign_str)
        elif parse_keyword(i,data) == "If":
            i+=2
            tmp = parse_parenthesis(i,data)
            if_str = tmp[0]
            i = tmp[1]
            if_denning(parent_list,if_str)
        elif parse_keyword(i, data) == "While":
            print "Found While",ww
            global ww
            ww+=1
            i+=5
            tmp = parse_parenthesis(i,data)
            while_str = tmp[0]
            i= tmp[1]
            while_denning(parent_list,while_str)
        i+=1
    print "Exiting Continuos parse"," i ",i

################################### main #############################################
with open(sys.argv[1], "r") as inputfile:
    #data = inputfile.read().replace('\n', '').replace(' ','')
    data="".join(inputfile.read().split())
#bbody ="body=[Assign(targets=[Name(id='var_c', ctx=Store()),], value=Num(n=2)),While(test=Compare(left=Name(id='cond2', ctx=Load()),ops=[Gt(),], comparators=[Num(n=0),]),body=[Assign(targets=[Name(id='var_c',ctx=Store()),], value=Num(n=1)),While(test=Compare(left=Name(id='cond3', ctx=Load()), ops=[Gt(),], comparators=[Num(n=0),]), body=[Assign(targets=[Name(id='var_c', ctx=Store()),], value=Num(n=4)),], orelse=[]),], orelse=[]),While(test=Compare(left=Name(id='cond4', ctx=Load()), ops=[Gt(),], comparators=[Num(n=0),]), body=[Assign(targets=[Name(id='var_c', ctx=Store()),], value=Num(n=0)),], orelse=[]),]"
print data
continuous_parse([],0,data)
print "\n\n\n"
print gbody_str
continuous_parse([],0,gbody_str)







