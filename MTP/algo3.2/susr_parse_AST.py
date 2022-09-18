import sys
import re

class const:
    otime = "*"   #u"\u2295"
    oplus = "+"   #u"\u2297"
    lt =    "<="  #u"\u2264"

def make_lub_string(llist): #assumption list containing string elemnts
    if len(llist) == 0:
        return "Low"
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
        return "High"
    if len(llist) == 1:
        return llist[0]
    uniq_list = list(set(llist))
    if len(uniq_list) == 1:
        return uniq_list[0]
    ret=""
    ret+=uniq_list[0]
    i=1
    while i < len(uniq_list):
        ret+=" "+ const.otime +" "
        ret+=uniq_list[i]
        i=i+1
    return ret

def split_through_orelse(if_str):
    # find first body word
    i = if_str.find("body=[")
    i = parse_square_br(i + 5, if_str)[1] + 1
    return ["{" + if_str[1:i] + "}", if_str[i + 7:]]

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
    if i + 11 < len(data) - 1 and data[i:i + 11] == 'FunctionDef':
        return "FunctionDef"
    return "none"

def parse_square_br(i,data):
    if data[i] != '[':
        print "Error: [ is missing", "data:", data, i
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

def multiple_assign(parent_list, global_while_list, assign_str, target_id_index):
    Su = []
    Sr = []
    tmp = assign_str.split("value", 1)
    Su = parse_variables(tmp[0])
    Sr = parse_variables(tmp[1])
    return [Su,Sr,Sr]

def assign_denning(assign_str):  # applying dennig's model on assignments
    Su = []
    Sr = []
    ss = assign_str.split("value")
    target_id_index = [m.start() for m in re.finditer('id=', ss[0])]

    if len(target_id_index) > 1:
        multiple_assign(assign_str, target_id_index)
        return 0

    if "id='" in ss[0]:
        Su.append(extract_variavle_name(0,ss[0].split("id='")[1]))
        #print "lvalue", left," ",
    else:
        left = ['const']
    id_index = [m.start() for m in re.finditer('id=',ss[1])] # list of starting index of variables in right part of string
    eLabel =[]
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
            eLabel.append(vname)
    Sr = eLabel
    print "Verify '=' :", make_lub_string(eLabel), "<=", make_glb_string(Su)
    return [Su,Sr,eLabel]

def augAssign_denning(parent_list,augAssign_str):
    Sr = parse_variables(augAssign_str)
    Su = [Sr[0]]
    print "Verify '=' :", make_lub_string(Sr) ,"<=", make_glb_string(Su)
    return [Su,Sr,Sr]

def if_denning(if_str):
    # type: (list, string) -> dummylist
    Su = []
    Sr = []
    eLabel = []
    if "orelse=" not in if_str:
        #print "termination",if_str
        if if_str[0:2] == "[]":      # absence of else part
            return [[],[],[]]
        else:                        # handling else part
            else_str = if_str
            S = susr_continuous_parse(else_str)
            Su = S[0]
            Sr = S[1]
            return [Su,Sr,[]]

    tmp = split_through_orelse(if_str)
    if_half = tmp[0]
    ladder = tmp[1]

    if if_str[1:5] != "test":
        print "Error test not found in if"

    """extract test=...() from if_half"""
    i = if_half.find("(")

    tmp = parse_parenthesis(i, if_half)
    test_str = tmp[0]
    eLabel += parse_variables(test_str)
    i = tmp[1]


    """then extract body part and process like normal AST text """
    # body processing
    body_onward_str = if_half[i:]
    # setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    body_str = parse_square_br(i, body_onward_str)[0]

    S1 = susr_continuous_parse("",{},body_str,"if")
    S2 = susr_continuous_parse("",{},ladder,"if")
    #print S1,S2
    if not S1 and not S2:
        Su = Sr = []
    elif S1 and not S2:
        Su = S1[0]
        Sr = S1[1]
    elif S2 and not S1:
        Su = S2[0]
        Sr = S2[1]
    else:
        Su = S1[0] + S2[0]
        Sr = S1[1] + S2[1]

    #print S2,ladder
    print "Verify if:", make_lub_string(eLabel), "<=", make_glb_string(Su)
    return [Su,Sr+eLabel,eLabel]

def while_denning(while_str):
    Su = []
    Sr = []
    eLabel = []
    compare = "()"
    if while_str[6:10] == "Name":
        tmp = parse_parenthesis(10, while_str)
        compare = tmp[0]
        i = tmp[1]
    elif while_str[6:10] == "Comp":
        tmp = parse_parenthesis(13, while_str)
        compare = tmp[0]
        i = tmp[1]
        
    eLabel += parse_variables(compare)

    #body processing
    body_onward_str = while_str[i:]        ### Asumption : Compare string always followed by body=[...] imediatly
    #setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    body_str = parse_square_br(i,body_onward_str)[0]

    S1 = susr_continuous_parse("",{},body_str,"while")
    Su += S1[0]
    Sr += S1[1] + eLabel
    print "Verify while :", make_lub_string(Sr + eLabel), "<=", make_glb_string(Su)
    return [Su,Sr,eLabel]

def set_clear_denning(called_by_fun,fun_global,expr_str):
    Su = []
    Sr = []
    eLabel = []
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
        Su = Sr = [var_name]
        print "verify set", var_name + " <=  " + var_name
        #print [Su,Sr,eLabel]
        return [Su,Sr,eLabel]
    elif attr == "clear":
        # treat it like AugAssign s0 -= 1
        Su = Sr = [var_name]
        print "verify clear", var_name + " <=  " + var_name
        return [Su, Sr, eLabel]
    elif attr == "wait":
        eLabel = [var_name]
        return [[],eLabel,eLabel]


def print_su_list(Slist,i):
    #print "\n-->",Slist
    tmp =[]
    while i < len(Slist):
        if not Slist[i]:
            i += 1
            continue
        tmp += Slist[i][0]
        i += 1
    return make_glb_string(tmp)

PCLabel = []
def seq(Slist,tag):
    #print "Slist", Slist
    if Slist and not Slist[0]:
        return [[],[],[]]
    if len(Slist) == 0 or ( len(Slist[0]) == 0 and len(Slist[1]) == 0 ):
        return [[],[],[]]
    if len(Slist) == 1:
        return Slist[0]
    Su = []
    Sr = []
    i = 0
    while i < len(Slist):
        if not Slist[i]:
            i += 1
            continue
        Su += Slist[i][0]
        Sr += Slist[i][1]
        if i < len(Slist) - 1:
            print "Verify in",tag,"seq",i,":", make_lub_string(Slist[i][1]), "<=", print_su_list(Slist,i+1)
        i += 1
    #print "---->",Su
    #print "Verify PC :", make_lub_string(PCLabel), "<=", make_glb_string(Su)
    #PCLabel += Sr
    return [list(set(Su)),list(set(Sr)),[]]

def extract_Globals(fun_str):
    global_index = [m.start() for m in re.finditer("Global\(", fun_str)]
    #debug print fun_str,global_index
    globals = {}
    for it in global_index:
        global_str = parse_parenthesis(it + 6, fun_str)[0]
        #debug print global_str
        sq_str = parse_square_br(global_str.find("["), global_str)[0]
        ss = sq_str.strip("[").strip("]")
        sslist = ss.split(",")
        #print sslist
        for it in sslist:
            if it == '':
                continue
            globals[(it.strip("'"))] = 1
    #debug print globals
    return globals

#global var for counting
ww = ww1 = ww2 = 1

def fun_denning(fun_str):
    S = []
    global PCLabel
    PCLabel = []
    fun_name = extract_variavle_name(fun_str.find("name=") + 6, fun_str)
    # print fun_name
    fun_globals = extract_Globals(fun_str)
    fun_globals.update(supreme_global)
    # print globals
    fun_global_while = []
    susr_continuous_parse(fun_name, fun_globals, fun_str,"function")

supreme_global = {}

def susr_continuous_parse(called_by_fun,fun_global,data,tag):
    S = []
    count = 0
    global PCLabel
    # type: (object, object) -> object
    length = len(data)
    i=0
    #print data
    while i < length-1:
        #checking for keyword
        if parse_keyword(i, data) == "FunctionDef":
            #print "fun::::::::::::",called_by_fun
            tmpPC = PCLabel
            i += 11
            tmp = parse_parenthesis(i, data)
            fun_str = tmp[0]
            i = tmp[1]
            global_while_list = []
            fun_denning(fun_str)
            PCLabel = tmpPC
        elif parse_keyword(i, data) == "Expr(":                    #NEED generlization
            i += 4
            tmp = parse_parenthesis(i, data)
            expr_str = tmp[0]
            i = tmp[1]
            S.append(set_clear_denning(called_by_fun, fun_global, expr_str))
        elif parse_keyword(i,data) == "AugAssign":
            i+=9
            tmp = parse_parenthesis(i,data)
            #print parse_parenthesis(i,data)
            augAssign_str = tmp[0]
            i=tmp[1]
            #print augAssign_denning(augAssign_str)
            S.append(augAssign_denning(augAssign_str))
        elif parse_keyword(i,data) == "Assign":
            global ww
            #print "Assign found",ww
            ww+=1
            i+=6
            tmp = parse_parenthesis(i,data)
            assign_str = tmp[0]
            i= tmp[1]
            if "value=Name(id='threading'" in assign_str:
                continue
            #print assign_denning(assign_str)
            #print "%%assign", assign_denning(assign_str)
            S.append(assign_denning(assign_str))
        elif parse_keyword(i,data) == "If":
            global ww1
            #print "If found", ww1
            ww1 += 1
            i+=2
            tmp = parse_parenthesis(i,data)
            if_str = tmp[0]
            i = tmp[1]
            S.append(if_denning(if_str))
        elif parse_keyword(i, data) == "While":
            global ww2
            #print "while found", ww2
            ww2 += 1
            i+=5
            tmp = parse_parenthesis(i,data)
            while_str = tmp[0]
            i= tmp[1]
            #print while_denning(while_str)
            S.append(while_denning(while_str))
        i+=1
    #print seq(S),"-------------------#",data
    return seq(S[:],tag)

################################### main #############################################
with open(sys.argv[1], "r") as inputfile:
    #data = inputfile.read().replace('\n', '').replace(' ','')
    data="".join(inputfile.read().split())
#print data
susr_continuous_parse("",{},data,"outer")
#print "#if: ",ww1-1
#print "#while: ",ww2-1
#print "#assign: ",ww-1








