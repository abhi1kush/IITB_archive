
class subject:
    #set of subjects
    S = set()
    #clearance of subject (class variable)

    def __init__(self,s,R,W):
        self.s = s
        self.R = R
        self.W = W
        self.Rs=self.R
        self.Ws=subject.S

    def canRead(self,sub,ob):
        return sub.s in ob.R and (sub.R & ob.R).issuperset(sub.Rs) and (sub.W | ob.W).issubset(sub.Ws)

    def canWrite(self,sub,ob):
        return sub.s in ob.W and sub.R.issuperset(ob.R) and sub.W.issubset(ob.W)

    def canDowngrade(self,sub,ob,dg_ob):
        return sub.s == ob.s and sub.R == ob.R and sub.W == ob.W and ob.s == dg_ob.s and ob.W == dg_ob.W and dg_ob.R.issuperset(ob.R) and dg_ob.R.difference(ob.R).issuperset(ob.W)

    def canRelabel(self,sub,ob,re_ob):
        return sub.s == ob.s and (sub.s in ob.R) and ob.R.issuperset(sub.R) and ob.W == sub.W and ob.s == re_ob.s and (sub.s in re_ob.W) and sub.R.issuperset(re_ob.R) and sub.W == re_ob.W

    def create(self,sub):
        return subject(sub.s,sub.R,sub.W | set([sub.s]))

    def lub_join(self,rw1,rw2):
        self.R = rw1.R & rw2.R
        self.W = rw1.W | rw2.W
        self.rw = subject(rw1.s+rw2.s,self.R,self.W)
        return self.rw

    def glb_meet(self,rw1,rw2):
        self.R = rw1.R | rw2.R
        self.W = rw1.W & rw2.W
        self.rw = subject(rw1.s + rw2.s, self.R, self.W)
        return self.rw

    def canFlow(self,rw1,rw2):
        return rw1.R.issuperset(rw2.R) and rw1.W.issubset(rw2.W)
