#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import base64
import numpy as np

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
        self._cache = {} # a dictionary storing the csubfile
        self._usedSpace = 0
        self._subfileIndexing = {} # used to store the index for each uncoded subfile
        self._Z = {}      # a dictionary storing the coded subfiles in cache of each coded subfile size. E.g. _Z[1] is a 2-d matrix in GF(2)
        self._ZUpToDate = {}
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
        self.clear()
        for csubfile in cacheContent:
            self.addCacheSubfile(csubfile)

    def getCacheContent(self):
        return self._cache

    def getUsedSpace(self):
        return self._usedSpace

    """
    add/del/check cache subfile
    """
    def hasCacheSubfile(self, csubfile=None, fileId=-1, subfileId=-1):
        if isinstance(csubfile, CSubfile):
            csubfileId = csubfile.getId()
        elif isinstance(csubfile, int):
            csubfileId = csubfile
        else:
            print('unknown input ', csubfile)
            return False

        if csubfileId in self._cache:
            return True
        return False

    def addCacheSubfile(self, csubfile):
        csubfileId = csubfile.getId()
        csubfileSize = csubfile.getSubfileSize()
        if not self.hasCacheSubfile(csubfile): # new csubfile
            if csubfileSize <= (self._M - self._usedSpace):
                self._cache[csubfileId] = csubfile
                self._usedSpace += csubfileSize
                self._ZUpToDate[csubfileSize] = False
            else:
                # no space for this subfile
                print('no space')
                pass
        else: # replace the current subfile
            csubfileInCacheSize = self._cache[csubfileId].getSubfileSize()
            if (self._M - self._usedSpace) +  csubfileInCacheSize >= csubfileSize: # has space for the replacement
                self._cache[csubfileId] = csubfile
                self._usedSpace += csubfileSize - csubfileInCacheSize
                self._ZUpToDate[csubfileSize] = False

    def delCacheSubfile(self, csubfileId):
        if self.hasCacheSubfile(csubfileId):
            csubfile = self._cache.pop(csubfileId)
            csubfileSize = csubfile.getSubfileSize()
            self._usedSpace -= csubfileSize
            self._ZUpToDate[csubfileSize] = False
        if self._usedSpace < 0:
            self._usedSpace = 0

    def clear(self):
        self._cache = {}
        self._usedSpace = 0
        self._subfileIndexing = {}
        self._Z = {}
        self._ZUpToDate = {}


    """
    Cache Behaviors
    """

    def _genZ(self, subfileSize):
        """
        Generate a matrix for coded subfiles of chosen size in cache.
        E.g.
        [
            0, 1, 0, 0
            0, 0, 1, 1
            1, 0, 1, 0
        ]
        means that there are three subfiles in cache.
            1. subfile is subfile 2,
            2. subfile 3 XOR subfile 4,
            3. subfile 1 XOR subfile 3
        """

        if subfileSize in self._ZUpToDate and self._ZUpToDate[subfileSize]:
            return
        # collect uncoded subfile id
        tag2id = {} # tag: fileId-subfileId   id: the column of subfile in _Z
        id2tag = {}
        curId = 0
        tgtSubfileIdList = []
        for csubfileId in self._cache:
            csubfile = self._cache[csubfileId]
            if csubfile.getSubfileSize() != subfileSize:
                continue
            tgtSubfileIdList.append(csubfileId)
            for fileId, subfileId in csubfile.getSubfileBrief():
                tag = str(fileId) + '-'+str(subfileId)
                if tag not in tag2id:
                    tag2id[tag] = curId
                    id2tag[curId] = tag
                    curId += 1

        # curId now is the num of distinct uncodedsubfiles
        # print(tag2id)
        # print(id2tag)

        self._Z[subfileSize] = np.zeros((len(tgtSubfileIdList), curId))
        for row, csubfileId in enumerate(tgtSubfileIdList):
            csubfile = self._cache[csubfileId]
            for fileId, subfileId in csubfile.getSubfileBrief():
                tag = str(fileId) + '-'+str(subfileId)
                curId = tag2id[tag]
                self._Z[subfileSize][row, curId] = 1

        self._ZUpToDate[subfileSize] = True
        # print(self._Z[subfileSize])




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
        for csubfileId in self._cache:
            printout += self._cache[csubfileId].__str__() + '\n'
        return printout


    """
    serilization
    """
    def toString(self):
        ZDict = {id: self._cache[id].toString() for id in self._cache}
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


        uncodedsubfile11 = CSubfile(id=11, subfileSet={subfile11})
        uncodedsubfile21 = CSubfile(id=21, subfileSet={subfile21})
        uncodedsubfile31 = CSubfile(id=31, subfileSet={subfile31})
        uncodedsubfile42 = CSubfile(id=42, subfileSet={subfile42})

        subfileSet1 = {subfile21, subfile31, subfile42}
        codedSubfile2 = CSubfile(id=20, subfileSet=subfileSet2)

        self.setM(10)
        self.addCacheSubfile(uncodedsubfile1)
        self.addCacheSubfile(codedSubfile2)

if __name__=='__main__':

    subfile11 = Subfile(fileId=1, subfileId=1, subfileSize=1, content=b'\x11')
    subfile21 = Subfile(fileId=2, subfileId=1, subfileSize=1, content=b'\x21')
    subfile31 = Subfile(fileId=3, subfileId=1, subfileSize=1, content=b'\x31')
    subfile42 = Subfile(fileId=4, subfileId=2, subfileSize=1, content=b'\x42')
    # subfileSet = {subfile11, subfile21, subfile31, subfile42}



    uncodedsubfile11 = CSubfile(subfileSet={subfile11})
    uncodedsubfile21 = CSubfile(subfileSet={subfile21})
    uncodedsubfile31 = CSubfile(subfileSet={subfile31})
    uncodedsubfile42 = CSubfile(subfileSet={subfile42})

    subfileSet1 = {subfile21, subfile31, subfile42}

    codedSubfile1 = CSubfile(subfileSet=subfileSet1)

    cache = Cache(M=20)
    cache.addCacheSubfile(uncodedsubfile11)
    cache.addCacheSubfile(uncodedsubfile21)
    cache.addCacheSubfile(uncodedsubfile31)
    cache.addCacheSubfile(uncodedsubfile42)
    cache.addCacheSubfile(codedSubfile1)

    # print(cache)

    cache._genZ(1)


    #
    # cacheStr = cache.toString()
    #
    # cacheFromStr = Cache(inStr=cacheStr)
    # print(cacheFromStr)
