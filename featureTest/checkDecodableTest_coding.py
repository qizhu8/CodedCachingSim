# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from GeneratorMatrix import GeneratorMatrix

import numpy as np

M = 20
N = 40

Z = np.random.randint(0, 2, size=(M, N))
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
