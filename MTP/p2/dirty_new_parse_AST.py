#INPUT P - the set of principals that have a stake in the computation.
#      p - computing athority 
#      S - set of all principals in system.
from  more_itertools import unique_everseen
import sys
import re, pdb
import copy
import itertools

iteration = 20
debug = 0
def debugPrint(x):
    if debug == 1:
        print x

class const:
    otime = "*"  # u"\u2295"
    oplus = "+"  # u"\u2297"
    lt = "<="  # u"\u2264"


def SemanticsOfProgram(P,p,c,PC,S):
    if p not in P:
        print "MISSUSE";
    for x in AccessedGlobal(c):
        if p not in R(lamda(x)):
            print "MISSUSE";
    #intialization
    for x in Global(c):
        M[x] = Md[x]
        lamda[x] = lamdad[x]
    for x in ((VA(c) - Global(c)) | set(PC)):
        M[x] = 0
        lamda[x] = (p,S,set([p]))

def VA(data):
    return set(parse_variables(data))

def Global(data): #discard all whiles, ifs and functions -> then remaining code will have only globals.
    str = ""
    length = len(data)
    i = 0
    while i < length - 1:
        # checking for keyword
        if parse_keyword(i, data) == "FunctionDef":
            i += 11
            i = parse_parenthesis(i, data)[1]
        elif parse_keyword(i, data) == "Expr(":
            i += 4
            i = parse_parenthesis(i, data)[1]
        elif parse_keyword(i, data) == "AugAssign":
            i += 9
            i = parse_parenthesis(i, data)[1]
        elif parse_keyword(i, data) == "If":
            i += 2
            i = parse_if(i, data)[1]

        elif parse_keyword(i, data) == "While":
            i += 5
            i = parse_parenthesis(i, data)[1]
        else:
            str += data[i]
        i += 1
    return set(parse_variables(str))

def parseTestVariables(data):
    test_index = [ m.start() for m in re.finditer('test=', data) ]
    ll = []
    for it in test_index:
        ll += parse_variables(parse_next_parenthesis(it,str)[0])
    return ll

def AccessedGlobal(data):
    #(i)right-hand side of assignment
    #(ii) condition of branching/iteration
    #(iii) return
    ll = []
    length = len(data)
    i = 0
    while i < length - 1:
        # checking for keyword
        if parse_keyword(i, data) == "AugAssign":
            i += 9
            tmp = parse_parenthesis(i, data)
            ll += parse_variables(tmp[0])
            i = tmp[1]
        elif parse_keyword(i, data) == "Assign":
            i += 6
            tmp = parse_parenthesis(i, data)
            ryt = tmp[0].split("value=")[1]
            ll += parse_variables(ryt)
            i = tmp[1]
        elif parse_keyword(i, data) == "If":
            i += 2
            tmp = parse_parenthesis(i, data)
            ll += parseTestVariables(tmp[0])
            i = tmp[1]
        elif parse_keyword(i, data) == "While":
            i += 5
            tmp = parse_parenthesis(i, data)
            ll += parseTestVariables(tmp[0])
            i = tmp[1]
        elif parse_keyword(i,data) == "Return":
            i += 6
            tmp = parse_parenthesis(i,data)
            ll += parse_variables(tmp[0])
            i = tmp[1]
        i += 1
    return set(ll)

def ModifiedGlobal(data):
    ss = target_of_assignment(data)
    modifiedVarList = parse_variables(ss)
    return Global(data) & set(modifiedVarList)


def make_lub_string(llist):  # assumption list containing string elemnts
    if len(llist) == 0:
        return "Low"
    if len(llist) == 1:
        return llist[0]
    tmp = set(llist)
    uniq_list = list(tmp)
    if len(uniq_list) == 1:
        return str(uniq_list[0])
    ret = ""
    ret += uniq_list[0]
    i = 1
    while i < len(uniq_list):
        ret += " " + const.oplus + " "
        ret += uniq_list[i]
        i += 1
    return ret


def make_glb_string(llist):  # assumption list containing string elemnts
    # type: (list) -> string
    if len(llist) == 0:
        return "High"
    if len(llist) == 1:
        return llist[0]
    uniq_list = list(set(llist))
    if len(uniq_list) == 1:
        return uniq_list[0]
    ret = ""
    ret += uniq_list[0]
    i = 1
    while i < len(uniq_list):
        ret += " " + const.otime + " "
        ret += uniq_list[i]
        i += 1
    return ret


def split_through_orelse(if_str):
    # find first body word
    i = if_str.find("body=[")
    i = parse_square_br(i + 5, if_str)[1] + 1
    return ["{" + if_str[1:i] + "}", if_str[i + 7:]]


def parse_keyword(i, data):
    # checking for
    funLen =  len("Expr(value=Call(func=Name(id='")
    attrLen = len("Expr(value=Call(func=Attribute(value=Name(id='")
    
    if i + 6 < len(data) - 1 and data[i:i + 6] == 'Assign':
        return "Assign"
    if i + 9 < len(data) - 1 and data[i:i + 9] == 'AugAssign':
        return "AugAssign"
    if i + 2 < len(data) - 1 and data[i:i + 2] == 'If':
        return "If"
    if i + 5 < len(data) - 1 and data[i:i + 5] == 'While':
        return "While"
    if i + 11 < len(data) - 1 and data[i:i + 11] == 'FunctionDef':
        return "FunctionDef"
    if i + 6 < len(data) - 1 and data[i:i+6] == "Return":
        return "Return"
    if i +  funLen < len(data) - 1 and data[i:i + funLen] == "Expr(value=Call(func=Name(id='":
	return  "fun_call"
    if i + attrLen  < len(data) - 1 and data[i:i + attrLen ] == "Expr(value=Call(func=Attribute(value=Name(id='":
        if extract_variavle_name(i+attrLen,data) == 'thread':
            return "thread_fun_call"
        else:
	    return "set_clear_wait"
    return "none"

def parse_square_br(i, data):
    if data[i] != '[':
        print "Error: [ is missing"
        return []
    ret = "["
    count = 1
    i += 1
    while count > 0 and i < len(data) - 1:
        if data[i] == '[':
            count += 1
        if data[i] == ']':
            count -= 1
        ret += data[i]
        i += 1
    return [ret, i]


def parse_parenthesis(i, data):
    # type: (int , string) -> string
    if data[i] != '(':
        print data[i-4:i+4],data[i]
        print "Error: ( is missing"
        return []
    ret = "("
    count = 1
    i += 1
    while count > 0 and i < len(data) - 1:
        if data[i] == '(':
            count += 1
        if data[i] == ')':
            count -= 1
        ret += data[i]
        i += 1
    return [ret, i]

def parse_next_parenthesis(i,data):
    while i < len(data)-1 and data[i] != '(':
        i+=1
    if i == len(data)-1:
        print "No parenthesis in string"
        return ["",i]
    ret = "("
    count = 1
    i += 1
    while count > 0 and i < len(data) - 1:
        if data[i] == '(':
            count += 1
        if data[i] == ')':
            count -= 1
        ret += data[i]
        i += 1
    return [ret, i]

def extract_variavle_name(startpos, line):
    # string->string
    var = ""
    while line[startpos] != "'":
        var += line[startpos]
        startpos += 1
    return var

def target_of_assignment(str):  # find all targets
    # string->list
    targets_ptrn = r"targets=\[.*?\]"
    ctargets_ptrn = re.compile(targets_ptrn)
    temp_list = ctargets_ptrn.findall(str)
    ret = ''.join(temp_list)  # converting to string
    return ret


def parse_variables(line):
    # type: (string) -> list
    # type: (str) -> object
    id_index = [m.start() for m in re.finditer('id=', line)]
    var_list = []
    for it in id_index:
        vname = extract_variavle_name(it + 4, line)
        if vname == "False" or vname == "True":
            continue
        var_list.append(vname)
    return var_list


def multiple_assign(assign_str, target_id_index, PC):
    global line
    tmp = assign_str.split("value", 1)
    rvalue = parse_variables(tmp[0])
    lvalue = parse_variables(tmp[1])
    pc_update(PC,lvalue)

    # printing denning's rule
    for it in rvalue:
        # left = make_lub_string(dict[key])
        if len(lvalue) == 0:
            print "low " + const.lt + " " + it
            line += 1
        else:
            print make_lub_string(lvalue), const.lt, it
            line += 1
    return PC[:]

def pc_update(PC, list):
    #print "pre update", PC
    for pc in PC:
        pc += list
    #print "post update",PC

def assign_denning(assign_str, PC):  # applying dennig's model on assignments
    #pdb.set_trace()
    global line
    global output
    ss = assign_str.split("value")
    target_id_index = [m.start() for m in re.finditer('id=', ss[0])]

    if len(target_id_index) > 1:
        return multiple_assign(assign_str, target_id_index, PC)

    if "id='" in ss[0]:
        left = extract_variavle_name(0, ss[0].split("id='")[1])
    else:
        left = ['const']
    id_index = [m.start() for m in
            re.finditer('id=', ss[1])]  # list of starting index of variables in right part of string
    rvalue = []
    if len(id_index) == 0:
        # rvalue.append("low")
        pass
    else:
        for it in id_index:
            startpos = it + 4
            vname = extract_variavle_name(startpos, ss[1])
            """Exclusion of False keyword"""
            if vname == "False" or vname == "True":
                continue
            rvalue.append(vname)
    #pc_update(PC,rvalue)

    ret = ""
    l = rvalue
    #l1 = l + lambda(pc)
    #updating PC
    for pc in PC:
        pc += l
    for pc in PC:
            output.append(make_lub_string(pc)+ " " + const.lt + " " + make_glb_string([left])) 
    line += 1
    return PC[:]


def augAssign_denning(called_by_fun, fun_global, augAssign_str, PC):
    # i = augAssign_str.find("id=")
    # Su = [extract_variavle_name(i + 4, augAssign_str)]
    global output
    Sr = parse_variables(augAssign_str)
    pc_update(PC,Sr)
    for pc in PC:
        output.append( make_lub_string(pc) + " " + const.lt + " " + Sr[0])
    return PC[:]

PCA = []

def if_denning(called_by_fun, fun_global, if_str, rest, PC):
    # type: (list, list, string, dict, string) -> print rules
    #pdb.set_trace()
    #print "begin IF",PC
    if "orelse=" not in if_str:
        # print "termination",if_str
        if if_str[0:2] == "[]":  # absence of else part
            return []
        else:  # handling else part
            else_str = if_str
            continuous_parse([], ccalled_by_fun, fun_global, else_str, PC[:])
            return []

    tmp = split_through_orelse(if_str)
    if_half = tmp[0]
    ladder = tmp[1]

    if if_str[1:5] != "test":
        print "Error test not found in if"

    """extract test=...() from if_half"""
    i = if_half.find("(")
    tmp = parse_parenthesis(i, if_half)
    test_str = tmp[0]
    #parent_list += parse_variables(test_str)
    i = tmp[1]
    pc_update(PC,parse_variables(test_str))

    """then extract body part and process like normal AST text """
    # body processing
    body_onward_str = if_half[i:]  ### Asumption : Compare string always followed by body=[...] imediatly
    # setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    body_str = parse_square_br(i, body_onward_str)[0]
    memo = {}
    memo2 = {}
    PC1 = copy._deepcopy_list(PC,memo)
    PC2 = copy._deepcopy_list(PC, memo2)
    PCA = list(continuous_parse([], called_by_fun, fun_global, body_str , PC1[:]))
    PCB = list(continuous_parse([], called_by_fun, fun_global, ladder , PC2[:]))
    #debugPrint(PCA)
    #debugPrint(PCB)
    #print "end IF",PCB + PCA
    return PCB + PCA

def while_denning(iteration,  called_by_fun, fun_global, while_str, PC):
    # debug print "printing while_str",while_str[6:10]
    compare = "()"
    if while_str[6:10] == "Name":
        tmp = parse_parenthesis(10, while_str)
        compare = tmp[0]
        i = tmp[1]
    elif while_str[6:10] == "Comp":
        tmp = parse_parenthesis(13, while_str)
        compare = tmp[0]
        i = tmp[1]
    pc_update(PC,parse_variables(compare))
    # body processing
    body_onward_str = while_str[i:]  ### Asumption : Compare string always followed by body=[...] imediatly
    # setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    body_str = parse_square_br(i, body_onward_str)[0]
    memo = {}
    memo2 = {}
    PC1 = copy._deepcopy_list(PC, memo)
    PC2 = copy._deepcopy_list(PC, memo2)

    PCB = list(continuous_parse( [], called_by_fun, fun_global, body_str, PC2[:]))
    return PC1 + PCB

def set_clear_denning( called_by_fun, fun_global, expr_str, PC):
    #ASSUMPTION SEMAPHORE VAR IS ALWAYS GLOBAL
    global output
    i = expr_str.find("Call(")
    i += 4
    call_str = parse_parenthesis(i, expr_str)[0]
    i = call_str.find("Attribute(")
    i += 9
    attribute_str = parse_parenthesis(i, call_str)[0]
    i = attribute_str.find("Name(")
    i += 4
    # name_str = parse_parenthesis(i,attribute_str)[0]
    i = attribute_str.find("id=")
    var_name = extract_variavle_name(i + 4, attribute_str)
    i = attribute_str.find("attr=")
    attr = extract_variavle_name(i + 6, attribute_str)
    if attr == "set" or attr == "clear":
        # treat it like AugAssign s0 += 1
        # treat it like AugAssign s0 -= 1
        pc_update(PC,[var_name])
        #print "set clear-> ",PC
        for pc in PC:
            output.append( make_lub_string(pc)+ " " + const.lt + " " + make_glb_string([var_name])) #label[left]
    elif attr == "wait":
        #global_while_list.append(var_name)
        pc_update(PC,[var_name])
        #print "wait -> ",PC

def extract_Globals(fun_str):
    global_index = [m.start() for m in re.finditer("Global\(", fun_str)]
    globals = {}
    for it in global_index:
        global_str = parse_parenthesis(it + 6, fun_str)[0]
        sq_str = parse_square_br(global_str.find("["), global_str)[0]
        ss = sq_str.strip("[").strip("]")
        sslist = ss.split(",")
        for it in sslist:
            if it == '':
                continue
            globals[(it.strip("'"))] = 1
    return globals


def fun_denning(fun_str,PC):
    fun_name = extract_variavle_name(fun_str.find("name=") + 6, fun_str)
    fun_globals = extract_Globals(fun_str)
    funPC = []
    PC = continuous_parse(funPC, fun_name, fun_globals, fun_str,PC) 
    return PC + funPC

# global var for counting
ww = ww1 = ww2 = 1

# global while list
global_while_list = []


def parse_if(i, data):
    tmp = parse_parenthesis(i, data)
    i = tmp[1]
    if_str = tmp[0]
    rest = data[i:]
    return [if_str, i, rest]

def uniq(l):
    ll = []
    for it in l:
        ll.append(list(set(it)))
    return ll

fun_hash = {}

def duplicateRemoval(PC):
    tmpPC = []
    for pc in PC:
        tmppc = list(set(pc))
        tmppc.sort()
        tmpPC.append(tmppc)
    tmpPC.sort()
    return list(tmpPC for tmpPC,_ in itertools.groupby(tmpPC))

recCount =0
def continuous_parse( funPC, called_by_fun, fun_global, data, PC):
    #pdb.set_trace()
    # type: (object, object) -> object
    global recCount 
    length = len(data)
    i = 0
    recCount += 1
    debugPrint(recCount)
    debugPrint("Continuous_parse before loop:")
    while i < length - 1:
        #checking for keyword
        if parse_keyword(i,data) == "FunctionDef":  #skipping all function definition
            tmp = parse_parenthesis(i+11, data)
            i = tmp[1]
        if parse_keyword(i,data) == "thread_fun_call": #parsing function call used in threads
            tmp = parse_parenthesis(i+4,data)
            i = tmp[1]
            if 'start_new_thread' in tmp[0]:
                #print "got thread call"
                fi = tmp[0].find("args=[")
                funName = extract_variavle_name(fi+15,tmp[0]) #len(args=[Name(id=') = 15
                if funName in fun_hash:
                    findex = fun_hash[funName]
                else:
                    print "Function not found but prgram called function" 
                findex += 11
                tmp = parse_parenthesis(findex, data)
                fun_str = tmp[0]
                tmp = fun_denning(fun_str,[[]])
                memo = {}
                ls = duplicateRemoval(tmp)
                PC = copy._deepcopy_list(ls, memo)

        if parse_keyword(i,data) == "fun_call":  #parsing functioncalls
            tmp = parse_parenthesis(i+4,data)
            #print "got fun call"
            funName = extract_variavle_name(i + len("Expr(value=Call(func=Name(id='"),data)
            i = tmp[1]
            if funName in fun_hash:
                findex = fun_hash[funName]
            else:
                print "Function not found but prgram called function" 
            findex += 11
            tmp = parse_parenthesis(findex, data)
            fun_str = tmp[0]
            tmp = fun_denning(fun_str,PC)
            memo = {}
            ls = duplicateRemoval(tmp)
            PC = copy._deepcopy_list(ls, memo)

        if parse_keyword(i,data) == "Return":
            debugPrint("Return stmt:")
            funPC += PC
        if parse_keyword(i, data) == "set_clear_wait":
            i += 4
            tmp = parse_parenthesis(i, data)
            expr_str = tmp[0]
            if expr_str.find("'set'") != -1 or expr_str.find("'clear'") != -1 or expr_str.find("'wait'") != -1 :
                i = tmp[1]
                set_clear_denning( called_by_fun, fun_global, expr_str, PC)
        if parse_keyword(i, data) == "AugAssign":
            i += 9
            tmp = parse_parenthesis(i, data)
            augAssign_str = tmp[0]
            i = tmp[1]
            tmp = augAssign_denning(parent_list[:], global_while_list, called_by_fun, fun_global, augAssign_str, PC[:])
            memo = {}
            ls = duplicateRemoval(tmp)
            PC = copy._deepcopy_list(ls, memo)

        if parse_keyword(i, data) == "Assign":
            global ww
            ww += 1
            i += 6
            tmp = parse_parenthesis(i, data)
            assign_str = tmp[0]
            i = tmp[1]
            if "value=Name(id='threading'" in assign_str:
                continue
            tmp = assign_denning(assign_str, PC[:])
            memo = {}
            ls = duplicateRemoval(tmp)
            PC = copy._deepcopy_list(ls,memo)
        elif parse_keyword(i, data) == "If":
            debugPrint("If stmt:")
            global ww1
            ww1 += 1
            i += 2
            tmp = parse_if(i, data)
            if_str = tmp[0]
            i = tmp[1]
            rest = tmp[2]
            tmp = if_denning(called_by_fun, fun_global, if_str, rest, PC[:])
            ls = duplicateRemoval(tmp)
            memo = {}
            PC = copy._deepcopy_list(ls, memo)
        elif parse_keyword(i, data) == "While":
            debugPrint("while stmt:")
            global ww2
            ww2 += 1
            i += 5
            tmp = parse_parenthesis(i, data)
            while_str = tmp[0]
            i = tmp[1]
            it = 1
            while( it <= iteration ):
                memo = {}
                lastPC = copy._deepcopy_list(PC, memo)
                tmp = duplicateRemoval(PC)
                memo = {}
                PC = copy._deepcopy_list(tmp, memo)
                #print "### While Iteration:",it
                tmp = while_denning(it,  called_by_fun, fun_global, while_str, PC[:])
                ls = duplicateRemoval(tmp)
                memo = {}
                PC = copy._deepcopy_list(ls, memo)
                #print lastPC,"|--|", PC
                #print "-> PC:",PC
                if lastPC == PC:
                    #print "Saturation point of loop!"
                    break
                it += 1
        i += 1
    debugPrint(recCount)
    recCount -= 1;
    debugPrint("END continuous parse:")
    return PC[:]


################################### main #############################################
with open(sys.argv[1], "r") as inputfile:
    # data = inputfile.read().replace('\n', '').replace(' ','')
    data = "".join(inputfile.read().split())
llist = []
dummy = []
su_sr_list = []
line = 0
PC = [[]]
gg = []
output = []

fun_call_index = [m.start() for m in re.finditer("FunctionDef", data)]
for index in fun_call_index:
    varName = extract_variavle_name(index+len("FunctionDef(name='"),data)
    fun_hash[varName] = index

#G = Global(data)
continuous_parse("", [], dummy, data, PC)

for it in list(unique_everseen(output)):
    print it
