import sys
import re


class const:
    otime = "*"  # u"\u2295"
    oplus = "+"  # u"\u2297"
    lt = "<="  # u"\u2264"


def make_lub_string(llist):  # assumption list containing string elemnts
    if len(llist) == 0:
        return 0
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
        i = i + 1
    return ret


def make_glb_string(llist):  # assumption list containing string elemnts
    # type: (list) -> string
    if len(llist) == 0:
        return 0
    if len(llist) == 1:
        return llist[0]
    tmp = set(llist)
    uniq_list = list(tmp)
    if len(uniq_list) == 1:
        return uniq_list[0]
    ret = ""
    ret += uniq_list[0]
    i = 1
    while i < len(uniq_list):
        ret += " " + const.oplus + " "
        ret += uniq_list[i]
        i = i + 1
    return ret


def split_through_orelse(if_str):
    # find first body word
    i = if_str.find("body=[")
    i = parse_square_br(i + 5, if_str)[1] + 1
    return [if_str[0:i] + ")", if_str[i + 7:]]


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


def extract_variavle_name(startpos, line):
    # string->string
    var = ""
    while line[startpos] != "'":
        var += line[startpos]
        startpos = startpos + 1
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


def multiple_assign(parent_list, global_while_list, assign_str, target_id_index):
    tmp = assign_str.split("value", 1)
    target_id_index = [m.start() for m in re.finditer('id=', tmp[0])]
    id_index = [m.start() for m in
                re.finditer('id=', tmp[1])]  # list of starting index of variables in right part of string
    rvalue = []
    if len(id_index) > 0:
        for it in id_index:
            startpos = it + 4
            rvalue.append(extract_variavle_name(startpos, tmp[1]))
    parent_list += rvalue
    dict = {}
    local_dependency = []
    for it in reversed(target_id_index):
        var_name = extract_variavle_name(it + 4, assign_str)
        dict[var_name] = parent_list + local_dependency + global_while_list
        local_dependency.append(var_name)

    # printing denning's rule
    for key in dict:
        # left = make_lub_string(dict[key])
        if len(dict[key]) == 0:
            print "low " + const.lt + " " + key
        else:
            print make_lub_string(dict[key]), const.lt, key


def assign_denning(parent_list, global_while_list, called_by_fun, fun_global,assign_str, su_sr_list):  # applying dennig's model on assignments
    ss = assign_str.split("value")
    target_id_index = [m.start() for m in re.finditer('id=', ss[0])]

    if len(target_id_index) > 1:
        multiple_assign(parent_list, global_while_list, assign_str, target_id_index)
        return 0

    if "id='" in ss[0]:
        Su = extract_variavle_name(0, ss[0].split("id='")[1])
        # print "lvalue", Su," ",
    else:
        Su = ['const']
    id_index = [m.start() for m in re.finditer('id=', ss[1])]  # list of starting index of variables in right part of string

    """compute eLabel"""
    eLabel = []
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
            eLabel.append(vname)
    Sr = eLabel
    su_sr_list.append([[Su],Sr,eLabel])


def augAssign_denning(parent_list, global_while_list, called_by_fun, fun_global, augAssign_str,su_sr_list):
    #i = augAssign_str.find("id=")
    #Su = [extract_variavle_name(i + 4, augAssign_str)]
    Sr = parse_variables(augAssign_str)
    Su = [Sr[0]]
    su_sr_list.append([Su,Sr,Sr])

def if_denning(parent_list, global_while_list, called_by_fun, fun_global, if_str):
    # type: (list, list, string, dict, string) -> print rules
    if "orelse=" not in if_str:
        # print "termination",if_str
        if if_str[0:2] == "[]":  # absence of else part
            return []
        else:  # handling else part
            else_str = if_str
            continuous_parse(parent_list[:], global_while_list, called_by_fun, fun_global, else_str)
            return []

    tmp = split_through_orelse(if_str)
    if_half = tmp[0]
    ladder = tmp[1]

    """extract compare from if_half"""
    i = if_half.find("Compare(")
    compare = parse_parenthesis(i + 7, if_half)[0]
    i = parse_parenthesis(i + 7, if_half)[1]
    parent_list += parse_variables(compare)
    # print parent_list

    """then extract body part and process like normal AST text """
    # body processing
    body_onward_str = if_half[i:]  ### Asumption : Compare string always followed by body=[...] imediatly
    # setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    body_str = parse_square_br(i, body_onward_str)[0]

    continuous_parse(parent_list[:], global_while_list, called_by_fun, fun_global, body_str)
    continuous_parse(parent_list[:], global_while_list, called_by_fun, fun_global, ladder)


def while_denning(parent_list, global_while_list, called_by_fun, fun_global, while_str):
    """
    :type parent_list: list
    """
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

    parent_list += parse_variables(compare)
    global_while_list += parse_variables(compare)

    # body processing
    body_onward_str = while_str[i:]  ### Asumption : Compare string always followed by body=[...] imediatly
    # setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    body_str = parse_square_br(i, body_onward_str)[0]

    continuous_parse(parent_list[:], global_while_list, called_by_fun, fun_global, body_str)

def set_clear_denning(parent_list, global_while_list, expr_str):
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
    if attr == "set":
        # treat it like AugAssign s0 += 1
        print make_lub_string(parent_list + [var_name] + global_while_list) + " <=  " + var_name
    elif attr == "clear":
        # treat it like AugAssign s0 -= 1
        print make_lub_string(parent_list + [var_name] + global_while_list) + " <= " + var_name
    elif attr == "wait":
        global_while_list.append(var_name)
        pass
        # print "This Expr(...) is neither set nor clear"


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


def fun_denning(fun_str):
    fun_name = extract_variavle_name(fun_str.find("name=") + 6, fun_str)
    # print fun_name
    fun_globals = extract_Globals(fun_str)
    # print globals
    fun_global_while = []
    continuous_parse([], fun_global_while, fun_name, fun_globals, fun_str)


# global var for counting
ww = ww1 = ww2 = 1

# global while list
global_while_list = []


def continuous_parse(parent_list, global_while_list, called_by_fun, fun_global, data,su_sr_list):
    # type: (object, object) -> object
    print "global while",global_while_list
    length = len(data)
    i = 0
    while i < length - 1:
        # checking for keyword
        if parse_keyword(i, data) == "FunctionDef":
            i += 11
            tmp = parse_parenthesis(i, data)
            fun_str = tmp[0]
            i = tmp[1]
            fun_denning(fun_str)
        if parse_keyword(i, data) == "Expr(":
            i += 4
            tmp = parse_parenthesis(i, data)
            expr_str = tmp[0]
            i = tmp[1]
            set_clear_denning(parent_list[:], global_while_list, expr_str)
        if parse_keyword(i, data) == "AugAssign":
            i += 9
            tmp = parse_parenthesis(i, data)
            augAssign_str = tmp[0]
            i = tmp[1]
            augAssign_denning(parent_list[:], global_while_list, called_by_fun, fun_global, augAssign_str)
        if parse_keyword(i, data) == "Assign":
            global ww
            # print "Assign found",ww
            ww += 1
            i += 6
            tmp = parse_parenthesis(i, data)
            assign_str = tmp[0]
            i = tmp[1]
            if "value=Name(id='threading'" in assign_str:
                continue
            assign_denning(parent_list[:], global_while_list, called_by_fun, fun_global, assign_str,su_sr_list)
        elif parse_keyword(i, data) == "If":
            global ww1
            # print "If found", ww1
            ww1 += 1
            i += 2
            tmp = parse_parenthesis(i, data)
            if_str = tmp[0]
            i = tmp[1]
            if_denning(parent_list[:], global_while_list, called_by_fun, fun_global, if_str)
        elif parse_keyword(i, data) == "While":
            global ww2
            # print "while found", ww2
            ww2 += 1
            i += 5
            tmp = parse_parenthesis(i, data)
            while_str = tmp[0]
            i = tmp[1]
            while_denning(parent_list[:], global_while_list, called_by_fun, fun_global, while_str)
        i += 1


################################### main #############################################
with open(sys.argv[1], "r") as inputfile:
    # data = inputfile.read().replace('\n', '').replace(' ','')
    data = "".join(inputfile.read().split())
# print data
llist = []
dummy = []
su_sr_list = []
continuous_parse(llist[:], global_while_list, "", dummy, data,su_sr_list)
# print "#if: ",ww1-1
# print "#while: ",ww2-1
# print "#assign: ",ww-1
