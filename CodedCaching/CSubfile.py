#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Subfile import Subfile
import json
import base64

class CSubfile(object):
    """docstring for CSubfile (Coded Subfile)."""

    def __init__(self, id=None, subfileSet=set(), inStr=""):
        # super(Subfile, self).__init__()
        self._id = None
        self._subfileSet = {} # a 2-level dictionary. First level for fileId, second level for subfileId, value is subfile instance
        self._subfileSize = 0
        self._subfileCounter = 0
        self._subfileBrief = []
        self._subfileBriefUpToDate = True # True: matches _codedSubfileDict
        self._subfileContent = b''

        if inStr:
            self.fromString(inStr)
        else:
            self.setId(id)
            self.setSubfileSet(subfileSet)


    """
    simple variable set/get
    """
    def clearSubfile(self):
        self._subfileBriefUpToDate = True
        self._subfileSet = {}
        self._subfileCounter = 0
        self._subfileContent = b''

    def setId(self, id):
        self._id = id

    def getId(self):
        return self._id

    def setSubfileSet(self, subfileSet):
        self.clearSubfile()
        for subfile in subfileSet:
            self.addSubfile(subfile)

    def getSubfileSet(self):
        return self._subfileSet

    def getSubfileContent(self):
        return self._subfileContent

    def getSubfileCounter(self):
        return self._subfileCounter

    def getSubfileSize(self):
        return self._subfileSize

    def getSubfileBrief(self):
        if not self._subfileBriefUpToDate:
            self._updateSubfileBrief()
        return self._subfileBrief

    """
    add/remove/check subfile
    """
    def addSubfile(self, subfile):
        fileId, subfileId = subfile.getFileId(), subfile.getSubfileId()
        subfileSize = subfile.getSubfileSize()

        if self._subfileCounter == 0: # no file in current subfile
            self._subfileSize = subfileSize
            self._subfileContent = subfile.getContent()
            self._subfileBrief = [[fileId, subfileId]]
            self._subfileCounter = 1

        else:
            if self._subfileSize != subfileSize:
                print("New subfile has a size which is not compatable to the current subfiles")
                return

            if fileId in self._subfileSet: # this file show up before, continue check subfile id
                if subfileId in self._subfileSet[fileId]: # this subfile show up before. do nothing
                    return
                else: # same file id but different subfile id
                    self._subfileSet[fileId].add(subfileId)
            else:   # this file hasn't shown up before
                self._subfileSet[fileId] = {subfileId}

            self._subfileContent = Subfile.XOR(self._subfileContent, subfile.getContent())
            self._subfileCounter += 1
            if self._subfileBriefUpToDate:
                self._subfileBrief.append([fileId, subfileId])



    def delSubfile(self, subfile):
        fileId, subfileId = subfile.getFileId(), subfile.getSubfileId()
        if self.hasSubfile(fileId, subfileId): # exists subfile, pop the subfile
            self._subfileBriefUpToDate = False
            self._subfileContent = Subfile.XOR(self._subfileContent, subfile.getContent())
            self._subfileSet[fileId].remove(subfileId)
            if not self._subfileSet[fileId]: # an empty dict, then pop this file
                self._subfileSet.pop(fileId)
            self._subfileCounter -= 1

        if self._subfileCounter <= 0:
            self._subfileCounter = 0
            self._subfileSize = 0

    def hasSubfile(self, fileId, subfileId):
        if fileId in self._subfileSet:
            if subfileId in self._subfileSet[fileId]: # exists subfile
                return True
        return False

    def _updateSubfileBrief(self):
        if not self._subfileBriefUpToDate:
            self._subfileBrief = []
            for fileId in self._subfileSet:
                for subfileId in self._subfileSet[fileId]:
                    self._subfileBrief.append([fileId, subfileId])
        self._subfileBriefUpToDate = True

    """
    nice printout
    """
    def __str__(self):
        printout = "id:{id} size={size}, counter={counter}: ".format(id=self._id, size=self._subfileSize, counter=self._subfileCounter)


        printout += self.getSubfileBrief().__str__()

        return printout

    def printSubfileContent(self):
        printout = """base64: {base64}\ninteger: {integer}""".format(
                base64=base64.b64encode(self._subfileContent).decode(),
                integer=int.from_bytes(self._subfileContent, byteorder='big')
                )
        print(printout)

    """
    serilization
    """
    def toString(self):
        d = {
            'id': self._id,
            'size': self._subfileSize,
            'subfile': self.getSubfileBrief(),
            'content': base64.b64encode(self._subfileContent).decode()
            }

        # for fileId in self._subfileSet:
        #     for subfileId in self._subfileSet[fileId]:
        #         d['subfile'].append(self._subfileSet[fileId][subfileId].toString())
        # print(d)
        return json.dumps(d)

    def fromString(self, inStr):
        d = json.loads(inStr)
        self._id = d['id']
        self.clearSubfile()
        self._subfileContent = base64.b64decode(d['content'])
        self._subfileBrief = d['subfile']
        self._subfileCounter = len(self._subfileBrief)
        self._subfileSize = d['size']
        for fileId, subfileId in self._subfileBrief:
            if fileId in self._subfileSet:
                self._subfileSet[fileId].add(subfileId)
            else:
                self._subfileSet[fileId] = {subfileId}

if __name__ == '__main__':
    id = 20
    subfile11 = Subfile(fileId=1, subfileId=1, subfileSize=1, content=b'\x11')
    subfile21 = Subfile(fileId=2, subfileId=1, subfileSize=1, content=b'\x21')
    subfile31 = Subfile(fileId=3, subfileId=1, subfileSize=1, content=b'\x31')
    subfile42 = Subfile(fileId=4, subfileId=2, subfileSize=1, content=b'\x42')
    # subfileSet = {subfile11, subfile21, subfile31, subfile42}
    subfileSet = {subfile11, subfile42}
    codedSubfile = CSubfile(id=id, subfileSet=subfileSet)
    print(codedSubfile)
    codedSubfile.printSubfileContent()

    codedSubfileStr = codedSubfile.toString()
    print(codedSubfileStr)

    codedSubfileFromStr = CSubfile(inStr=codedSubfileStr)
    codedSubfileFromStr.delSubfile(subfile11)
    print(codedSubfileFromStr.toString())
    codedSubfileFromStr.printSubfileContent()

    # print(codedSubfileFromStr.getSubfileBrief())

    # print("-"*20)
    # codedSubfileCopy = codedSubfile.copy()
    # print(codedSubfileCopy)
