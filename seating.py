from z3 import *
import pandas as pd
import numpy as np

INVITATI = 10
NUM_TAVOLI= 4
DIM_TAVOLI = 3

def postiVicini(posto):
    t_n = posto // DIM_TAVOLI
    return [(t_n*DIM_TAVOLI + i) for i in range(DIM_TAVOLI)]

#def getInvitato(ps, t, i):
#    return ps[i + (t*DIM_TAVOLI)]

if __name__ == "__main__":

    vincoli = pd.read_csv("test.csv")

    accompagnatori = np.zeros(vincoli.shape, int)
    accompagnatori[vincoli == 100] = 1

    divisi = np.zeros(vincoli.shape, int)
    divisi[vincoli == -100] = 1

    preferenze = vincoli.to_numpy()
    preferenze[preferenze==100] = 0
    preferenze[preferenze==-100] = 0

    #https://ericpony.github.io/z3py-tutorial/guide-examples.htm

    # un posto per ogni invitato
    p = [Int("p_%s" % i) for i in range(INVITATI)]

    # ad ogni posto deve corrispondere un unico invitato
    val_p = [And(0 <= p[i], p[i] < INVITATI) for i in range(INVITATI)]

    # tutti gli invitati devono avere un posto
    tutti_seduti = [Distinct([p[i] for i in range(INVITATI)])]


    #s = Solver()
    s = Optimize()

    s.add(val_p)
    s.add(tutti_seduti)

    ##################################
    # gli invitati devono essere seduti nello stesso tavolo dei propri accompagnatori
    acc_c = [If(p[k] == i, Or([p[min(s, INVITATI - 1)] == j for s in postiVicini(k)]) ,True) for i in range(INVITATI) for j in range(i) for k in range(INVITATI) if accompagnatori[i][j] == 1]

    s.add(acc_c)
    ##################################

    # gli invitati devono essere in un tavolo diverso dalle persone con cui non vanno d'accordo
    div_c = [If(p[k] == i, And([p[min(s, INVITATI - 1)] != j for s in postiVicini(k)]) ,True) for i in range(INVITATI) for j in range(i) for k in range(INVITATI) if divisi[i][j] == 1]

    s.add(div_c)

    #################################
    PREF = Array("PREF", IntSort(), IntSort())
    for i in range(INVITATI):
        for j in range (i):
            PREF = Store(PREF, (j + i*INVITATI), int(preferenze[i][j]))

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


    ############################################
    #pretty print del risultato
    if(s.check() == sat):
        m = s.model()
        
        for i in range(INVITATI):
            if i % DIM_TAVOLI == 0:
                print("-------------")
                print("tavolo ", i//DIM_TAVOLI + 1)
            #print(m.evaluate(p[i]), vincoli.columns[m.evaluate(p[i]).as_long()])
            print(vincoli.columns[m.evaluate(p[i]).as_long()])
    else:
        print("unsat")
