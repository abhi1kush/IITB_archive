#INPUT P - the set of principals that have a stake in the computation.
#      p - computing athority 
#      S - set of all principals in system.
#      label file 

import sys
import re, pdb
import copy

class const:
    otime = "*"  # u"\u2295"
    oplus = "+"  # u"\u2297"
    lt = "<="  # u"\u2264"

def extract_variavle_name(startpos, line):
    # string->string
    var = ""
    while line[startpos] != "'":
        var += line[startpos]
        startpos += 1
    return var

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

def parse_parenthesis(i, data):
    # type: (int , string) -> string
    if data[i] != '(':
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

def parse_keyword(i, data):
    # checking for
            if i + 4 < len(data) and data[i:i + 5] == 'Expr(':
                return "Expr("
            if i + 9 < len(data) - 1 and data[i:i + 9] == 'AugAssign':
                return "AugAssign"
            if i + 6 < len(data) - 1 and data[i:i + 6] == 'Assign':
                return "Assign"
            if i + 2 < len(data) - 1 and data[i:i + 2] == 'If':
                return "If"
            if i + 5 < len(data) - 1 and data[i:i + 5] == 'While':
                return "While"
            if i + 11 < len(data) - 1 and data[i:i + 11] == 'FunctionDef':
                return "FunctionDef"
            if i + 6 < len(data) - 1 and data[i:i+6] == "Return":
                return "Return"
            return "none"

def parse_if(i, data):
    tmp = parse_parenthesis(i, data)
    i = tmp[1]
    if_str = tmp[0]
    rest = data[i:]
    return [if_str, i, rest]

def Global(data): #discard all whiles, ifs and functions -> then remaining code will have only globals.
    # print "global while", global_while_list
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
    #print str
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


################################### main #############################################
with open(sys.argv[1], "r") as inputfile:
    # data = inputfile.read().replace('\n', '').replace(' ','')
    data = "".join(inputfile.read().split())
# print data
s = Global(data)
for it in s:
    print it + " = "
