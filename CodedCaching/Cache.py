# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import json
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
        self._freeSpace = 0

        if inStr:
            self.fromString(inStr)


    """
    Simple variable set/get
    """
    def setM(self, M):
        self._M = M

    def getM(self):
        return self._M

    def setCacheContent(self, cacheContent):
        for csubfile in cacheContent:
            self.addCacheSubfile(csubfile)

    def getCacheContent(self):
        return self._Z

    def getFreeSpace(self):
        return self._freeSpace

    """
    add/del/check cache subfile
    """
    def hasCacheSubfile(self, csubfile):
        if isinstance(csubfile):
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
            if csubfileSize <= self._freeSpace:
                self._Z[csubfileId] = csubfile
                self._freeSpace -= csubfileSize
            else:
                # no space for this subfile
                pass
        else: # replace the current subfile
            csubfileInCacheSize = self._Z[csubfileId].getSubfileSize()
            if self._freeSpace +  csubfileInCacheSize >= csubfileSize:
                self._Z[csubfileId] = csubfile
                self._freeSpace += csubfileInCacheSize - csubfileSize

    def delCacheSubfile(self, csubfileId):
        if self.hasCacheSubfile(csubfileId):
            csubfile = self._Z.pop(csubfileId)
            self._freeSpace += csubfile.getSubfileSize()

    """
    nice printout
    """
    def __str__(self):
        printout = """"""
        printout += "free/total: {free}/{total}\n".format(self._freeSpace, self._M)
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
