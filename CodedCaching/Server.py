"""
Server
"""
import numpy as np
from scipy import special
import itertools

class Server():
    def __init__(self, M, N, K, t, fileId2Alphabet=False):
        self.M = M
        self.N = int(N)
        self.K = int(K)
        self.t = int(t)

        # Z is a binary table of K x N*(K choose t), where (K choose t) is the number of subfiles a file is split into
        self.numOfSubfile = int(special.comb(self.K, self.t))
        self.numOfCodedSubfiles = int(special.comb(self.K, self.t+1))
        self.Z = None

        self.placementDone = False

        self.fileId2Alphabet=fileId2Alphabet    # true: file indexes are represented in A-Z rather than numbers

    """
    ========Placement Phase Related=========
    """
    def generateZ(self, isRandom=False):
        """Public function"""
        self._generateZ_std()
        if isRandom:
            self._permutateZ()
        
        return self.Z


    def _generateZ_std(self):
        """Standard. The assignment of subfiles follows the order in n-choose-k"""
        subfileIdx = 0

        self.Z = np.zeros((self.K, self.N*self.numOfSubfile), dtype=bool)
        for userLst in itertools.combinations(range(self.K), self.t):
            # go through all combinations of t users
            for user in userLst:
                for fileIdx in range(self.N):
                    self.Z[user][subfileIdx + self.numOfSubfile*fileIdx] = True
            subfileIdx += 1
        self.placementDone = True
    
    def _permutateZ(self):
        """Randomly switch two columns in Z belongs to the same file.
            Switch two columns won't change the cache capacity, the number subfiles each user has, the number of users each subfile is cached by
            Switch two rows belongs to the same file of two users also won't break the rule.
        """
        if not self.placementDone:
            self._placementPrep_std()
        
        columnOrder = np.asarray([])
        for fileIdx in range(self.N):
            startCol = fileIdx * self.numOfSubfile
            # permute between users
            rowPermutOrder = np.random.permutation(self.K)
            self.Z[:, startCol:startCol+self.numOfSubfile] = self.Z[rowPermutOrder, startCol:startCol+self.numOfSubfile]

            # permute between subfiles (but we only can generate the permutation order for current file related subfiles)
            colPermutOrder = np.random.permutation(self.numOfSubfile)
            columnOrder = np.concatenate([columnOrder, colPermutOrder+startCol])
        columnOrder = np.asarray(columnOrder, dtype=int)
        self.Z = self.Z[:, columnOrder]
    
    """
    =========Delivery Phase Related==========
    """
    def generateX(self, D):
        return self._generateX(D)
        
    def _generateX(self, D):
        """
        This function generates all coded subfiles in the server transmission by iterating all groups of t+1 users. 
        """
        codedSubfileList = np.zeros((self.numOfCodedSubfiles, self.numOfSubfile*self.N), dtype=bool)
        groupList = []      # indicating for whom each coded subfile is generated
        D = np.asarray(D, dtype=int)
        codedSubfileIdx = 0
        for group in itertools.combinations(range(self.K), self.t+1):
            D_select = D[np.asarray(group)]

            # check how many users possess each subfile
            Z_select = self.Z[group, :]
            Z_select_sum = np.sum(Z_select, axis=0)
                        
            # rule out subfile that that are possessed by < t user
            # the reminder are subfiles is needed by one user
            Z_select_sum = Z_select_sum >= self.t 

            # zero out columns that are not needed by any user
            uselessCols = np.ones((self.numOfSubfile*self.N), dtype=bool)
            for row, usefulFileIdx in enumerate(D_select):
                startCol = usefulFileIdx * self.numOfSubfile
                uselessCols[startCol:startCol+self.numOfSubfile] &= False
            Z_select_sum[uselessCols] &= False
            # vote for subfiles that user i needs
            for row, d_i in enumerate(D_select):
                startCol = d_i * self.numOfSubfile
                # a coded subfile voted by user "row" must be 
                # 1. Z_select_sum (the subfile that can be recover) 
                # 2. Z_select the subfile is needed (not in cache) by the user 
                codedSubfileList[codedSubfileIdx, startCol:startCol+self.numOfSubfile] += \
                    Z_select_sum[startCol:startCol+self.numOfSubfile] & ~Z_select[row, startCol:startCol+self.numOfSubfile] 

            if self.fileId2Alphabet:
                group = [member+1 for member in group]

            groupList.append(group)
            codedSubfileIdx += 1
        
        return codedSubfileList, groupList

    def setPrintoutMode(self, fileId2Alphabet):
        self.fileId2Alphabet = fileId2Alphabet

    
if __name__ == "__main__":
    M = 1
    N = 3
    K = 3
    t = round(M*K/N)
    server = Server(M=1, N=3, K=3, t=t)
    server.generateZ(isRandom=False)
    print(server.Z+0)
    
    D = [1, 1, 1]
    X = server.generateX(D)

