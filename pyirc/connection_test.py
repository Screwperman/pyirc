# -*- coding: utf-8 -*-
#
# Tests for connection.py

import unittest
from pmock import *

import connection

# Test cases.
class TestServer(unittest.TestCase):
    def setUp(self):
        self.w = Mock()
        self.d = Mock()

        # Inject a fresh mock to replace the wireproto module
        connection.wireproto = self.w

        def dispatcher_ctor(host, port, ext):
            self.assertEquals(host, 'host')
            self.assertEquals(port, 1234)
            return self.d

        self.conn = connection.Server('host', 1234, 'nick', 'user',
                                      'foo', _conn_class=dispatcher_ctor)

    def tearDown(self):
        self.w.verify()
        self.d.verify()

    def testConnectionSequence(self):
        """Test that the Connection knows how to say hello to a server"""
        self.w.expects(once()).encode(eq('NICK'), eq('nick')).will(
            return_value(1))
        self.w.expects(once()).encode(
            eq('USER'), eq('user'), eq('0'), eq('*'), eq('foo')).will(
            return_value(2))

        self.d.expects(once()).output(eq(1))
        self.d.expects(once()).output(eq(2))

        # We simulate the connection event from the dispatcher ourselves.
        self.conn.handle_connect()


class Test_ConnectionDispatcher(unittest.TestCase):
    def setUp(self):
        # The following are things that asyncore will call on our
        # socket. Since we're going to drive the socket manually
        # without asyncore's help, we just return dummy values to
        # please it.
        self.sock = Mock()
        self.sock.expects(once()).fileno().will(return_value(1))
        self.sock.expects(once()).setblocking(eq(0))
        self.sock.expects(once()).getpeername()

        self.handler = Mock()
        self.handler.expects(once()).handle_connect()
        self.dispatcher = connection._ConnectionDispatcher(
            '', 0, self.handler, ext_sock=self.sock)
        # Asyncore would call this handler on a real connect, but we
        # need to simulate it.
        self.dispatcher.handle_connect()

    def tearDown(self):
        self.sock.verify()
        self.handler.verify()

    def _sock_read(self, data):
        self.sock.expects(once()).recv(eq(8192)).will(return_value(data))

    def _sock_write(self, expected_data, amount_written):
        self.sock.expects(once()).send(eq(expected_data)).will(
            return_value(amount_written))

    def _handle_command(self, cmd):
        self.handler.expects(once()).handle_command(eq(cmd))

    def testDispatcherReadsMessages(self):
        """Test that the dispatcher properly handles incoming data"""
        self._sock_read('a\r\n')
        self._handle_command('a')
        self.dispatcher.handle_read()

        self._sock_read('bc\r\n')
        self._handle_command('bc')
        self.dispatcher.handle_read()

        # Fragmented packet. Confusingly, pmock requires us to set
        # expectations in reverse order for them to be found correctly.
        self._sock_read('\nef\r\n')
        self._sock_read('cd\r')
        self._sock_read('ab')
        self._handle_command('ef')
        self._handle_command('abcd')
        self.dispatcher.handle_read()
        self.dispatcher.handle_read()
        self.dispatcher.handle_read()

    def testDispatcherWritesOutput(self):
        """Test that the dispatcher properly handles outgoing data"""
        # Again with the confusing reverse expectations. Read the
        # expectation setup in reverse order.
        self._sock_write('h', 1)
        self._sock_write('efgh', 3)
        self._sock_write('defgh', 1)
        self._sock_write('abcdefgh', 3)
        self.dispatcher.output('abcdefgh')
        self.dispatcher.handle_write()
        self.dispatcher.handle_write()
        self.dispatcher.handle_write()
        self.dispatcher.handle_write()
