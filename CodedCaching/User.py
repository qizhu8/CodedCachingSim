# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import json
import numpy as np

from Cache import Cache
from BitSequence import BitSequence

class User(object):
    """
    docstring for User.

    User class emulates the behaviors of a network user.

    """

    def __init__(self, id=0, M=0, N=0, cache=Cache(), popTab=[], inStr=""):
        super(User, self).__init__()

        self._id = 0            # user id
        self._N = 0             # number of files
        self._M = 0             # cache size
        self._prevD = 0         # previous request
        self._cache = Cache()   # local cache
        self._popTab = np.array([])       # file popularity
        if inStr:
            self.fromString(inStr)
        else:
            self.setId(id)
            self.setM(M) # this function includes expanding cache size
            self.setN(N)
            self.setPopTab(popTab)
            self.setCache(cache)


    """
    simple variable set/get
    """

    def setM(self, M):
        if self._cache.setM(M):
            self._M = M
        else:
            return

    def getM(self):
        return self._M

    def setId(self, id):
        self._id = id

    def getId(self):
        return self._id

    def setN(self, N):
        if N > self._N: # expanding
            self._popTab = np.concatenate((self._popTab, np.zeros(((N - self._N), ))), axis=None)
        elif N < self._N:
            self._popTab = self._popTab[:N]
            self._popTab = self._popTab / sum(self._popTab)
        self._N = N

    def getN(self):
        return self._N

    def setPopTab(self, popTab=[], mode=""):
        def uniformDist():
            return np.ones((self._N,))/self._N
        def randomDist():
            randD = np.random.rand(self._N)
            return randD / sum(randD)

        if popTab:
            self._popTab = np.array(popTab)
            self._popTab = self._popTab / sum(self._popTab)
            self._N = len(self._popTab)
        elif mode:
            reactFuncDict = {'uniform': uniformDist, 'random': randomDist}
            if mode in reactFuncDict:
                self._popTab = reactFuncDict[mode]()
            else:
                print('Support modes are: ' + reactFuncDict.keys().__str__())

    def getPopTab(self):
        return self._popTab

    def setCache(self, cache):
        if isinstance(cache, Cache):
            self._cache = cache
            self._M = cache.getM()

    def getCache(self):
        return self._cache

    def clearCache(self):
        self._Cache.clear()


    """
    User Actions
    """
    def genD(self, D=-1):
        if D >= 0: # hacked mode. Generate input demand vector
            self._prevD = D
        else:      # randomly generate demand based on pop Tab
            self._prevD = np.random.choice(np.arange(self._N), p=self._popTab)
        return self._prevD


    """
    nice printout
    """
    def __str__(self):
        printout = "Id: {id}\nM: {M}\n".format(id=self._id, M=self._M)
        # file pop table
        printout += "Pop. Tab.:\n"
        for i in range(self._N):
            printout += "  {id}: {pop:2.2f}%\n".format(id=i, pop = self._popTab[i]*100)
        printout += "Z: "
        printout += self._cache.__str__()
        return printout


    """
    serilization
    """
    def toString(self):
        d = {
                'id':self._id,
                'M': self._M,
                'N': self._N,
                'PopTab': list(self._popTab),
                'Z': self._cache.toString()
            }


        return json.dumps(d)

    def fromString(self, inStr):
        d = json.loads(inStr)

        self._id = d['id']
        self.setM(d['M'])
        self.setN(d['N'])
        self.setPopTab(d['PopTab'])
        self.setCache(Cache(inStr=d['Z']))


if __name__ == '__main__':

    cache = Cache()
    cache.exampleSelfSetup()

    user = User()
    user.setId(999)
    user.setM(3)
    user.setPopTab([1])
    user.setN(5)
    user.setCache(cache)

    user.setPopTab(mode='random')
    print(user)

    userStr = user.toString()

    userFromStr = User(inStr=userStr)
    print(userFromStr)


    for i in range(10):
        d = user.genD()
        print(str(i) + ': ' + str(d))
