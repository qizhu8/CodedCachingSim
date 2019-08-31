# -*- coding: utf-8 -*-
#!/usr/bin/env python3

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
        return '-'.join([str(self._id[0]), str(self._id[1])])

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

    """
    bytes array operator
    """
    def XOR(a, b):
        # if not isinstance(a, bytes) or isinstance(b, bytes):
        if a.__class__.__name__ not in ['bytes', 'bytearray'] or b.__class__.__name__ not in ['bytes', 'bytearray']:
            raise Exception('Input arrays are not bytes, they are %s and %s' %(a.__class__.__name__, b.__class__.__name__))
        if len(a) != len(b):
            raise Exception('Input arrays are of different length, %d and %d' %(len(a), len(b)))
        return bytes([a[i] ^ b[i] for i in range(len(a))])

if __name__ == '__main__':
    subfile = Subfile(fileId=1, subfileId=3, subfileSize=1)
    subfile.setContent(b'\x13\x13')
    print(subfile)

    subfileStr = subfile.toString()
    print(subfileStr)

    subfileFromStr = Subfile(inStr=subfileStr)
    print(subfileFromStr)
    print(subfileFromStr.toString())
