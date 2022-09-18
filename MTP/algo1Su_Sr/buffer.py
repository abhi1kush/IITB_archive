PCLabel = []
def seq(Slist):
    global PCLabel
    Su = []
    Sr = []
    i = 0
    while i < len(Slist):
        Su += Slist[i][0]
        Sr += Slist[i][1]
        print "Verify:", Slist[i][1], "<=", Slist[i+1][1]
    print "Verify:", PCLabel, "<=", Su
    PCLabel += Sr
    return [Su,Sr,[]]
