"""
Network class is in charge of:
1. Storing M - User Cache Size, N - Number of Files, K - Number of Users
2. Storing User instances, Server instance, and attacker instance
"""
import numpy as np
from scipy import special
import itertools

from Server import Server
from User import User
from tabulate import tabulate

T_BE_INTEGER = True

class Network():

    def __init__(self, M, N, K, t=None, fileId2Alphabet=False):

        self.M = M
        self.N = int(N)
        self.K = int(K)
        if t is None:
            self.t = self.M * self.K / self.N
        else:
            self.t = t
            self.M = self.t * self.N/self.K  # make up the missing block of M 


        if T_BE_INTEGER and self.t != int(self.t):
            raise Exception("Make sure t = M*K/N is an integer")
        
        self.numOfSubfile = int(special.comb(self.K, self.t))
        self.numOfCodedSubfiles = int(special.comb(self.K, self.t+1))

        self.fileId2Alphabet = fileId2Alphabet

        self.server = Server(self.M, self.N, self.K, self.t, self.fileId2Alphabet)
        self.userset = [User(id, self.M, self.N, self.K, self.t, fileId2Alphabet=fileId2Alphabet) for id in range(self.K)]

        self.placementDone = False

    def placement(self, isRandom=False, verboseForUser=False, verboseForCache=False):
        Z = self.server.generateZ(isRandom=isRandom)
        for userId in range(self.K):
            self.userset[userId].setZ(Z[userId, :])
            if verboseForUser:
                # self.userset[userId].printUserDetail(fileId2Alphabet=fileId2Alphabet)
                print(self.userset[userId])
        if verboseForCache:
            self.printCacheContent(Z)

        self.placementDone = True
    
    def delivery(self, D=None, verbose=False):
        if not self.placementDone:
            self.placement(verbose=verbose)

        if D is None:
            D = [self.userset[id].genD() for id in range(self.K)]
        
        if verbose:
            print("D:", D)
        
        X, groupList = self.server.generateX(D)

        if verbose:
            print("Server Transmission is:")
            print(self.printableServerTransmission(X))
        
        return D, X, groupList

    def printableServerTransmission(self, X, inList=False, fileId2Alphabet=False):
        printoutList = []
        totalRow, totalCol = X.shape
        for row in range(totalRow):
            subfileList = []
            for col in range(totalCol):
                if X[row][col]:
                    fileId = int(col / self.numOfSubfile)
                    subfileId = int(col % self.numOfSubfile)
                    if fileId2Alphabet:
                        subfileList.append("{fileIdChr}{subfileId}".format(fileIdChr=chr(65+fileId), subfileId=subfileId+1))
                    else:
                        subfileList.append("{fileId}-{subfileId}".format(fileId=fileId, subfileId=subfileId))
            if len(subfileList):
                printoutList.append(" + ".join(subfileList))
                # printoutList.append("{id}:{subfileInfo}".format(id=row, subfileInfo=" + ".join(subfileList)))
        if not inList:
            return " || ".join(printoutList)
        else:
            return printoutList

    
    def printCacheContent(self, Z):
        if self.fileId2Alphabet:
            header = ["UserId"] + [chr(65+fileId)+""+str(subfileId+1) for fileId in range(self.N) for subfileId in range(self.numOfSubfile)]
        else:
            header = ["UserId"] + [str(fileId)+"-"+str(subfileId) for fileId in range(self.N) for subfileId in range(self.numOfSubfile)]
        UserId = np.asarray([range(self.K)]).T
        print(tabulate(np.hstack([UserId, Z]), headers=header))
    
    def allD(self):
        curD = [0] * self.K
        while curD != [self.N-1]*self.K:
            yield curD
            for checkPos in range(self.K-1, -1, -1):
                if curD[checkPos] < self.N-1:
                    curD[checkPos] += 1
                    break
                else:
                    curD[checkPos] = 0
        yield curD
    
    def __str__(self):
        print_template = """M:{M}\nN:{N}\nK:{K}\nt:{t}"""

        return print_template.format(M=self.M, N=self.N, K=self.K, t=self.t)


if __name__ == "__main__":
    # if t is specified, M is not needed. Currently, I only consider t to be a positive integer.
    # M: unified cache size per user (if t is specified, M is not useful anymore)
    # N: number of files in the network
    # K: number of users in the network
    # t: M*K/N, 
    # M, N, K, t = -1, 3, 3, 1
    M, N, K, t = -1, 3, 5, 3
    # M, N, K, t = -1, 4, 5, 2

    codedCachingNetwork = Network(M=M, N=N, K=K, t=t, fileId2Alphabet=True)
    print(codedCachingNetwork)
    # codedCachingNetwork.placement(verboseForCache=True, verboseForUser=True, isRandom=True)
    codedCachingNetwork.placement(verboseForCache=True, verboseForUser=True, isRandom=False)
    X_D_table = []
    # for D in itertools.combinations_with_replacement(range(N), K):
    for D in codedCachingNetwork.allD():
        D, X, groupList = codedCachingNetwork.delivery(verbose=False, D=D) # generate X based on D
        groupList
        D_str = ",".join(list(map(lambda d: chr(65+ d), D)))
        X_D_table.append(["["+D_str+"]"] + codedCachingNetwork.printableServerTransmission(X, inList=True, fileId2Alphabet=True))

    # header = ["D", "X"]
    header = ["D"] + groupList
    print(tabulate(X_D_table, headers=header))


