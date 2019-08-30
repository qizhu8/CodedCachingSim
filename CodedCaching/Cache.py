# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import json
from Subfile import Subfile
from CSubfile import CSubfile

class Cache(object):
    """
    docstring for Cache.

    Class Cache emulates cache in the Coded Caching network.
    """

    def __init__(self, M=0, cacheContent=[], inStr=""):
        """
        M: unified cache size
        """
        super(Cache, self).__init__()
        self._M = 0
        self._Z = {} # a dictionary storing the cache bit
        self._usedSpace = 0

        if inStr:
            self.fromString(inStr)
        else:
            self._M = M
            self.setCacheContent(cacheContent)


    """
    Simple variable set/get
    """
    def setM(self, M):
        if M >= self._usedSpace: # still not touching user cache
            self._M = max(0, M)
            return True
        else:
            print("There are {used} > {targetM} unified bits in cache. ".format(used=self._usedSpace, targetM=self._M))
            print("You can remove some of the files in cache.")
            return False

    def getM(self):
        return self._M

    def setCacheContent(self, cacheContent):
        if not isinstance(cacheContent, list):
            cacheContent = list(cacheContent)
        for csubfile in cacheContent:
            self.addCacheSubfile(csubfile)

    def getCacheContent(self):
        return self._Z

    def getUsedSpace(self):
        return self._usedSpace

    """
    add/del/check cache subfile
    """
    def hasCacheSubfile(self, csubfile):
        if isinstance(csubfile, CSubfile):
            csubfileId = csubfile.getId()
        elif isinstance(csubfile, int):
            csubfileId = csubfile
        else:
            print('unknown input ', csubfile)
            return False

        if csubfileId in self._Z:
            return True
        return False

    def addCacheSubfile(self, csubfile):
        csubfileId = csubfile.getId()
        csubfileSize = csubfile.getSubfileSize()
        if not self.hasCacheSubfile(csubfile):
            if csubfileSize <= (self._M - self._usedSpace):
                self._Z[csubfileId] = csubfile
                self._usedSpace += csubfileSize
            else:
                # no space for this subfile
                pass
        else: # replace the current subfile
            csubfileInCacheSize = self._Z[csubfileId].getSubfileSize()
            if (self._M - self._usedSpace) +  csubfileInCacheSize >= csubfileSize:
                self._Z[csubfileId] = csubfile
                self._usedSpace += csubfileSize - csubfileInCacheSize

    def delCacheSubfile(self, csubfileId):
        if self.hasCacheSubfile(csubfileId):
            csubfile = self._Z.pop(csubfileId)
            self._usedSpace -= csubfile.getSubfileSize()
        if self._usedSpace < 0:
            self._usedSpace = 0

    def clear(self):
        self._Z = {}
        self._usedSpace = 0


    """
    Cache Behaviors
    """

    def decode(self, instance, soft=True):
        """
        decode BitSequence or CodedSubfile

            instance: supportive instance
            soft:
                - True: only decode the header without returning the actual bits
                - False: return the decode bits
        """
        decodeFuncDict = {
            'BitSequence':self._decodeBitSequence,
            'CSubfile': self._decodeCSubfile
            }
        instanceClass = instance.__class__.__name__
        if instanceClass in decodeFuncDict:
            decodeFunc = decodeFuncDict[instanceClass]
            return decodeFunc(instance, soft=soft)
        else:
            print('Input instance is of class %d, which doesn''t have supportive decode function yet.' % instasnceClass )
            return False, []

    def _decodeBitSequence(self, bitSequence, soft=True):

        return False, []

    def _decodeCSubfile(self, csubfile, soft=True):

        return False, []


    """
    nice printout
    """
    def __str__(self):
        printout = """"""
        printout += "used/total: {used}/{total}\n".format(used=self._usedSpace, total=self._M)
        for csubfileId in self._Z:
            printout += self._Z[csubfileId].__str__() + '\n'
        return printout


    """
    serilization
    """
    def toString(self):
        ZDict = {id: self._Z[id].toString() for id in self._Z}
        d = {'M': self._M, 'Z': ZDict}
        return json.dumps(d)

    def fromString(self, inStr):
        d = json.loads(inStr)
        self._M = d['M']
        ZDict = d['Z']
        for id in ZDict:
            self.addCacheSubfile(CSubfile(inStr=ZDict[id]))

    """
    example
    """
    def exampleSelfSetup(self):
        subfile11 = Subfile(fileId=1, subfileId=1, subfileSize=2)
        subfile21 = Subfile(fileId=2, subfileId=1, subfileSize=1)
        subfile31 = Subfile(fileId=3, subfileId=1, subfileSize=1)
        subfile42 = Subfile(fileId=4, subfileId=2, subfileSize=1)

        subfileSet1 = {subfile11}
        subfileSet2 = {subfile21, subfile31, subfile42}
        uncodedsubfile1 = CSubfile(id=1, subfileSet=subfileSet1)
        codedSubfile2 = CSubfile(id=20, subfileSet=subfileSet2)

        self.setM(3)
        self.addCacheSubfile(uncodedsubfile1)
        self.addCacheSubfile(codedSubfile2)

if __name__=='__main__':
    subfile11 = Subfile(fileId=1, subfileId=1, subfileSize=2)
    subfile21 = Subfile(fileId=2, subfileId=1, subfileSize=1)
    subfile31 = Subfile(fileId=3, subfileId=1, subfileSize=1)
    subfile42 = Subfile(fileId=4, subfileId=2, subfileSize=1)

    subfileSet1 = {subfile11}
    subfileSet2 = {subfile21, subfile31, subfile42}
    uncodedsubfile1 = CSubfile(id=1, subfileSet=subfileSet1)
    codedSubfile2 = CSubfile(id=20, subfileSet=subfileSet2)

    cache = Cache(M=3, cacheContent=[uncodedsubfile1])
    cache.addCacheSubfile(codedSubfile2)

    print(cache)

    cacheStr = cache.toString()

    cacheFromStr = Cache(inStr=cacheStr)
    print(cacheFromStr)
