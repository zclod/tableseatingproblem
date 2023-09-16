from z3 import *
import pandas as pd
import numpy as np

INVITATI = 10

TAVOLI = [3,2,3,2]

def postiVicini1(posto):
    acc = 0
    for i in range(NUM_TAVOLI):
        if posto >= (acc-1) and posto < (acc + TAVOLI[i]):
            return [acc + j for j in range(TAVOLI[i])]

        acc += TAVOLI[i]
    return []

if __name__ == "__main__":

    NUM_TAVOLI = len(TAVOLI)
    POSTO_INIZIALE = []
    
    x=0
    for i in range(NUM_TAVOLI):
        POSTO_INIZIALE.append(x)
        x += TAVOLI[i]


    vincoli = pd.read_csv("test.csv")

    accompagnatori = np.zeros(vincoli.shape, int)
    accompagnatori[vincoli == 100] = 1

    divisi = np.zeros(vincoli.shape, int)
    divisi[vincoli == -100] = 1

    preferenze = vincoli.to_numpy()
    preferenze[preferenze==100] = 0
    preferenze[preferenze==-100] = 0

    s = Optimize()

    ###################################

    # un posto per ogni invitato
    p = [Int("p_%s" % i) for i in range(INVITATI)]

    # ad ogni posto deve corrispondere un unico invitato
    val_p = [And(0 <= p[i], p[i] < INVITATI) for i in range(INVITATI)]

    # tutti gli invitati devono avere un posto
    tutti_seduti = [Distinct([p[i] for i in range(INVITATI)])]


    ##################################
    # gli invitati devono essere seduti nello stesso tavolo dei propri accompagnatori
    acc_c = [Or([Or([And(p[s] == i, p[t] == j) for s in postiVicini1(POSTO_INIZIALE[k]) for t in postiVicini1(POSTO_INIZIALE[k]) if (s < INVITATI and t < INVITATI)]) for k in range(NUM_TAVOLI)]) for i in range(INVITATI) for j in range(INVITATI) if accompagnatori[i][j] == 1]

    ##################################

    ## gli invitati devono essere in un tavolo diverso dalle persone con cui non vanno d'accordo
    div_c = [Not(Or([Or([And(p[s] == i, p[t] == j) for s in postiVicini1(POSTO_INIZIALE[k]) for t in postiVicini1(POSTO_INIZIALE[k]) if (s < INVITATI and t < INVITATI)]) for k in range(NUM_TAVOLI)])) for i in range(INVITATI) for j in range(INVITATI) if divisi[i][j] == 1]


    #################################
    PREF = Array("PREF", IntSort(), IntSort())
    for i in range(INVITATI):
        for j in range (i):
            PREF = Store(PREF, (j + i*INVITATI), int(preferenze[i][j]))


    ints = []
    for t in range(NUM_TAVOLI):
        for i in range(TAVOLI[t]):
            for j in range(i+1,TAVOLI[t]):
                if (j + POSTO_INIZIALE[t]) < INVITATI and (i + POSTO_INIZIALE[t]) < INVITATI:
                    i1 = p[i + POSTO_INIZIALE[t]]
                    i2 = p[j + POSTO_INIZIALE[t]]
                    s.add(i1 > i2)
                    ints.append(Select(PREF,(i2 + i1*INVITATI)))

    #################################

    s.add(val_p)
    s.add(tutti_seduti)
    s.add(acc_c)
    s.add(div_c)
    s.maximize(sum(ints))

    #################################
    #pretty print the final result

    if(s.check() == sat):
        m = s.model()
        
        print("-------------")
        print("tavolo 1")

        t = 0
        acc = TAVOLI[0]
        for i in range(INVITATI):
            print(vincoli.columns[m.evaluate(p[i]).as_long()])
            if (i+1) == acc and (i+1) < INVITATI:
                t += 1
                acc += TAVOLI[t]
                print("-------------")
                print("tavolo ", t + 1)
    else:
        print("unsat")
