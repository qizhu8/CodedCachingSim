# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import json

from Subfile import Subfile
from CSubfile import CSubfile

class BitSequence(object):
    """
    docstring for BitSequence.

    BitSequence is sent by the server to users to respond users' file requests.
    """

    def __init__(self, codedSubfileDict={}, inStr=""):
        super(BitSequence, self).__init__()

        self._codedSubfileDict = {}
        self._codedSubfileCounter = 0

        if inStr:
            self.fromString(inStr)
        else:
            self.setCodedSubfileDict(codedSubfileDict)

    def setCodedSubfileDict(self, codedSubfileDict):
        for id in codedSubfileDict:
            self.addCodedSubfile(codedSubfileDict[id])


    def hasCodedSubfile(self, codedSubfileId):
        if codedSubfileId in self._codedSubfileDict:
            return True
        return False

    def addCodedSubfile(self, codedSubfile):
        codedSubfileId = codedSubfile.getId()
        if not self.hasCodedSubfile(codedSubfileId):
            self._codedSubfileDict[codedSubfileId] = codedSubfile
            self._codedSubfileCounter += 1
        else: # replace
            self._codedSubfileDict[codedSubfileId] = codedSubfile


    def delCodedSubfile(self, codedSubfileId):
        if self.hasCodedSubfile(codedSubfileId):
            self._codedSubfileDict.pop(codedSubfileId)
            self._codedSubfileCounter -= 1

    """
    nice printout
    """
    def __str__(self):
        printout = """"""
        for codedSubfileId in self._codedSubfileDict:
            printout += self._codedSubfileDict[codedSubfileId].__str__() + '\n'
        return printout

    """
    serilization
    """
    def toString(self):
        d = {id: self._codedSubfileDict[id].toString() for id in self._codedSubfileDict}
        return json.dumps(d)

    def fromString(self, inStr):
        d = json.loads(inStr)
        self._codedSubfileDict = {}
        for id in d:
            self._codedSubfileDict[id] = CSubfile(inStr=d[id])

    """
    example self setup
    """
    def exampleSelfSetup(self):
        subfile11 = Subfile(fileId=1, subfileId=1, subfileSize=1)
        subfile12 = Subfile(fileId=1, subfileId=2, subfileSize=1)
        subfile13 = Subfile(fileId=1, subfileId=3, subfileSize=1)
        subfile21 = Subfile(fileId=2, subfileId=1, subfileSize=1)
        subfile22 = Subfile(fileId=2, subfileId=2, subfileSize=1)
        subfile23 = Subfile(fileId=2, subfileId=3, subfileSize=1)
        subfile31 = Subfile(fileId=3, subfileId=1, subfileSize=1)
        subfile32 = Subfile(fileId=3, subfileId=2, subfileSize=1)
        subfile33 = Subfile(fileId=3, subfileId=3, subfileSize=1)
        subfile41 = Subfile(fileId=4, subfileId=1, subfileSize=1)
        subfile42 = Subfile(fileId=4, subfileId=2, subfileSize=1)
        subfile43 = Subfile(fileId=4, subfileId=3, subfileSize=1)

        subfileSet1 = {subfile11, subfile21, subfile31, subfile41}
        subfileSet2 = {subfile12, subfile22, subfile32, subfile42}
        subfileSet3 = {subfile13, subfile23, subfile33, subfile43}

        codedSubfile1 = CSubfile(id=1, subfileSet=subfileSet1)
        codedSubfile2 = CSubfile(id=2, subfileSet=subfileSet2)
        codedSubfile3 = CSubfile(id=3, subfileSet=subfileSet3)

        self.addCodedSubfile(codedSubfile1)
        self.addCodedSubfile(codedSubfile2)
        self.addCodedSubfile(codedSubfile3)

if __name__=='__main__':
    subfile11 = Subfile(fileId=1, subfileId=1, subfileSize=1)
    subfile12 = Subfile(fileId=1, subfileId=2, subfileSize=1)
    subfile13 = Subfile(fileId=1, subfileId=3, subfileSize=1)
    subfile21 = Subfile(fileId=2, subfileId=1, subfileSize=1)
    subfile22 = Subfile(fileId=2, subfileId=2, subfileSize=1)
    subfile23 = Subfile(fileId=2, subfileId=3, subfileSize=1)
    subfile31 = Subfile(fileId=3, subfileId=1, subfileSize=1)
    subfile32 = Subfile(fileId=3, subfileId=2, subfileSize=1)
    subfile33 = Subfile(fileId=3, subfileId=3, subfileSize=1)
    subfile41 = Subfile(fileId=4, subfileId=1, subfileSize=1)
    subfile42 = Subfile(fileId=4, subfileId=2, subfileSize=1)
    subfile43 = Subfile(fileId=4, subfileId=3, subfileSize=1)

    subfileSet1 = {subfile11, subfile21, subfile31, subfile41}
    subfileSet2 = {subfile12, subfile22, subfile32, subfile42}
    subfileSet3 = {subfile13, subfile23, subfile33, subfile43}

    codedSubfile1 = CSubfile(id=1, subfileSet=subfileSet1)
    codedSubfile2 = CSubfile(id=2, subfileSet=subfileSet2)
    codedSubfile3 = CSubfile(id=3, subfileSet=subfileSet3)

    bitSequence = BitSequence()
    bitSequence.addCodedSubfile(codedSubfile1)
    bitSequence.addCodedSubfile(codedSubfile2)
    bitSequence.addCodedSubfile(codedSubfile3)

    print(bitSequence)

    bitSequenceStr = bitSequence.toString()

    bitSequenceFromStr = BitSequence(inStr=bitSequenceStr)

    print(bitSequenceFromStr)
