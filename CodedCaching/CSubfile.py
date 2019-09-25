#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import functionSet as fcs
from Subfile import Subfile
import json
import base64
import hashlib

class CSubfile(object):
    """docstring for CSubfile (Coded Subfile)."""

    def __init__(self, subfileSet=set(), inStr=""):
        # super(Subfile, self).__init__()
        self._id = None # id is computed by sha256(brief)
        self._subfileSet = {} # a 2-level dictionary. First level for fileId, second level for subfileId, value is subfile instance
        self._subfileSize = 0
        self._subfileCounter = 0
        self._subfileBrief = []
        self._subfileBriefUpToDate = False # True: matches _codedSubfileDict
        self._idUpToDate = False
        self._subfileContent = b''

        if inStr:
            self.fromString(inStr)
        else:
            self.setSubfileSet(subfileSet)


    """
    simple variable set/get
    """
    def clearSubfile(self):
        self._subfileBriefUpToDate = False
        self._idUpToDate = False
        self._subfileSet = {}
        self._subfileCounter = 0
        self._subfileContent = b''

    # def setId(self, id):
    #     self._id = id

    def getId(self):
        if not self._idUpToDate:
            self._updateId()
        return self._id

    def setSubfileSet(self, subfileSet):
        self.clearSubfile()
        for subfile in subfileSet:
            self.addSubfile(subfile)
        self._updateSubfileBrief()
        self._updateId()
        self._subfileBriefUpToDate = True
        self._idUpToDate = True

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

    def copy(self):
        # self._id = None # id is computed by sha256(brief)
        # self._subfileSet = {} # a 2-level dictionary. First level for fileId, second level for subfileId, value is subfile instance
        # self._subfileSize = 0
        # self._subfileCounter = 0
        # self._subfileBrief = []
        # self._subfileBriefUpToDate = False # True: matches _codedSubfileDict
        # self._idUpToDate = False
        # self._subfileContent = b''

        newCSubfile = CSubfile()
        newCSubfile._id = self._id
        newCSubfile._subfileSet = self._subfileSet.copy()
        newCSubfile._subfileSize = self._subfileSize
        newCSubfile._subfileCounter = self._subfileCounter
        newCSubfile._subfileBrief = self._subfileBrief.copy()
        newCSubfile._subfileBriefUpToDate = self._subfileBriefUpToDate
        newCSubfile._idUpToDate = self._idUpToDate
        newCSubfile._subfileContent = self._subfileContent

        return newCSubfile


    """
    add/remove/check subfile
    """
    def addSubfile(self, subfile):
        fileId, subfileId = subfile.getFileId(), subfile.getSubfileId()
        subfileSize = subfile.getSubfileSize()

        # print(self._subfileCounter)
        if self._subfileCounter == 0: # no file in current subfile
            self._idUpToDate = False

            self._subfileSize = subfileSize
            self._subfileContent = subfile.getContent()
            self._subfileBrief = [[fileId, subfileId]]
            self._subfileSet[fileId] = {subfileId}
            self._subfileCounter = 1

        else:
            if self._subfileSize != subfileSize:
                print("New subfile has a size which is not compatable to the current subfiles")
                return

            if fileId in self._subfileSet: # this file show up before, continue check subfile id
                if subfileId in self._subfileSet[fileId]: # this subfile show up before. do nothing
                    return
                else: # same file id but different subfile id
                    self._idUpToDate = False

                    self._subfileSet[fileId].add(subfileId)
            else:   # this file hasn't shown up before
                self._idUpToDate = False

                self._subfileSet[fileId] = {subfileId}

            self._subfileContent = fcs.XOR(self._subfileContent, subfile.getContent())
            self._subfileCounter += 1
            if self._subfileBriefUpToDate:
                self._subfileBrief.append([fileId, subfileId])

            # print(self._subfileCounter)


    def delSubfile(self, subfile):

        fileId, subfileId = subfile.getFileId(), subfile.getSubfileId()
        if self.hasSubfile(fileId, subfileId): # exists subfile, pop the subfile
            self._idUpToDate = False
            self._subfileBriefUpToDate = False

            self._subfileContent = fcs.XOR(self._subfileContent, subfile.getContent())
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

    """
    XOR csubfile
    """
    def XORSubfile(self, csubfile):
        if isinstance(csubfile, Subfile):
            csubfile = CSubfile(subfileSet={csubfile})

        csubfileBrief = csubfile.getSubfileBrief()
        # update the _subfileSet
        for fileId, subfileId in csubfileBrief:
            if self.hasSubfile(fileId, subfileId):
                # after XORing, this subfile will be cancelled out
                self._idUpToDate = False
                self._subfileBriefUpToDate = False

                self._subfileSet[fileId].remove(subfileId)
                if not self._subfileSet[fileId]: # an empty dict, then pop this file
                    self._subfileSet.pop(fileId)
                self._subfileCounter -= 1
            else:
                # after XORing, this subfile will be inserted
                self._idUpToDate = False
                self._subfileBriefUpToDate = False

                if fileId in self._subfileSet:
                    self._subfileSet[fileId].add(subfileId)
                else:
                    self._subfileSet[fileId] = {subfileId}

                self._subfileCounter += 1

        # update the content
        self._subfileContent = fcs.XOR(self._subfileContent, csubfile.getSubfileContent())



    def _updateSubfileBrief(self):
        if not self._subfileBriefUpToDate:
            self._subfileBrief = []
            for fileId in self._subfileSet:
                for subfileId in self._subfileSet[fileId]:
                    self._subfileBrief.append([fileId, subfileId])
        self._subfileBriefUpToDate = True
        self._updateId()

    def _updateId(self):
        if not self._subfileBriefUpToDate:
            self._updateSubfileBrief()
        csubfileBrief = []
        for fileId, subfileId in self._subfileBrief:
            csubfileBrief.append(str(fileId) + '-' + str(subfileId))
        csubfileBrief.sort()
        csubfileBriefStr = "|".join(csubfileBrief)
        m = hashlib.sha256()
        m.update(csubfileBriefStr.encode())
        self._id = m.hexdigest()
        self._idUpToDate = True

    def downgradeToSubfile(self):
        if self.getSubfileCounter() == 1:
            brief = self.getSubfileBrief()
            return Subfile(
                fileId=brief[0][0],
                subfileId=brief[0][1],
                subfileSize=self.getSubfileSize(),
                content=self.getSubfileContent())
        else:
            return None

    """
    nice printout
    """
    def __str__(self):

        printout = "id:{id} \nsize={size}, counter={counter}\n".format(
            id=self.getId(),
            size=self._subfileSize,
            counter=self._subfileCounter)


        printout += "brief:" + self.getSubfileBrief().__str__()

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
            'id': self.getId(),
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
    subfile11 = Subfile(fileId=1, subfileId=1, subfileSize=1, content=b'\x11')
    subfile21 = Subfile(fileId=2, subfileId=1, subfileSize=1, content=b'\x21')
    subfile31 = Subfile(fileId=3, subfileId=1, subfileSize=1, content=b'\x31')
    subfile42 = Subfile(fileId=4, subfileId=2, subfileSize=1, content=b'\x42')
    codedSubfile1 = CSubfile(subfileSet={subfile11, subfile21, subfile31, subfile42})
    codedSubfile2 = CSubfile(subfileSet={           subfile21, subfile31, subfile42})
    uncodedSubfile = CSubfile(subfileSet={subfile11})

    codedSubfile1.XORSubfile(codedSubfile2)
    print(codedSubfile1)
    print(uncodedSubfile)
