# -*- coding: utf-8 -*-
#
# Tests for connection.py

import unittest
from pmock import *

import connection

# Test cases.
class TestConnection(unittest.TestCase):
    def setUp(self):
        self.w = Mock()
        self.d = Mock()

        # Inject a fresh mock to replace the wireproto module
        connection.wireproto = self.w

        def dispatcher_ctor(host, port, ext):
            self.assertEquals(host, 'host')
            self.assertEquals(port, 1234)
            return self.d

        self.conn = connection.Connection('host', 1234, 'nick', 'user',
                                          'foo', _conn_class=dispatcher_ctor)

    def tearDown(self):
        self.w.verify()
        self.d.verify()

    def testConnectionSequence(self):
        """Test that the Connection knows how to say hello to a server."""
        self.w.expects(once()).encode(eq('NICK'), eq('nick')).will(
            return_value(1))
        self.w.expects(once()).encode(
            eq('USER'), eq('user'), eq('0'), eq('*'), eq('foo')).will(
            return_value(2))

        self.d.expects(once()).output(eq(1))
        self.d.expects(once()).output(eq(2))

        # We simulate the connection event from the dispatcher ourselves.
        self.conn.handle_connect()
