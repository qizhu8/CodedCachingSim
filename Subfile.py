# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import json

class Subfile(object):
    """docstring for Subfile."""

    def __init__(self, fileId=None, subfileId=None, inStr=''):
        super(Subfile, self).__init__()

        if inStr:
            self.fromString(inStr)

        if fileId:
            self._fileId = fileId
        if subfileId:
            self._subfileId = subfileId

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

    """
    nice printout
    """
    def __str__(self):
        return '-'.join([str(self._fileId), str(self._subfileId)])

    """
    serilization
    """
    def toString(self):
        return json.dumps({'fileId': self._fileId, 'subfileId': self._subfileId})

    def fromString(self, inStr):
        d = json.loads(inStr)
        self._fileId = d['fileId']
        self._subfileId = d['subfileId']

if __name__ == '__main__':
    subfile = Subfile(fileId=1, subfileId=3)
    print(subfile)

    subfileStr = subfile.toString()
    print(subfileStr)

    subfileFromStr = Subfile(inStr=subfileStr)
    print(subfileFromStr)
