# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
This program is to verify the feasibility of using belief propagation to "decode" the codeword
"""

import cvxpy
import numpy as np

M = 5      # number of subfiles in cache (row of Z)
N = 7     # number of subfiles in the system (column of Z)


# to make sure the result for each simulation is the same, we manually set the random seed
np.random.seed(seed=21)

Z = np.random.randint(0, 2, size=(M, N))
while np.linalg.matrix_rank(Z) != M:
    Z = np.random.randint(0, 2, size=(M, N))


targetCIdx = [0, 1, 3]
targetC = np.zeros((M, 1))
targetC[targetCIdx] = 1

x = Z.T.dot(targetC)
x %= 2

print("The Z is: \n {}".format(Z))
print("The codeword is: \n {}".format(x.T))


#"""
# parametersd


"""
I find out the optimal way.

Treat Z as a generation matrix but not in standard form.
Find out the mutation matrix A to make G=AZ a standard generation matrix.
Use G to find out the standard check matrix H

"""







# if sum(obj.value) != 0:
#     print("Could not find optimization result")
# else:
#     print("Find the result")
#     for row in range(M):
#         if C.value[row]:
#             print(row, ending='')

# print(C.value)
# print(obj.value)
# print(bounds.value)
# print(reminder.value)

#"""
