from z3 import *
import pandas as pd
import numpy as np
import sys

import datetime

set_param('parallel.enable', True)
###################################
# global variables

TABLES = [int(i) for i in sys.argv[1:]]
NUM_TABLES = len(TABLES)

if NUM_TABLES == 0:
    print("Usage: cat <constraints.csv> | python seating.py <table1_size> <table2_size> ...", file=sys.stderr)
    sys.exit(1)

###################################
# utilities

def printModel(m, names):
    for t in range(NUM_TABLES):
        print("-------------")
        print("table", t + 1)
        for g in range(num_guests):
            if m.evaluate(seats[t][g]):
                print(names[g])

###################################
# model definition

if __name__ == "__main__":

    # constraint matrix, 100 and -1 are hard constraints, intermediate values are just preferences
    # constraints = pd.read_csv("prova1.csv")
    constraints = pd.read_csv(sys.stdin)

    seatNeighbour = np.zeros(constraints.shape, int)
    seatNeighbour[constraints == 100] = 1

    separated = np.zeros(constraints.shape, int)
    separated[constraints == -1] = 1

    connections = constraints.to_numpy()
    connections[connections < 0] = 0

    num_guests = len(constraints.columns)
    guests_names = constraints.columns

    min_known_neighbours = 0

    #solver
    s = Optimize()
    #s = Solver()

    ###################################
    # model variables

    # one seat for every guest
    seats = [[Bool("table_%s_seat_%s" % (t, g)) for g in range(num_guests)] for t in range(NUM_TABLES)]

    colocated = [[Bool("guest_%s_guest_%s" % (g1, g2)) for g2 in range(g1)] for g1 in range(num_guests)]

    same_table = [[[Bool("g_%s_g%s_t%s" % (g1, g2, t)) 
                    for t in range(NUM_TABLES)]
                   for g2 in range(g1)]
                  for g1 in range(num_guests)]

    ###################################
    # Solution constraints

    print("start constraints generation", datetime.datetime.now())

    everyone_seated_c = [Sum([(seats[t][g]) for t in range(NUM_TABLES)]) == 1 for g in range(num_guests)]

    tavoli_c = [Sum([seats[t][g] for g in range(num_guests)]) <= TABLES[t] for t in range(NUM_TABLES)]

    link_table_seat_c = [And([
        Or([
            Not(seats[t][g1]),
            Not(seats[t][g2]),
            same_table[g1][g2][t]
            ]),
        Implies(same_table[g1][g2][t], seats[t][g1]),
        Implies(same_table[g1][g2][t], seats[t][g2])
        ])
                           for g1 in range(num_guests)
                           for g2 in range(g1)
                           for t in range(NUM_TABLES)]

    link_colocated_same_table_c = [
            Sum([same_table[g1][g2][t] for t in range(NUM_TABLES)]) == colocated[g1][g2]
            for g1 in range(num_guests)
            for g2 in range(g1)
            ]

    neighbour_c = [colocated[g1][g2] for g1 in range(num_guests) for g2 in range(g1) if seatNeighbour[g1][g2] == 1]

    separated_c = [Not(colocated[g1][g2]) for g1 in range(num_guests) for g2 in range(g1) if separated[g1][g2] == 1]

    min_known_neighbours_c = [
            Sum([same_table[g2][g][t]
                 for g2 in range(g + 1, num_guests)
                 for t in range(NUM_TABLES)
                 if connections[g2][g] > 0]) +
            Sum([same_table[g][g1][t]
                 for g1 in range(g)
                 for t in range(NUM_TABLES)
                 if connections[g][g1] > 0]) >= min_known_neighbours
            for g in range(num_guests)]


    totalPreference = Sum([
        connections[g1][g2] * colocated[g1][g2]
        for g1 in range(num_guests)
        for g2 in range(g1)
        if connections[g1][g2] > 0
        ])

    s.add(everyone_seated_c)
    s.add(tavoli_c)
    s.add(link_table_seat_c)
    s.add(link_colocated_same_table_c)
    s.add(neighbour_c)
    s.add(separated_c)
    s.add(min_known_neighbours_c)

    # s.add(seats[0][0])

    #s.maximize(totalPreference)

    print("start model check", datetime.datetime.now())

    if s.check() == sat:
        m = s.model()
        lb = m.evaluate(totalPreference)

        print()
        print("current solution score: ", lb)
        printModel(m, guests_names)

        while True:
            s.push()
            s.add(totalPreference > lb)

            if s.check() == sat:
                lb = s.model().evaluate(totalPreference)
                print()
                print("current solution score: ", lb)
                printModel(s.model(), guests_names)
                s.pop()

            else:
                break

    else:
        print("unsat")
        print("end model check", datetime.datetime.now())
