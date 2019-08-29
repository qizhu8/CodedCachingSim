#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Packet import Packet

class CCPacket(Packet):
    """
    CCPacket heritages class Packet. More details about the header, payload used by Coded Caching Network are defined here.
    """
    HEADER_KEY = {'id', 'source', 'destination'}
    PAYLOAD_KEY = {'content'}
    def __init__(self, id=None, source=None, destination=None, content=None, inStr=""):
        super(CCPacket, self).__init__(inStr=inStr)
        # self._header = {}
        # self._payload = {}

        for key in HEADER_KEY:
            if key not in self._header:
                self._header[key] = None
        for key in PAYLOAD_KEY:
            if key not in self._payload:
                self._payload[key] = None

        if id:
            self._header['id'] = id
        if source:
            self._header['source'] = source
        if destination:
            self._header['destination'] = destination
        if content:
            self._payload['content'] = content

    """
    variables set/get functions
    """
    # _header.id
    def setId(self, id):
        self._header['id'] = id

    def getId(self):
        return self._header['id']

    # _header.source
    def setSource(self, source):
        self._header['source'] = source

    def getSource(self):
        return self._header['source']

    # _header.destination
    def setDestination(self, destination):
        self._header['destination'] = destination

    def getDestination(self):
        return self._header['destination']

    # _payload.content
    def setContent(self, content):
        self._header['content'] = content

    def gettContent(self):
        return self._header['content']
