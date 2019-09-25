#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import base64
import numpy as np
import copy

from Subfile import Subfile
from CSubfile import CSubfile
from GeneratorMatrix import GeneratorMatrix
from BitSequence import BitSequence

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

    def copy(self):
        return copy.copy(self)

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

    def _getZ(self, subfileSize):
        """
        Get/Generate a matrix for coded subfiles of chosen size in cache.
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
            return copy.deepcopy(self._Z[subfileSize])
            # return self._Z[subfileSize][0].copy(), self._Z[subfileSize][1].copy(), self._Z[subfileSize][2].copy(), self._Z[subfileSize][3].copy()
        # collect uncoded subfile id
        tag2id = {} # tag: fileId-subfileId   id: the column of subfile in _Z
        id2tag = {}
        curId = 0
        tgtSubfileIdList = []
        for csubfileId in self._cache:
            csubfile = self._cache[csubfileId]
            # only focus on csubfiles match the input size
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
        # print("curId=%d tgtCsubfile=%s" %(curId, tgtSubfileIdList.__str__()))

        # self._Z[subfileSize] = np.zeros((len(tgtSubfileIdList), curId))
        Z = np.zeros((len(tgtSubfileIdList), curId))

        for row, csubfileId in enumerate(tgtSubfileIdList):
            csubfile = self._cache[csubfileId]
            for fileId, subfileId in csubfile.getSubfileBrief():
                tag = str(fileId) + '-'+str(subfileId)
                curId = tag2id[tag]
                Z[row, curId] = 1

        G = GeneratorMatrix(G=Z)
        G.standardize()
        self._Z[subfileSize] = [G, tag2id, id2tag, tgtSubfileIdList]
        self._ZUpToDate[subfileSize] = True

        # print(Z)
        return copy.deepcopy(self._Z[subfileSize])
        # return self._Z[subfileSize][0].copy(), self._Z[subfileSize][1].copy(), self._Z[subfileSize][2].copy(), self._Z[subfileSize][3].copy()



    def decode(self, instance, soft=False):
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

    def _decodeBitSequence(self, bitSequence, soft=False):
        CSubfileDict = bitSequence.getCSubfileDict()
        decodingFlag = False
        rstSubfileList = []
        for csubfileId in CSubfileDict:
            # print("decoding " + csubfileId)
            # print(CSubfileDict[csubfileId])
            flag, rstList = self._decodeCSubfile(CSubfileDict[csubfileId], soft)
            decodingFlag |= flag
            rstSubfileList += rstList

            # print("%r %s" % (flag, rstList))
        return decodingFlag, rstSubfileList

    def _decodeCSubfile(self, csubfile, soft=False):
        csubfile = csubfile.copy()
        # print("decoding " + csubfile.getId())

        csubfileSize = csubfile.getSubfileSize()
        csubfileBrief = csubfile.getSubfileBrief()

        # if csubfile is actually uncoded subfile, directly return it.
        if len(csubfileBrief) == 1:
            return True, [csubfile.downgradeToSubfile()]

        # may need to try decoding

        Z, tag2id, id2tag, tgtSubfileIdList = self._getZ(csubfileSize)

        # Assume the vector is of the same size as any other csubfile in cache
        # If there are subfiles that have not shown up before, add columns afterwards
        csubfileVector = np.zeros((1, Z.N))

        #
        curNewSubfileId = len(tag2id)
        numOfUnseenSubfiles = 0
        for fileId, subfileId in csubfileBrief:
            tag = str(fileId) + '-'+str(subfileId)
            if tag in tag2id:
                # this subfile is in cache
                id = tag2id[tag]
                csubfileVector[0, id] = 1
            else:
                # find a subfile not seen before
                tag2id[tag] = curNewSubfileId
                id2tag[curNewSubfileId] = tag

                numOfUnseenSubfiles += 1
                curNewSubfileId += 1

        # cannot decode out a uncoded subfile if there are at least 2 unseen subfiles
        if numOfUnseenSubfiles > 1:
            return False, []

        # if the number of unseen subfiles == 1, check whether the csubfile without the unseen subfile is in Vz
        if numOfUnseenSubfiles == 1:
            if Z.isInSpace(csubfileVector.T)[0]: # isInSpace return a True/False vector as large as input
                # generate the index set of csubfile that can help decoding
                decodingIdxSet = Z.decode(csubfileVector.T)
                # print(decodingIdxSet)

                fileId, subfileId = list(map(int, id2tag[curNewSubfileId-1].split('-')))

                if soft:
                    # if only need the soft decoding result, no need to decode the content,
                    # just return a Subfile instance with proper fileId and subfileId
                    rstSubfile = Subfile(fileId=fileId, subfileId=subfileId, subfileSize=csubfileSize, content=b'')

                else:
                    # follow the decodingIdxSet to actually decode the subfile
                    rstSubfile = csubfile.copy()
                    for checkCSubfileId in range(decodingIdxSet.shape[0]):
                        if decodingIdxSet[checkCSubfileId][0]:
                            rstSubfile.XORSubfile(self._cache[tgtSubfileIdList[checkCSubfileId]])

                return True, [rstSubfile.downgradeToSubfile()]
            else:
                return False, []
            # csubfileVector = np.concatenate([csubfileVector, np.ones((1, numOfUnseenSubfiles))], axis=1)
            # Z.G = np.concatenate([Z.G, np.zeros((Z.K, numOfUnseenSubfiles))], axis=1)

        if numOfUnseenSubfiles == 0:
            rstSubfileList = []
            # we can only check each uncoded subfile
            # csubfileVectorTmp = csubfileVector.copy().T
            csubfileVectorMat = (csubfileVector.copy().T.dot(np.ones((1, Z.N))) + np.eye(Z.N)) %2
            csubfileInSpace = Z.isInSpace(csubfileVectorMat)

            for id in range(Z.N):
                if not csubfileInSpace[id]:
                    continue
                csubfileVectorTmp = np.expand_dims(csubfileVectorMat[:, id], axis=0).T
                # print("checking id=%d tag:%s" % (id, id2tag[id]))
                # print("csubfileVectorTmp")
                # print(csubfileVectorTmp.T)
                decodingIdxSet = Z.decode(csubfileVectorTmp)

                # print("csubfileVector")
                # print(csubfileVector)
                #
                # print("Z")
                # print(Z.initG)
                # print("decodingIdxSet")
                # print(decodingIdxSet.T)

                fileId, subfileId = list(map(int, id2tag[subfileId].split('-')))
                if soft:
                    # if only need the soft decoding result, no need to decode the content,
                    # just return a Subfile instance with proper fileId and subfileId
                    rstSubfile = Subfile(fileId=fileId, subfileId=subfileId, subfileSize=csubfileSize, content=b'')

                else:
                    # follow the decodingIdxSet to actually decode the subfile
                    rstSubfile = csubfile.copy()
                    for checkCSubfileId in range(decodingIdxSet.shape[0]):
                        if decodingIdxSet[checkCSubfileId][0]:
                            rstSubfile.XORSubfile(self._cache[tgtSubfileIdList[checkCSubfileId]])
                rstSubfileList.append(rstSubfile.downgradeToSubfile())

            return len(rstSubfileList)>0, rstSubfileList


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
    subfile41 = Subfile(fileId=4, subfileId=1, subfileSize=1, content=b'\x41')

    subfile12 = Subfile(fileId=1, subfileId=2, subfileSize=1, content=b'\x12')
    subfile22 = Subfile(fileId=2, subfileId=2, subfileSize=1, content=b'\x22')
    subfile32 = Subfile(fileId=3, subfileId=2, subfileSize=1, content=b'\x32')
    subfile42 = Subfile(fileId=4, subfileId=2, subfileSize=1, content=b'\x42')

    subfile51 = Subfile(fileId=5, subfileId=1, subfileSize=1, content=b'\x51')
    # subfileSet = {subfile11, subfile21, subfile31, subfile42}



    uncodedsubfile11 = CSubfile(subfileSet={subfile11})
    uncodedsubfile21 = CSubfile(subfileSet={subfile21})
    uncodedsubfile31 = CSubfile(subfileSet={subfile31})
    uncodedsubfile42 = CSubfile(subfileSet={subfile42})

    codedSubfile1 = CSubfile(subfileSet={subfile21, subfile31, subfile42})
    codedSubfile2 = CSubfile(subfileSet={subfile21, subfile32, subfile41})
    codedSubfile3 = CSubfile(subfileSet={subfile22, subfile31, subfile41})

    decodableSubfile1 = CSubfile(subfileSet={subfile21, subfile31, subfile41, subfile32, subfile42})
    decodableSubfile2 = CSubfile(subfileSet={subfile31, subfile41, subfile51, subfile32, subfile42})

    undecodableSubfile1 = CSubfile(subfileSet={subfile21, subfile31, subfile41, subfile22, subfile32, subfile42})

    cache = Cache(M=20)
    # cache.addCacheSubfile(uncodedsubfile11)
    # cache.addCacheSubfile(uncodedsubfile21)
    # cache.addCacheSubfile(uncodedsubfile31)
    # cache.addCacheSubfile(uncodedsubfile42)
    cache.addCacheSubfile(codedSubfile1)
    cache.addCacheSubfile(codedSubfile2)
    cache.addCacheSubfile(codedSubfile3)


    # decode csubfile
    print('='*20)
    decodable, decodeRstList = cache.decode(CSubfile(subfileSet={subfile42}))
    print("decodable? %r" % decodable)
    for subfile in decodeRstList:
        print(subfile)
    print("GT")
    print(subfile42)

    # decode csubfile
    print('='*20)
    decodable, decodeRstList = cache.decode(decodableSubfile1)
    print("decodable? %r" % decodable)
    for subfile in decodeRstList:
        print(subfile)
    print("GT")
    print(subfile21)

    print('-'*30)
    decodable, decodeRstList = cache.decode(decodableSubfile2)
    print("decodable? %r" % decodable)
    for subfile in decodeRstList:
        print(subfile)
    print("GT")
    print(subfile51)

    print('-'*30)
    decodable, decodeRstList = cache.decode(undecodableSubfile1)
    print("decodable? %r" % decodable)
    for subfile in decodeRstList:
        print(subfile)


    # decode bitSequence
    print('='*30)
    bitSequence = BitSequence()
    bitSequence.addCodedSubfile(decodableSubfile1)
    bitSequence.addCodedSubfile(decodableSubfile2)
    bitSequence.addCodedSubfile(undecodableSubfile1)

    decodable, decodeRstList = cache.decode(bitSequence)
    print("decodable? %r" % decodable)

    for subfile in decodeRstList:
        print(subfile)
