# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from BitSequence import BitSequence


class Server(object):
    """
    docstring for Server.

    Server class interacts directly with simulation users.
    Server is in charge of responding users' file requests
    """

    def __init__(self):
        super(Server, self).__init__()
