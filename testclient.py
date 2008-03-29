#!/usr/bin/env python

import sys
import asyncore
from pyirc.server import Server

if len(sys.argv) == 3:
    host, port = sys.argv[1], int(sys.argv[2])
else:
    host, port = 'irc.rezosup.org', 6667

s = Server(host, port, 'daive', 'bleh')
asyncore.loop()
