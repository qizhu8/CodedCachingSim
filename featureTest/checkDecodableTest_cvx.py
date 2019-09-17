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

M = 20      # number of subfiles in cache (row of Z)
N = 100     # number of subfiles in the system (column of Z)


# to make sure the result for each simulation is the same, we manually set the random seed
np.random.seed(seed=20)
Z = np.random.randint(0, 2, size=(M, N))

targetCIdx = [0, 3, 5, 6, 15, 12]
targetC = np.zeros((M, 1))
targetC[targetCIdx] = 1

x = Z.T.dot(targetC)

# x = np.zeros((N,))

# for row in targetC:
    # x += Z[row]
x %= 2

print(x)

#"""
# the task is to use cvxpy to find out the indexes of rows in "Z" that are used to generate "x"

# create the variable to be optimized
C = cvxpy.Variable((M, 1), boolean=True)
bounds = cvxpy.Variable((N, 1), integer=True)
reminder = cvxpy.Variable((N, 1), boolean=True)
# create the constraints
constraints = []
# for col in range(N):
<<<<<<< HEAD:featureTest/checkDecodableTest.py
for col in range(M): # even though we need to use range(N), since Z is of rank M (ideally), we only need to choose M linear independent columns to get the result. This can largely accelerate the solving process.
    constraint = Z[:, col].T * C + x[0, col] <= bounds[col, 0] * 2 + reminder[col, 0]
=======
for col in range(M): # even though we need to use range(N), but N is sufficiently large
    constraint = Z[:, col].T * C + x[col, 0] <= bounds[col, 0] * 2 + reminder[col, 0]
>>>>>>> 24b163d6e527a00efdb4243fe5436be5d79d3da6:featureTest/checkDecodableTest_cvx.py
    constraints.append(constraint)
    constraint = Z[:, col].T * C + x[col, 0] >= bounds[col, 0] * 2
    constraints.append(constraint)

# objective function
# obj = 0
# for col in range(N):
#     obj += bounds[col, 0] * 2 - (Z[:, col].T * C + x[0, col])
obj = sum(reminder)


# generate cvx problem
decodingProblem = cvxpy.Problem(cvxpy.Minimize(obj), constraints)


# Solving the problem
decodingProblem.solve(solver=cvxpy.GLPK_MI)


if sum(obj.value) != 0:
    print("Could not find optimization result")
else:
    print("Find the result")
    for row in range(M):
        if C.value[row]:
            print(row, )

# print(C.value)
# print(obj.value)
# print(bounds.value)
# print(reminder.value)

#"""
