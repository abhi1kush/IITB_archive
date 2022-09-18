import sys
import re
import shutil

line = 0

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
    return ["{" + if_str[1:i] + "}", if_str[i + 7:]]

def parse_keyword(i, data):
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
    id_index = [m.start() for m in re.finditer('id=', line)]
    var_list = []
    for it in id_index:
        vname = extract_variavle_name(it + 4, line)
        if vname == "False" or vname == "True":
            continue
        var_list.append(vname)
    return var_list


def multiple_assign(parent_list, global_while_list, assign_str, target_id_index):
    global line
    tmp = assign_str.split("value", 1)
    rvalue = parse_variables(tmp[0])
    lvalue = parse_variables(tmp[1])

    # printing denning's rule
    for it in rvalue:
        if len(lvalue) == 0:
            print "low " + const.lt + " " + it
            line += 1
        else:
            print make_lub_string(lvalue), const.lt, it
            line += 1


def assign_denning(parent_list, global_while_list, called_by_fun, fun_global,assign_str):  # applying dennig's model on assignments
    global line
    ss = assign_str.split("value")
    target_id_index = [m.start() for m in re.finditer('id=', ss[0])]

    if len(target_id_index) > 1:
        multiple_assign(parent_list, global_while_list, assign_str, target_id_index)
        return 0

    if "id='" in ss[0]:
        left = extract_variavle_name(0, ss[0].split("id='")[1])
        # print "lvalue", left," ",
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

    """Update local parent_list """
    parent_list += rvalue

    """Printing denning rules for stmts"""

    # print "= rvalues", rvalue, "parent_list", parent_list
    """Renaming all local variable of function"""
    mod_parent_list = []
    if called_by_fun != "":
        if left not in fun_global:
            left += "_" + called_by_fun
        for it in parent_list:
            if it not in fun_global:
                it += "_" + called_by_fun
            mod_parent_list.append(it)
    if called_by_fun != "" and len(mod_parent_list) > 0:
        parent_list = mod_parent_list

    ret = ""
    if len(parent_list + global_while_list) == 0 :
        ret = "low" + " " + const.lt + " " + left
    else:
        ret = make_lub_string(parent_list + global_while_list)
        ret += " " + const.lt + " " + left
    print ret
    line += 1

def augAssign_denning(parent_list, global_while_list, called_by_fun, fun_global, augAssign_str):
    i = augAssign_str.find("id=")
    var_name = extract_variavle_name(i + 4, augAssign_str)
    parent_list.append(var_name)
    assign_denning(parent_list[:], global_while_list, called_by_fun, fun_global, augAssign_str)


def track_while(while_str):
    while_list = []
    while_index = [m.start() for m in re.finditer("While", while_str)]
    for it in while_index:
        count = 0
        i = it
        while count < 2 :
            if while_str[i] == "(":
                count += 1
            i += 1
        i -= 1
        test_str = parse_parenthesis(i, while_str)[0]
        while_list += parse_variables(test_str)
    return while_list

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

    if if_str[1:5] != "test":
        print "Error test not found in if"

    """extract test=...() from if_half"""
    i = if_half.find("(")
    tmp = parse_parenthesis(i, if_half)
    test_str = tmp[0]
    parent_list += parse_variables(test_str)
    i = tmp[1]

    """then extract body part and process like normal AST text """
    # body processing
    body_onward_str = if_half[i:]  ### Asumption : Compare string always followed by body=[...] imediatly
    # setting i to location of [ in body_str: ,body=[..
    i = body_onward_str.find("[")
    body_str = parse_square_br(i, body_onward_str)[0]

    continuous_parse(parent_list[:], global_while_list, called_by_fun, fun_global, body_str)
    continuous_parse(parent_list[:], global_while_list, called_by_fun, fun_global, ladder)

def while_denning(parent_list, global_while_list, called_by_fun, fun_global, while_str):
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

def set_clear_denning(parent_list, global_while_list,called_by_fun, fun_global, expr_str):
    global line
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
    """Renaming local var"""
    if var_name not in fun_global:
        var_name += "_"+called_by_fun
    i = attribute_str.find("attr=")
    attr = extract_variavle_name(i + 6, attribute_str)
    if attr == "set":
        # treat it like AugAssign s0 += 1
        print make_lub_string(parent_list + [var_name] + global_while_list) + " <=  " + var_name
        line += 1
    elif attr == "clear":
        # treat it like AugAssign s0 -= 1
        print make_lub_string(parent_list + [var_name] + global_while_list) + " <= " + var_name
        line += 1
    elif attr == "wait":
        global_while_list.append(var_name)

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


def fun_denning(global_while_list,fun_str):
    fun_name = extract_variavle_name(fun_str.find("name=") + 6, fun_str)
    fun_globals = extract_Globals(fun_str)
    fun_globals.update(supreme_global)
    fun_global_while = []
    continuous_parse(global_while_list, fun_global_while, fun_name, fun_globals, fun_str)


# global var for counting
ww = ww1 = ww2 = 1
nested_while = 0
supreme_global = {}

def continuous_parse(parent_list, global_while_list, called_by_fun, fun_global, data):
    # type: (object, object) -> object
    length = len(data)
    i = 0
    while i < length - 1:
        # checking for keyword
        if parse_keyword(i, data) == "FunctionDef":
            i += 11
            tmp = parse_parenthesis(i, data)
            fun_str = tmp[0]
            i = tmp[1]
            global_while_list = []
            fun_denning(global_while_list,fun_str)
        if parse_keyword(i, data) == "Expr(":                    #NEED generlization
            i += 4
            tmp = parse_parenthesis(i, data)
            expr_str = tmp[0]
            i = tmp[1]
            set_clear_denning(parent_list[:], global_while_list, called_by_fun, fun_global, expr_str)
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
                var_name = parse_variables(target_of_assignment(assign_str))[0]
                supreme_global[var_name] = 1
                continue
            assign_denning(parent_list[:], global_while_list, called_by_fun, fun_global, assign_str)
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
            global nested_while
            # print "while found", ww2
            ww2 += 1
            i += 5
            tmp = parse_parenthesis(i, data)
            while_str = tmp[0]
            i = tmp[1]
            if nested_while == 0:
                global_while_list += track_while(while_str)
            nested_while += 1
            while_denning(parent_list[:], global_while_list, called_by_fun, fun_global, while_str)
            nested_while -= 1
        i += 1


############# main ###################
with open(sys.argv[1], "r") as inputfile:
    # data = inputfile.read().replace('\n', '').replace(' ','')
    data = "".join(inputfile.read().split())
orig_stdout = sys.stdout
f = file('tmp_constraints.txt', 'w')
sys.stdout = f
llist = []
dummy = []
outside_while_list = []
continuous_parse(llist[:], outside_while_list, "", dummy, data)

sys.stdout = orig_stdout
f.close()

from_file = open('tmp_constraints.txt','r')
to_file = open('constraints.txt','w')
to_file.write(str(line)+"\n")
shutil.copyfileobj(from_file, to_file)

# print "#while: ",ww2-1
# print "#assign: ",ww-1
