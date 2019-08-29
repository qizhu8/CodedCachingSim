# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import json

class Subfile(object):
    """docstring for Subfile."""

    def __init__(self, fileId=None, subfileId=None, subfileSize=0, inStr=''):
        super(Subfile, self).__init__()
        self._fileId = None
        self._subfileId = None
        self._subfileSize = 0

        if inStr:
            self.fromString(inStr)
        else:
            self._fileId = fileId
            self._subfileId = subfileId
            self._subfileSize = subfileSize

    """
    variables set/get functions
    """
    def setFileId(self, fileId):
        self._fileId = fileId

    def getFileId(self):
        return self._fileId

    def setSubfileId(self, subfileId):
        self._subfileId = subfileId

    def getSubfileId(self):
        return self._subfileId

    def setSubfileSize(self, subfileSize):
        self._subfileSize = subfileSize

    def getSubfileSize(self):
        return self._subfileSize

    """
    nice printout
    """
    def __str__(self):
        return '-'.join([str(self._fileId), str(self._subfileId)])

    """
    serilization
    """
    def toString(self):
        return json.dumps({'fileId': self._fileId, 'subfileId': self._subfileId, 'subfileSize': self._subfileSize})

    def fromString(self, inStr):
        d = json.loads(inStr)
        self._fileId = d['fileId']
        self._subfileId = d['subfileId']
        self._subfileSize = d['subfileSize']

if __name__ == '__main__':
    subfile = Subfile(fileId=1, subfileId=3, subfileSize=1)
    print(subfile)

    subfileStr = subfile.toString()
    print(subfileStr)

    subfileFromStr = Subfile(inStr=subfileStr)
    print(subfileFromStr)
