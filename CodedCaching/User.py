"""
User
"""

import numpy as np
from scipy import special
import copy 
class User():
    def __init__(self, id, M, N, K, t, Z = [], popularity=None, fileId2Alphabet=False):
        self.M = M
        self.N = int(N)
        self.K = int(K)
        self.t = int(t)
        self.id=int(id)

        self.Z = Z
        self.popularity = None
        self.setPopularity(popularity)
         
        # Z is a binary table of K x N*(K choose t), where (K choose t) is the number of subfiles a file is split into
        self.numOfSubfile = int(special.comb(self.K, self.t))
        self.numOfCodedSubfiles = int(special.comb(self.K, self.t+1))

        self.fileId2Alphabet=fileId2Alphabet    # true: file indexes are represented in A-Z rather than numbers
    
    def setPopularity(self, popularity):
        if popularity is None: # default uniform
            self.popularity = np.ones((self.N)) / self.N
        else:
            self.popularity = np.asarray(popularity)
            self.popularity /= np.sum(self.popularity)

    def genD(self):
        return np.random.choice(self.N, 1, p=self.popularity)[0]
    
    def setZ(self, Z):
        self.Z = copy.copy(np.asarray(Z))
    
    def __str__(self):
        printout = ""
        printout += "User: {id}\n".format(id=self.id)

        printout += "\tPop: {pop}\n".format(pop=self.popularity.__str__())

        subfileList = []
        for col in range(min(self.numOfSubfile * self.N, len(self.Z))):
            if self.Z[col]:
                fileId = int(col / self.numOfSubfile)
                subfileId = col % self.numOfSubfile
                if self.fileId2Alphabet:
                    subfileList.append("{fileIdChr}{subfileId}".format(fileIdChr=chr(65+fileId), subfileId=subfileId+1))
                else:
                    subfileList.append("{fileId}-{subfileId}".format(fileId=fileId, subfileId=subfileId))
        if subfileList:
            printout += "\t" + ",".join(subfileList)
        
        return printout
    
    def setPrintoutMode(self, fileId2Alphabet):
        self.fileId2Alphabet = fileId2Alphabet
    
if __name__ == "__main__":
    M, N, K, t = 1, 3, 3, 1
    user = User(id=1, M=M, N=N, K=K, t=t, fileId2Alphabet=True)
    # user.setPrintoutMode(True)
    user.setZ([0, 1, 0, 0, 0, 1, 1, 0, 0])
    print(user)