from z3 import *

INVITATI = 10
NUM_TAVOLI= 3
DIM_TAVOLI = 4

def postiVicini(posto):
    t_n = posto // DIM_TAVOLI
    return [(t_n*DIM_TAVOLI + i) for i in range(DIM_TAVOLI)]

#def getInvitato(ps, t, i):
#    return ps[i + (t*DIM_TAVOLI)]

if __name__ == "__main__":

    #https://ericpony.github.io/z3py-tutorial/guide-examples.htm

    p = [Int("p_%s" % i) for i in range(INVITATI)]

    # ad ogni posto deve corrispondere un invitato
    val_p = [And(0 <= p[i], p[i] < INVITATI) for i in range(INVITATI)]

    tutti_seduti = [Distinct([p[i] for i in range(INVITATI)])]


    #s = Solver()
    s = Optimize()

    s.add(val_p)
    s.add(tutti_seduti)

    
    accompagnatori = (
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0)
            )

    #acc_c = [If(accompagnatori[j][i] == 1 and p[k] == i, Or([p[min(s, INVITATI - 1)] == j for s in postiVicini(k)]) ,True) for i in range(INVITATI) for j in range(i) for k in range(INVITATI)]

    acc_c = [If(p[k] == i, Or([p[min(s, INVITATI - 1)] == j for s in postiVicini(k)]) ,True) for i in range(INVITATI) for j in range(i) for k in range(INVITATI) if accompagnatori[i][j] == 1]

    s.add(acc_c)

    #print (acc_c)
    divisi = (
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0)
            )

    div_c = [If(p[k] == i, And([p[min(s, INVITATI - 1)] != j for s in postiVicini(k)]) ,True) for i in range(INVITATI) for j in range(i) for k in range(INVITATI) if divisi[i][j] == 1]

    s.add(div_c)

    preferenze = (
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,10,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,0,0,0,0,0,0,0),
                (0,0,0,30,0,0,0,0,0,0),
                (30,0,0,0,0,0,0,0,0,0),
                (0,0,0,10,0,0,0,0,0,0),
                (0,0,0,10,0,0,0,0,0,0),
                (0,0,0,0,0,0,10,0,0,0)
            )

    PREF = Array("PREF", IntSort(), IntSort())
    for i in range(INVITATI):
        for j in range (i):
            PREF = Store(PREF, (j + i*INVITATI), preferenze[i][j])

    ints = []
    for t in range(NUM_TAVOLI):
        for i in range(DIM_TAVOLI):
            for j in range(i+1,DIM_TAVOLI):
                if (j + t*DIM_TAVOLI) < INVITATI and (i + t*DIM_TAVOLI) < INVITATI:
                    i1 = p[i + t*DIM_TAVOLI]
                    i2 = p[j + t*DIM_TAVOLI]
                    s.add(i1 > i2)
                    ints.append(Select(PREF,(i2 + i1*INVITATI)))

    mx = s.maximize(sum(ints))

    if(s.check() == sat):
        m = s.model()
        
        for i in range(INVITATI):
            if i % DIM_TAVOLI == 0:
                print("-------------")
            print(m.evaluate(p[i]))
    else:
        print("unsat")
