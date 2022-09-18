import sys
import re

class const:
    otime = "*"   #u"\u2295"
    oplus = "+"   #u"\u2297"
    lt =    "<="  #u"\u2264"

def make_lub_string(llist): #assumption list containing string elemnts
    if len(llist) == 0:
        return 0
    if len(llist) == 1:
        return llist[0]
    tmp = set(llist)
    uniq_list = list(tmp)
    if len(uniq_list) == 1:
        return str(uniq_list[0])
    ret=""
    ret+=uniq_list[0]
    i=1
    while i < len(uniq_list):
        ret+=" "+ const.oplus +" "
        ret+=uniq_list[i]
        i=i+1
    return ret

def make_glb_string(llist): #assumption list containing string elemnts
    # type: (list) -> string
    if len(llist) == 0:
        return 0
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
        ret+=" "+ const.oplus +" "
        ret+=uniq_list[i]
        i=i+1
    return ret

def split_through_orelse(if_str):
    #find first body word
    i= if_str.find("body=[")
    i=parse_square_br(i+5,if_str)[1]+1
    return [if_str[0:i]+")",if_str[i+7:]]

def parse_keyword(i,data):
    # checking for
    if i + 4 < len(data) and data[i:i+5] == 'Expr(':
        return "Expr("
    if i+9 < len(data)-1 and data[i:i+9] == 'AugAssign':
        return "AugAssign"
    if i+6 < len(data)-1 and data[i:i+6] == 'Assign':
        return "Assign"
    if i+2 < len(data)-1 and data[i:i+2]=='If':
        return "If"
    if i+5 < len(data)-1 and data[i:i+5]=='While':
        return "While"
    return "none"

def parse_square_br(i,data):
    if data[i] != '[':
        print "Error: [ is missing"
        return []
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
    if data[i] != '(':
        print "Error: ( is missing"
        return []
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

def target_of_assignment(str): #find all targets
    #string->list
    targets_ptrn = r"targets=\[.*?\]"
    ctargets_ptrn = re.compile(targets_ptrn)
    temp_list=ctargets_ptrn.findall(str)
    ret = ''.join(temp_list) #converting to string
    return ret

def parse_variables(line):
    # type: (str) -> object
    id_index = [m.start() for m in re.finditer('id=',line)]
    var_list=[]
    for it in id_index:
        vname = extract_variavle_name(it + 4, line)
        if vname == "False" or vname == "True":
            continue
        var_list.append(vname)
    return var_list

def multiple_assign(parent_list,assign_str,target_id_index):
    tmp = assign_str.split("value",1)
    target_id_index = [m.start() for m in re.finditer('id=', tmp[0])]
    id_index = [m.start() for m in re.finditer('id=', tmp[1])]  # list of starting index of variables in right part of string
    rvalue = []
    if len(id_index) > 0:
        for it in id_index:
            startpos = it + 4
            rvalue.append(extract_variavle_name(startpos,tmp[1]))
    parent_list += rvalue
    dict={}
    local_dependency=[]
    for it in reversed(target_id_index):
        var_name = extract_variavle_name(it+4,assign_str)
        dict[var_name] = parent_list + local_dependency
        local_dependency.append(var_name)

    #printing denning's rule
    for key in dict:
        #left = make_lub_string(dict[key])
        if len(dict[key]) == 0:
            print "low " + const.lt + " "+key
        else:
            print make_lub_string(dict[key]),const.lt, key


def assign_denning(parent_list,assign_str):  # applying dennig's model on assignments
    ss = assign_str.split("value")
    target_id_index = [m.start() for m in re.finditer('id=', ss[0])]

    if len(target_id_index) > 1:
        multiple_assign(parent_list, assign_str, target_id_index)
        return 0

    if "id='" in ss[0]:
        left = extract_variavle_name(0,ss[0].split("id='")[1])
        #print "lvalue", left," ",
    else:
        left = ['const']
    id_index = [m.start() for m in re.finditer('id=',ss[1])] # list of starting index of variables in right part of string
    rvalue =[]
    if len(id_index) == 0:
        #rvalue.append("low")
        pass
    else:
        for it in id_index:
            startpos = it+4
            vname = extract_variavle_name(startpos, ss[1])
            """Exclusion of False keyword"""
            if vname == "False" or vname == "True":
                continue
            rvalue.append(vname)

    """Update local parent_list """
    parent_list += rvalue

    """Printing denning rules for stmts"""
    #print "= rvalues", rvalue, "parent_list", parent_list

    ret=""
    if len(parent_list) == 0:
            ret= "low" + " "+ const.lt +" "+left
    else:
		ret = make_lub_string(parent_list) + " "+ const.lt +" "+left
    print ret

def augAssign_denning(parent_list,augAssign_str):
    i=augAssign_str.find("id=")
    var_name = extract_variavle_name(i+4,augAssign_str)
    parent_list.append(var_name)
    assign_denning(parent_list[:],augAssign_str)

def if_denning(parent_list,if_str):
    # type: (list, string) -> dummylist
    if "orelse=" not in if_str:
        #print "termination",if_str
        if if_str[0:2] == "[]":      # absence of else part
            return []
        else:                        # handling else part
            else_str = if_str
            continuous_parse(parent_list[:],else_str)
            return []

    tmp = split_through_orelse(if_str)
    if_half = tmp[0]
    ladder = tmp[1]

    """extract compare from if_half"""
    i=if_half.find("Compare(")
    compare = parse_parenthesis(i+7, if_half)[0]
    i = parse_parenthesis(i+7, if_half)[1]
    parent_list += parse_variables(compare)
    #print parent_list

    """then extract body part and process like normal AST text """
    # body processing
    body_onward_str = if_half[i:]  ### Asumption : Compare string always followed by body=[...] imediatly
    # setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    body_str = parse_square_br(i, body_onward_str)[0]

    continuous_parse(parent_list[:],body_str)
    continuous_parse(parent_list[:],ladder)


def while_denning(parent_list,while_str):
    compare = "()"
    if while_str[6:10] == "Name":
        tmp = parse_parenthesis(10, while_str)
        compare = tmp[0]
        i = tmp[1]
    elif while_str[6:10] == "Comp":
        tmp = parse_parenthesis(13, while_str)
        compare = tmp[0]
        i = tmp[1]
        
    parent_list += parse_variables(compare)

    #body processing
    body_onward_str = while_str[i:]        ### Asumption : Compare string always followed by body=[...] imediatly
    #setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    body_str = parse_square_br(i,body_onward_str)[0]

    continuous_parse(parent_list[:],body_str)

def set_clear_denning(parent_list,expr_str):
    i = expr_str.find("Call(")
    i+=4
    call_str = parse_parenthesis(i,expr_str)[0]
    i = call_str.find("Attribute(")
    i += 9
    attribute_str = parse_parenthesis(i,call_str)[0]
    i = attribute_str.find("Name(")
    i += 4
    #name_str = parse_parenthesis(i,attribute_str)[0]
    i = attribute_str.find("id=")
    var_name = extract_variavle_name(i+4,attribute_str)
    i = attribute_str.find("attr=")
    attr = extract_variavle_name(i+6,attribute_str)
    if attr == "set":
        #treat it like AugAssign s0 += 1
        print make_lub_string(parent_list + [var_name]) + " <=  " + var_name
    elif attr == "clear":
        # treat it like AugAssign s0 -= 1
        print make_lub_string(parent_list + [var_name]) + " <= " + var_name
    else:
        pass
        #print "This Expr(...) is neither set nor clear"


#global var for counting
ww =ww1=ww2=1

def continuous_parse(parent_list,data):
    # type: (object, object) -> object
    length = len(data)
    i=0
    while i < length-1:
        #checking for keyword
        if parse_keyword(i,data) == "Expr(":
            i+=4
            tmp = parse_parenthesis(i, data)
            expr_str = tmp[0]
            i = tmp[1]
            set_clear_denning(parent_list[:],expr_str)
        if parse_keyword(i,data) == "AugAssign":
            i+=9
            tmp = parse_parenthesis(i,data)
            augAssign_str = tmp[0]
            i=tmp[1]
            augAssign_denning(parent_list[:],augAssign_str)
        if parse_keyword(i,data) == "Assign":
            global ww
            #print "Assign found",ww
            ww+=1
            i+=6
            tmp = parse_parenthesis(i,data)
            assign_str = tmp[0]
            i= tmp[1]
            if "value=Name(id='threading'" in assign_str:
                continue
            assign_denning(parent_list[:],assign_str)
        elif parse_keyword(i,data) == "If":
            global ww1
            #print "If found", ww1
            ww1 += 1
            i+=2
            tmp = parse_parenthesis(i,data)
            if_str = tmp[0]
            """if ww1 == 4 :
                print data
                print i,data[i:i+2]
                print if_str"""
            i = tmp[1]
            if_denning(parent_list[:],if_str)
        elif parse_keyword(i, data) == "While":
            global ww2
            #print "while found", ww2
            ww2 += 1
            i+=5
            tmp = parse_parenthesis(i,data)
            while_str = tmp[0]
            i= tmp[1]
            while_denning(parent_list[:],while_str)
        i+=1

################################### main #############################################
with open(sys.argv[1], "r") as inputfile:
    #data = inputfile.read().replace('\n', '').replace(' ','')
    data="".join(inputfile.read().split())
#print data
llist=[]
continuous_parse(llist[:],data)
#print "#if: ",ww1-1
#print "#while: ",ww2-1
#print "#assign: ",ww-1








