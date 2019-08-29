#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Subfile import Subfile
import json

class CSubfile(object):
    """docstring for CSubfile (Coded Subfile)."""

    def __init__(self, id=None, subfileSet=set(), inStr=""):
        # super(Subfile, self).__init__()
        self._id = None
        self._subfileSet = {} # a 2-level dictionary. First level for fileId, second level for subfileId, value is subfile instance
        self._subfileCounter = 0

        if inStr:
            self.fromString(inStr)
        else:
            self.setId(id)
            self.setSubfileSet(subfileSet)


    """
    simple variable set/get
    """
    def setId(self, id):
        self._id = id

    def getId(self):
        return self._id

    def setSubfileSet(self, subfileSet):
        for subfile in subfileSet:
            self.addSubfile(subfile)

    def getSubfileSet(self):
        return self._subfileSet

    def getSubfileCounter(self):
        return self._subfileCounter

    """
    add/remove/check subfile
    """
    def addSubfile(self, subfile):
        fileId, subfileId = subfile.getFileId(), subfile.getSubfileId()
        if fileId in self._subfileSet: # this file show up before
            if subfileId in self._subfileSet[fileId]: # this subfile show up before. do nothing
                return
            else:
                self._subfileSet[fileId][subfileId] = subfile
        else:
            self._subfileSet[fileId] = {subfileId: subfile}
        self._subfileCounter += 1

    def delSubfile(self, fileId, subfileId):
        if self.hasSubfile(fileId, subfileId): # exists subfile, pop the subfile
            self._subfileSet[fileId].pop(subfileId)
            if not self._subfileSet[fileId]: # an empty dict, then pop this file
                self._subfileSet.pop(fileId)
            self._subfileCounter -= 1

    def hasSubfile(self, fileId, subfileId):
        if fileId in self._subfileSet:
            if subfileId in self._subfileSet[fileId]: # exists subfile
                return True
        return False

    """
    nice printout
    """
    def __str__(self):
        printout = str(self._id)
        printout += ': '

        subfileStrList = []
        for fileId in self._subfileSet:
            for subfileId in self._subfileSet[fileId]:
                subfileStrList.append(self._subfileSet[fileId][subfileId].__str__())
        printout += ', '.join(subfileStrList)

        return printout

    """
    serilization
    """
    def toString(self):
        d = {'id': self._id, 'subfile': []}

        for fileId in self._subfileSet:
            for subfileId in self._subfileSet[fileId]:
                d['subfile'].append(self._subfileSet[fileId][subfileId].toString())

        return json.dumps(d)

    def fromString(self, inStr):
        d = json.loads(inStr)
        self._id = d['id']
        self._subfileSet = {}
        for subfileStr in d['subfile']:
            self.addSubfile(Subfile(inStr=subfileStr))


if __name__ == '__main__':
    id = 20
    subfile11 = Subfile(fileId=1, subfileId=1)
    subfile21 = Subfile(fileId=2, subfileId=1)
    subfile31 = Subfile(fileId=3, subfileId=1)
    subfile42 = Subfile(fileId=4, subfileId=2)
    subfileSet = {subfile11, subfile21, subfile31, subfile42}
    codedSubfile = CSubfile(id=id, subfileSet=subfileSet)

    print(codedSubfile)

    codedSubfileStr = codedSubfile.toString()
    print(codedSubfileStr)

    codedSubfileFromStr = CSubfile(inStr=codedSubfileStr)
    codedSubfileFromStr.delSubfile(1, 1)
    print(codedSubfileFromStr)
    print(codedSubfileFromStr.getSubfileCounter())
