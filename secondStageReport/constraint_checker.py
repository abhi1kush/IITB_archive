"""It takes two files as input First: constraint file Second: label file """
"""Format of constraint file :  no of constraint
                                x + y <= z
                                a <= b
                                ...
                                """
"""Format of label file :  u = [['s1'],[x,y,...],[a,b,...]]   single qute ' are optional
                           v = [['s2'],[x,y,...],[a,b,...]]
    """

import sys

if len(sys.argv) != 3:
    print "Error: wrong parameter (constraint file labelfile)"
    exit(0)

def process_constraint_file():
    cons = []
    with open(sys.argv[1], "r") as inputfile:
        i = 1
        constraints = -1
        for line in inputfile:
            line = "".join(line.split())
            if line == "":
                break
            if i == 1:
                constraints = int(line)
                i+=1
                continue
            tmp = line.split("<=")
            left = tmp[0]
            right = tmp[1]
            left_list = left.split("+")
            cons.append([left_list,right])
    return cons

def process_label_file():
    labels = {}
    with open(sys.argv[2], "r") as inputfile:
        for line in inputfile:
            line = "".join(line.split())
            line = "".join(line.split("'"))
            if line == "":
                break
            tmp = line.split("=")
            left = tmp[0]
            right = tmp[1]
            tmp_s = right.strip("[").strip("]").split("],[")
            owner = tmp_s[0]
            first_list = tmp_s[1].split(",")
            second_list = tmp_s[2].split(",")
            labels[left] = [set(first_list),set(second_list),owner]
    return labels


def join(label1,label2):
    R = label1[0].intersection(label2[0])
    W = label1[1] | label2[0]
    return [R,W]

def can_flow(label1,label2):
    return label1[0].issuperset(label2[0]) and label1[1].issubset(label2[1])

def sat(cons,labels):
    for constraint in cons:
        tmp = set(constraint[0])
        left_list = list(tmp)
        right = constraint[1]
        for it in left_list:
            if not can_flow(labels[it],labels[right]):
                return False
    return True

def can_perform(subject,constraint,labels):
    if subject not in labels[constraint[1]][1]:
        return False
    tmp = set(constraint[0])
    left_list = list(tmp)
    for it in left_list:
        if subject not in labels[it][0]:
            return False
    return True

def can_perform_set(cons,labels):
    # type: (list, dict{set,set,"str"}) -> set
    s = labels[cons[0][1]][1]
    for constraint in cons:
        tmp = set(constraint[0])
        left_list = list(tmp)
        right = constraint[1]
        for it in left_list:
            s = s.intersection(labels[it][0])
            if len(s) == 0:
                return s
        s = s.intersection(labels[right][1])
    return s

def can_perform_all(subject,cons,labels):
    for constraint in cons:
        if can_perform(subject,constraint,labels) == False:
            return False
    return True

########################### main ######################
print """Enter Choice
         1.Satisfied or not
         2.Can given subject perform all constraints
         3.Checking existance of subjects who follows constraints"""
choice = raw_input()

cons = process_constraint_file()
labels = process_label_file()

if choice == '1':
    print sat(cons,labels)
elif choice == '2':
    print "Enter subject"
    subject = raw_input()
    print can_perform_all(subject, cons, labels)
elif choice == '3':
    print can_perform_set(cons,labels)
