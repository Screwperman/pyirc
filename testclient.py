#!/usr/bin/env python

import asyncore
from pyirc.server import Server

s = Server('irc.rezosup.org', 6667, 'daive', 'bleh')
asyncore.loop()
