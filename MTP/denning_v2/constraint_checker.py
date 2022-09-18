"""It takes two files as input First: constraint file Second: label file """
"""Format of constraint file :  no of constraint
                                x + y <= z
                                a <= b
                                ...
                                """
"""Format of label file :  u = [[x,y,...],[a,b,...]]
                           v = [[x,y,...],[a,b,...]]
    """

import sys

if len(sys.argv) != 3:
    print "Error: wrong parameter"
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
            if line == "":
                break
            tmp = line.split("=")
            left = tmp[0]
            right = tmp[1]
            tmp_s = right.strip("[").strip("]").split("],[")
            first_list = tmp_s[0].split(",")
            second_list = tmp_s[1].split(",")
            labels[left] = [set(first_list),set(second_list)]
    return labels


def join(label1,label2,subject):
    R = label1[0].intersection(label2[0])
    W = label1[1] | label2[0]
    return [R,W]

def can_flow(label1,label2):
    return label1[0].issuperset(label2[0]) and label1[1].issubset(label2[1])


def can_perform(subject,constraint,labels):
    if subject not in labels[constraint[1]]:
        return False
    tmp = set(constraint[0])
    left_list = list(tmp)
    for it in left_list:
        if subject not in labels[it][0]:
            return False
    return True

def can_perform_all(subject,cons,labels):
    for constraint in cons:
        if can_perform(subject,constraint,labels) == False:
            return False
    return True

print process_constraint_file()
print process_label_file()
