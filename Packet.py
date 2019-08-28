#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json


class Packet(object):
    """
    This class defines the basic data structure of the back and forth traffic between users and the server.

    One packet object has two parts:
        _header: brief information about the packet, and the payload
        _payload: payload of course.
    """

    def __init__(self, inStr=""):
        super(Packet, self).__init__()
        self._header = {}
        self._payload = {}

        """
        dictionarize the fed in json string
        """
        if inStr:
            dict = json.loads(inStr)
            if 'header' in dict:
                self._header = dict['header']
            if 'payload' in dict:
                self._payload = dict['payload']

    def getHeader(self):
        return self._header

    def setHeader(self, header):
        self._header = header.copy()

    def getPayload(self):
        return self._payload

    def setPayload(self, payload):
        self._payload = payload.copy()


    def __dictPrint__(self, d, level=1):
        printout = ""
        for key in d:
            printout += '  '*level + key + ':\n'
            if isinstance(d[key], dict):
                printout += self.__dictPrint__(d[key], level+1)
            else:
                printout += '  '*(level+1) + d[key].__str__()
            printout += '\n'
        return printout

    def __str__(self):
        printout = """==============\n"""
        # print header
        printout += """Header:\n"""
        printout += self.__dictPrint__(self._header)
        printout += """\n"""

        # print payload
        printout += """Payload:\n"""
        printout += self.__dictPrint__(self._payload)
        printout += """\n"""

        return printout

    def toString(self):
        return json.dumps({'header': self._header, 'payload': self._payload})


if __name__ == '__main__':
    payload = {'data': {'x':1, 'y':2}, 'index': 192}
    header = {'Source': 'Alice', 'Destination': 'Bob'}

    txPkg = Packet()
    txPkg.setHeader(header)
    txPkg.setPayload(payload)

    rxStr = txPkg.toString()

    rxPkg = Packet(rxStr)
    print(rxPkg)
