from z3 import *
import pandas as pd
import numpy as np

###################################
# global variables

GUESTS = 10

TABLES = [3,3,2,2]

###################################
# utilities

def sumscan(l):
    acc = 0
    result = [acc]
    for i in range(len(l)):
        acc += l[i]
        result.append(acc)
    return result

def neighbours(seat):
    startingSeats = sumscan(TABLES)
    return [ startingSeats[i] + j
            for i in range(len(TABLES))
            for j in range(TABLES[i])
            if ((seat >= startingSeats[i] and seat < startingSeats[i+1])) ]




###################################
# model definition

if __name__ == "__main__":

    numTables = len(TABLES)
    tablesStartingSeats = sumscan(TABLES)
    
    # constraint matrix, 100 and -100 are hard constraints, intermediate values are just preferences
    costraints = pd.read_csv("test.csv")

    seatNeighbour = np.zeros(costraints.shape, int)
    seatNeighbour[costraints == 100] = 1

    separated = np.zeros(costraints.shape, int)
    separated[costraints == -100] = 1

    preferences = costraints.to_numpy()
    preferences[preferences==100] = 0
    preferences[preferences==-100] = 0

    #solver
    s = Optimize()

    ###################################
    # model variables

    # one seat for every guest
    seat = [Int("seat_%s" % i) for i in range(GUESTS)]

    # z3 "matrix" to be accessed throught z3 variables as indexes
    PREF = Array("PREF", IntSort(), IntSort())
    for i in range(GUESTS):
        for j in range (i):
            PREF = Store(PREF, (j + i*GUESTS), int(preferences[i][j]))

    ###################################
    # Solution constraints

    # for every seat there must be a guest assigned
    seat_val = [And(0 <= seat[i], seat[i] < GUESTS) for i in range(GUESTS)]

    # every guest must have a unique seat
    everyone_seated = [Distinct([seat[i] for i in range(GUESTS)])]

    # every guest must be at the same table of its seat neighbours
    neighbour_c = [Or([Or([And(seat[s] == i, seat[t] == j) for s in neighbours(tablesStartingSeats[k])
                     for t in neighbours(tablesStartingSeats[k]) if (s < GUESTS and t < GUESTS)])
                 for k in range(numTables)]) 
             for i in range(GUESTS) 
             for j in range(GUESTS) if seatNeighbour[i][j] == 1]

    # every guest must be in a different table with respect to the guests marked as separated
    separated_c = [Not(Or([Or([And(seat[s] == i, seat[t] == j) for s in neighbours(tablesStartingSeats[k])
                         for t in neighbours(tablesStartingSeats[k]) if (s < GUESTS and t < GUESTS)])
                     for k in range(numTables)]))
             for i in range(GUESTS)
             for j in range(GUESTS) if separated[i][j] == 1]

    #################################
    # Find the optimal solution

    # list of preference values computed for every table to be maximized
    totalPreference = []
    for t in range(numTables):
        for i in range(TABLES[t]):
            for j in range(i+1,TABLES[t]):
                if (j + tablesStartingSeats[t]) < GUESTS and (i + tablesStartingSeats[t]) < GUESTS:
                    i1 = seat[i + tablesStartingSeats[t]]
                    i2 = seat[j + tablesStartingSeats[t]]
                    #impose an ordering constraint to the table for performance reason
                    s.add(i1 > i2)
                    totalPreference.append(Select(PREF,(i2 + i1*GUESTS)))

    #################################

    s.add(seat_val)
    s.add(everyone_seated)
    s.add(neighbour_c)
    s.add(separated_c)
    s.maximize(sum(totalPreference))

    #################################
    #pretty print the final result

    if(s.check() == sat):
        m = s.model()
        
        print("-------------")
        print("table 1")

        t = 0
        acc = TABLES[0]
        for i in range(GUESTS):
            print(costraints.columns[m.evaluate(seat[i]).as_long()])
            if (i+1) == acc and (i+1) < GUESTS:
                t += 1
                acc += TABLES[t]
                print("-------------")
                print("table", t + 1)
    else:
        print("unsat")
