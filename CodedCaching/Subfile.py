#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import base64


class Subfile(object):
    """docstring for Subfile."""

    def __init__(self, fileId=None, subfileId=None, subfileSize=0, content=b'', inStr=''):
        super(Subfile, self).__init__()
        self._id = [None, None]
        self._subfileSize = 0
        self._content = b''

        if inStr:
            self.fromString(inStr)
        else:
            self.setId(fileId, subfileId)
            self.setSubfileSize(subfileSize)
            self.setContent(content)

    """
    variables set/get functions
    """
    def setId(self, fileId, subfileId):
        self._id = [fileId, subfileId]

    def getId(self):
        return self._id

    def getFileId(self):
        return self._id[0]

    def getSubfileId(self):
        return self._id[1]

    def setSubfileSize(self, subfileSize):
        self._subfileSize = max(0, subfileSize)

    def getSubfileSize(self):
        return self._subfileSize

    def setContent(self, content):
        self._content = content

    def getContent(self):
        return self._content

    """
    nice printout
    """
    def __str__(self):
        printout = '-'.join([str(self._id[0]), str(self._id[1])])
        printout += "  " + base64.b64encode(self._content).decode()
        return printout

    """
    serilization
    """
    def toString(self):
        d = {
            'id': self._id,
            'subfileSize': self._subfileSize,
            'content': base64.b64encode(self._content)
            }
        return json.dumps(d)

    def fromString(self, inStr):
        d = json.loads(inStr)
        self.setId(d['id'][0], d['id'][1])
        self.setSubfileSize(d['subfileSize'])
        self.setContent(base64.b64decode(d['content']))

if __name__ == '__main__':
    subfile = Subfile(fileId=1, subfileId=3, subfileSize=1)
    subfile.setContent(b'\x13\x13')
    print(subfile)

    subfileStr = subfile.toString()
    print(subfileStr)

    subfileFromStr = Subfile(inStr=subfileStr)
    print(subfileFromStr)
    print(subfileFromStr.toString())
