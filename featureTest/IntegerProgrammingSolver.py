# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
Pre-requests:

1. install cvxpy and cvxopt
pip3 install cvxpy cvxopt
2. install GLPK (Gnu Linear Programming Kit)
    - Mac:
        brew install glpk
    - Linux:
        apt-get install glpk
3. Harvest
"""

import cvxpy
import numpy as np

# The data for the Knapsack problem
# P is total weight capacity of sack
# weights and utilities are also specified
P = 165
weights = np.array([23, 31, 29, 44, 53, 38, 63, 85, 89, 82])
utilities = np.array([92, 57, 49, 68, 60, 43, 67, 84, 87, 72])

# The variable we are solving for
selection = cvxpy.Variable(len(weights), boolean=True)

# The sum of the weights should be less than or equal to P
weight_constraint = weights * selection <= P

# Our total utility is the sum of the item utilities
total_utility = utilities * selection

# We tell cvxpy that we want to maximize total utility
# subject to weight_constraint. All constraints in
# cvxpy must be passed as a list
knapsack_problem = cvxpy.Problem(cvxpy.Maximize(total_utility), [weight_constraint])

# Solving the problem
knapsack_problem.solve(solver=cvxpy.GLPK_MI)

# print out the solution
print(selection.value)
