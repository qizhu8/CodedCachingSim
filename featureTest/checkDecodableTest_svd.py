# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
This program is to verify the feasibility of using pseudo-inverse to check whether a coded subfile is decodable
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
x %= 2

print(x)

#"""

C = np.linalg.pinv(Z.T).dot(x)
print(C)


print("This method is not working")

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