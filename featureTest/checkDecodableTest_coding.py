# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from GeneratorMatrix import GeneratorMatrix

import numpy as np

# M must be smaller than N
M = 100
N = 400

while True:
    Z = np.random.randint(0, 2, size=(M, N))
    if np.linalg.matrix_rank(Z) >= M:
        break

G = GeneratorMatrix(G=Z)
G.standardize()
H = G.standardize()

# now simulate a subfile that can be decoded using Z
GTc = np.random.randint(0, 2, size=(M, 1))

x1 = Z.T.dot(GTc) % 2

x2 = x1.copy()
x2[0] ^= 1

# check x1 is in VZ

rst = G.isInSpace(np.concatenate([x1, x2], axis=1))
print(rst)

# we need to find the inverse of G.RowPermutMat
# The idea is again using row operations.
# First, the RowPermutMat is always of full rank (may need some proofs)
# Then we construct the following matrix R = [RowPermutMat | I]
# When we standardize R, we will end up with [I | inv(RowPermutMat)]
# But!!! BUT!!!!!!! NO NEED FOR THAT TO DECODE x1!!!!!!!!!!!!!!!!
# R = GeneratorMatrix(G=np.concatenate([G.RowPermutMat, np.eye(G.RowPermutMat.shape[0])], axis=1))
# R.standardize()
# RowPermutMat_inv = R.G[:, R.K:]
# initG_2 = RowPermutMat_inv.dot(G.G).dot(G.ColPermutMat) %2

# print(initG_2 - Z) # is all-zero matrix, which means we successfully find the inverse of the RowPermutMat and ColPermutMat



# We can find the corresponding C for X
Colx = G.ColPermutMat.T.dot(x1) %2
Rowc = Colx[:M, :]
c_dec = G.RowPermutMat.T.dot(Rowc) %2
print(c_dec.T)
print(GTc.T+0.0)

print("Is the decoding result the same is the GT?")
print(not any(c_dec - GTc) != 0)
