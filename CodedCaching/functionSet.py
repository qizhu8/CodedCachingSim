#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bytes array operator
"""
def XOR(a, b):
    # if not isinstance(a, bytes) or isinstance(b, bytes):
    # print(a.__class__.__name__, b.__class__.__name__)

    if a.__class__.__name__ in ['str']:
        a = [int(a[i]) for i in range(len(a))]
    if b.__class__.__name__ in ['str']:
        b = [int(b[i]) for i in range(len(b))]

    if a.__class__.__name__ not in ['bytes', 'bytearray', 'list'] or b.__class__.__name__ not in ['bytes', 'bytearray', 'list']:
        raise Exception('Input arrays are not bytes, they are %s and %s: %s and %s' %(a.__class__.__name__, b.__class__.__name__, a, b))
    if len(a) != len(b):
        raise Exception('Input arrays are of different length, %d and %d' %(len(a), len(b)))
    return bytes([a[i] ^ b[i] for i in range(len(a))])
