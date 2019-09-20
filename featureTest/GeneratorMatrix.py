# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
This program is to implement "transform generator matrix to standard form"
A First Course in Coding Theory by Raymond Hill (OUP, 1986) Theorem 5.4 and Theorem 5.5
"""

import numpy as np

class GeneratorMatrix(object):
    """docstring for GeneratorMatrix."""
    # useful functions
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = egcd(b % a, a)
            return (g, x - (b // a) * y, y)

    def modinv(a, m):
        g, x, y = egcd(a, m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return x % m

    def __init__(self, G=None, p=2, verbose=False):
        super(GeneratorMatrix, self).__init__()
        self.G = None
        """
        There are in all 5 allowed operations:
        0: switch two rows
            OPList.append([0, row1, row2])
        1: multiply a row by a non-zero scalar
            OPList.append([1, row, scalar])
        2: add a scalar multiply of one row (row 1) to another row (row 2)
            OPList.append([2, row1, row2, scalar])
        3: switch two column
            OPList.append([3, col1, col2])
        4: multiply a column by a non-zero scalar
            OPList.append([4, col, scalar])
        """
        self.OPList = [] # the permutation operations to make G standard
        self.K = None
        self.N = None
        self.p = p
        self.verbose = verbose
        self.standardStatus = None # True: self.G is standard, False: not standard, None: not sure

        # self.RowPermutMat * self.G * self.ColPermutMat = standard G
        self.RowPermutMat = None # a permutation matrix of size K x K
        self.ColPermutMat = None # a permutation matrix of size N x N

        self.setG(G)

    def setG(self, G):
        if G is None:
            return
        self.G = np.asarray(G)
        self.K, self.N = self.G.shape
        if self.K > self.N:
            self.G = self.G.T
            self.K, self.N = self.N, self.K
        self.OPList = []
        self.standardStatus = None



    def __checkRow(self, r):
        if r < 0 or r > self.K-1:
            print("row {r} is out of bound".format(r=r))
            return False
        return True

    def __checkCol(self, c):
        if c < 0 or c > self.N-1:
            print("column {c} is out of bound".format(c=c))
            return False
        return True

    def __checkScalarNoneZero(self, s):
        if s%self.p == 0:
            print("scalar {s} is 0 in GF({p})".format(s, self.p))
            return False
        return True

    """
    Op. 0: permutation of rows
    """
    def switchRows(self, r1, r2):
        if not self.__checkRow(r1) or not self.__checkRow(r2):
            # row indexes are not valid
            return
        if r1 != r2:
            tempRow = self.G[r1, :].copy()
            self.G[r1, :] = self.G[r2, :].copy()
            self.G[r2, :] = tempRow.copy()

            # record the operation
            if r1 <= r2:
                self.OPList.append([0, r1, r2])
            else: # make sure that the rows are ordered
                self.OPList.append([0, r2, r1])

            if self.verbose:
                print("r{r1} <-> r{r2}".format(r1=r1, r2=r2))
            self.standardStatus = None

    """
    Op. 1: Multiplication of a row by a non-zero scalar
    """
    def multiRow(self, row, scalar):
        if not self.__checkScalarNoneZero(scalar):
            # scalar should not be zero
            return
        if not self.__checkRow(row):
            # row index out of range
            return
        scalar %= self.p
        if scalar == 1:
            # meaningless
            return
        self.G[row, :] *= scalar
        self.G[row, :] %= self.p # in GF(p) space

        # record the operation
        self.OPList.append([1, row, scalar])

        if self.verbose:
            print("r{row} = r{row} x {scalar}".format(row=row, scalar=scalar))

        self.standardStatus = None

    """
    Op. 2: add a scalar multiple of one row to another
    """
    def addRow(self, r1, r2, scalar=1):
        if not self.__checkScalarNoneZero(scalar):
            # scalar should not be zero
            return
        if not self.__checkRow(r1) or not self.__checkRow(r2):
            # row indexes out of bound
            return
        scalar %= self.p

        row2 = self.G[r2, :].copy()*scalar
        self.G[r1, :] += row2
        self.G[r1, :] %= self.p

        # record the operation
        self.OPList.append([2, r1, r2, scalar])

        if self.verbose:
            print("r{r1} = r{r1} + r{r2} x {scalar}".format(r2=r2, r1=r1, scalar=scalar))

        self.standardStatus = None

    """
    Op. 3: switch two columns
    """
    def switchCols(self, c1, c2):
        if not self.__checkCol(c1) or not self.__checkCol(c2):
            # column indexes out of bound
            return
        if c1 != c2:
            col1 = self.G[:, c1].copy()
            self.G[:, c1] = self.G[:, c2].copy()
            self.G[:, c2] = col1.copy()

            # record the operation
            if c1 < c2:
                self.OPList.append([3, c1, c2])
            else:
                self.OPList.append([3, c2, c1])

            if self.verbose:
                print("c{c1} <-> c{c2}".format(c1=c1, c2=c2))

            self.standardStatus = None

    """
    Op. 4: multiply a column by a non-zero scalar
    """
    def multiCol(self, col, scalar):
        if not self.__checkCol(col):
            # column index out of bound
            return
        if not self.__checkScalarNoneZero(scalar):
            # scalar is zero in GF(p)
            return
        scalar %= self.p
        if scalar == 1:
            # meaningless
            return

        self.G[:, col] *= scalar
        self.G[:, col] %= self.p

        # record the operation
        self.OPList.append([4, col, scalar])

        if self.verbose:
            print("c{col} x {scalar}".format(col, scalar))

        self.standardStatus = None

    def printOps(self):
        for op in self.OPList:
            if op[0] == 0:
                print("r{r1} <-> r{r2}".format(r1=op[1], r2=op[2]))
            elif op[0] == 1:
                print("{row} x {scalar}".format(row=op[1], scalar=op[2]))
            elif op[0] == 2:
                print("r{r1} = r{r1} + r{r2} x {scalar}".format(r1=op[1], r2=op[2], scalar=op[3]))
            elif op[0] == 3:
                print("c{c1} <-> c{c2}".format(c1=op[1], c2=op[2]))
            elif op[0] == 4:
                print("c{col} = c{col} x {scalar}".format(op[1], op[2]))

    def isStandard(self):
        # check diag
        for i in range(self.K):
            if self.G[i, i] != 1:
                self.standardStatus = False
                return False
        checkSumOfCol = np.sum(self.G[:, :self.K], axis=0)
        # checkSum
        if any(checkSumOfCol > 1):
            self.standardStatus = False
            return False
        self.standardStatus = True
        return True

    def standardize(self):
        def cleanCurCol(pivot):
            # make sure that all rows have 0 at pivot's column except that the pivot's row is 1
            for row in range(self.K):
                if row == pivot:
                    continue
                if self.G[row, pivot] != 0:
                    self.addRow(row, pivot, -self.G[row, pivot])

        def makeCurValOne(row, col):
            # find out the inverse of G[row, col] to make it 1
            if self.p == 2: # no need
                return
            val = self.G[row, col]
            valInv = modinv(val, self.p)
            self.multiRow(row, valInv)

        for curPivot in range(self.K):
            # sequentially make [0, 0], [1, 1], ..., [K-1, K-1] to 1
            if self.G[curPivot, curPivot] == 1:
                # current pivot is 1.
                cleanCurCol(curPivot) # zero-out all rows except the pivot's row
            else:
                # current pivot is  1

                if self.G[curPivot, curPivot] == 0:
                    # current pivot is 0.
                    # search for a row/col that has 1 at this column

                    foundFlag = False
                    tgtRow, tgtCol = 0, 0
                    # search for first none-zero element
                    for startPos in range(curPivot, self.K):
                        # search vertically first
                        for row in range(startPos, self.K):
                            if self.G[row, startPos] != 0:
                                tgtRow, tgtCol = row, startPos
                                foundFlag = True
                                break

                        if foundFlag:
                            break

                        for col in range(startPos, self.N):
                            if self.G[startPos, col] != 0:
                                tgtRow, tgtCol = startPos, col
                                foundFlag = True
                                break

                        if foundFlag:
                            break

                    if foundFlag:
                        if tgtRow != curPivot:
                            self.switchRows(tgtRow, curPivot)
                        if tgtCol != curPivot:
                            self.switchCols(tgtCol, curPivot)
                        makeCurValOne(curPivot, curPivot)
                        cleanCurCol(curPivot)
                    else:
                        # cannot find such row/col => all the elements in the G[curPivot:, curPivot:] are zeros
                        break

                else:
                    # current pivot is not 1,
                    # multiply by certain scalar to make it 1

                    makeCurValOne(curPivot, curPivot)
                    cleanCurCol(curPivot)

        self.isStandard()

    def getH(self):
        if self.standardStatus is None:
            self.standardize()
        if self.standardStatus:
            A = self.G[:, self.K:]
            H = np.concatenate([-A.T, np.eye(self.N - self.K)], axis=1)
            H %= self.p
            return H
        else:
            # cannot get check matrix for a non-standardized G
            return None

    def isInSpace(self, X):
        H = self.getH()
        if H is None:
            print("Unable to generate check matrix H")
            return None

        X = np.asarray(X)
        X_r, X_c = X.shape
        if X_r != self.N:
            print("Input X should be a 2-d array of shape ({row}, ...)".format(row=self.N))
            return None

        syndrone = H.dot(X)%2
        isInSpace = [False] * X_c
        for i in range(X_c):
            if any(syndrone[:, i] != 0):
                isInSpace[i] = False
                if self.verbose:
                    print('Codeword {i} failed the checking'.format(i=i))
                    print('c:' + CList[:, i].__str__())
                    print('x:' + XList[:, i].__str__())
            else:
                isInSpace[i] = True
                if self.verbose:
                    print('Codeword {i} is good!'.format(i=i))
        return isInSpace

    def __str__(self):
        return self.G.__str__()

if __name__ == '__main__':
    # initG = np.array([
    #     [0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 1, 1, 0, 0, 1],
    #     [0, 0, 1, 1, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 1, 0],
    #     [1, 0, 1, 1, 1, 1, 0]
    # ])

    # initG = np.array([[0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    # [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    # [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
    # [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
    # [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0],
    # [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]])

    M = 20
    N = 40

    initG = np.random.randint(0, 2, size=(M, N))

    G = GeneratorMatrix(G=initG, p=2, verbose=False)
    print("init G")
    # print(G)

    # G.switchRows(0, 3)
    #
    # # G.multiRow(0, 2) # useless for GF(2)
    # # print(G)
    #
    # G.addRow(4, 0, -1)
    #
    # G.switchRows(3, 1)
    # G.addRow(3, 2, -1)
    # G.addRow(4, 2, -1)
    #
    # G.switchCols(6, 3)

    G.standardize()

    print("-"*20)
    # G.printOps()
    print(G.isStandard())


    H = G.getH()

    iters = 15
    CList = np.random.randint(0, 2, size=(M, iters))

    XList = initG.T.dot(CList) % 2

    # XList += np.random.randint(0, 2, size=(N, iters))
    XList %= 2


    syndrone = H.dot(XList)%2

    for i in range(iters):
        if any(syndrone[:, i] != 0):
            print('Codeword {i} failed the checking'.format(i=i))
            print('c:' + CList[:, i].__str__())
            print('x:' + XList[:, i].__str__())
        else:
            print('Codeword {i} is good!'.format(i=i))
