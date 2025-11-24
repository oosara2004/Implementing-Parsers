 

from collections import defaultdict, deque

class LR1Item:
    def __init__(self, left, right, dot, la):
        self.left = left
        self.right = right
        self.dot = dot
        self.la = la

    def next(self):
        return self.right[self.dot] if self.dot < len(self.right) else None

    def done(self):
        return self.dot >= len(self.right)

    def adv(self):
        return LR1Item(self.left, self.right, self.dot+1, self.la)

    def __hash__(self):
        return hash((self.left, tuple(self.right), self.dot, self.la))

    def __eq__(self, o):
        return (self.left, tuple(self.right), self.dot, self.la)==(o.left,tuple(o.right),o.dot,o.la)

    def __str__(self):
        r = self.right[:] if self.right else ["ε"]
        r.insert(self.dot,"•")
        return f"{self.left} -> {' '.join(r)}, {self.la}"

class LR1:
    def __init__(self, choice):
        if choice=="G1":
            self.grammar={
                "S'":[["S"]],
                "S":[["A","a","A","b"],["B","b","B","a"]],
                "A":[[]],
                "B":[[]],
            }
        else:
            self.grammar={
                "S'":[["S"]],
                "S":[["L","=","R"],["R"]],
                "L":[["*","R"],["id"]],
                "R":[["L"]],
            }

        self.nonterms=set(self.grammar.keys())
        self.terms=set()

        for A in self.grammar:
            for p in self.grammar[A]:
                for s in p:
                    if s not in self.nonterms:
                        if s!="ε":
                            self.terms.add(s)
        self.terms.add("$")

        self.prods=[]
        for A in self.grammar:
            if A!="S'":
                for p in self.grammar[A]:
                    self.prods.append((A,p))

        self.pindex={(L,tuple(R)):i+1 for i,(L,R) in enumerate(self.prods)}

        self.first={x:{x} for x in self.terms}
        for nt in self.nonterms:
            self.first[nt]=set()
        self.compute_first()

    def fst_seq(self, seq):
        out=set()
        if not seq:
            out.add("ε"); return out
        for s in seq:
            for x in self.first[s]:
                if x!="ε": out.add(x)
            if "ε" not in self.first[s]:
                break
        else:
            out.add("ε")
        return out

    def compute_first(self):
        changed=True
        while changed:
            changed=False
            for A in self.grammar:
                for prod in self.grammar[A]:
                    before=set(self.first[A])
                    if not prod:
                        self.first[A].add("ε")
                    else:
                        for X in prod:
                            for s in self.first[X]:
                                if s!="ε": self.first[A].add(s)
                            if "ε" not in self.first[X]:
                                break
                        else:
                            self.first[A].add("ε")
                    if before!=self.first[A]:
                        changed=True

    def closure(self, I):
        C=set(I)
        changed=True
        while changed:
            changed=False
            add=set()
            for it in C:
                X=it.next()
                if X in self.nonterms:
                    beta=it.right[it.dot+1:]
                    fs=self.fst_seq(beta+[it.la])
                    for p in self.grammar[X]:
                        for a in fs:
                            if a!="ε":
                                new=LR1Item(X,p,0,a)
                                if new not in C and new not in add:
                                    add.add(new)
            if add:
                C|=add; changed=True
        return C

    def goto(self,I,X):
        moved={it.adv() for it in I if it.next()==X}
        return self.closure(moved) if moved else set()

    def build(self):
        start=LR1Item("S'",self.grammar["S'"][0],0,"$")
        I0=self.closure({start})
        C=[I0]
        q=deque([I0])

        while q:
            I=q.popleft()
            for X in self.nonterms|self.terms:
                J=self.goto(I,X)
                if J and J not in C:
                    C.append(J)
                    q.append(J)

        ACTION=defaultdict(dict)
        GOTO=defaultdict(dict)

        index={frozenset(I):i for i,I in enumerate(C)}

        for i,I in enumerate(C):
            for it in I:
                a=it.next()
                if a in self.terms:
                    J=self.goto(I,a)
                    if J:
                        ACTION[i][a]=f"s{index[frozenset(J)]}"
                if it.done():
                    if it.left=="S'" and it.la=="$":
                        ACTION[i]["$"]="acc"
                    else:
                        num=self.pindex[(it.left,tuple(it.right))]
                        ACTION[i][it.la]=f"r{num}"

            for A in self.nonterms:
                J=self.goto(I,A)
                if J:
                    GOTO[i][A]=index[frozenset(J)]

        return C,ACTION,GOTO

    def print_all(self,C,ACTION,GOTO):
        for i,I in enumerate(C):
            print(f"I{i}")
            for it in sorted(I,key=lambda x:(x.left,x.right,x.dot,x.la)):
                print(" ",it)
            print()

        print("ACTION")
        terms=sorted(self.terms,key=lambda x:(x=="$",x))
        print("    "," ".join(f"{t:>6}" for t in terms))
        for s in range(len(C)):
            row=[ACTION[s].get(t,"") for t in terms]
            print(f"{s:<3}"," ".join(f"{v:>6}" for v in row))

        print("\nGOTO")
        nts=sorted([nt for nt in self.nonterms if nt!="S'"])
        print("    "," ".join(f"{nt:>6}" for nt in nts))
        for s in range(len(C)):
            row=[GOTO[s].get(nt,"") for nt in nts]
            print(f"{s:<3}"," ".join(f"{v:>6}" for v in row))



if __name__=="__main__":
    b=LR1("G1")   # اغيرها الى G2
    C,A,G=b.build()
    b.print_all(C,A,G)
 