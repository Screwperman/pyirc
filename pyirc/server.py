# -*- coding: utf-8 -*-
#
# Handles a connection to an IRC server.

import socket
import asyncore

import wireproto

class _ConnectionDispatcher(asyncore.dispatcher):
    """Thin wrapper around asyncore.dispatcher.

    Handles connection and buffered writing, and delegates other
    events to the actual Connection class. This is to get a clean
    class namespace, because asyncore defines a fair amount of methods
    and data we risk stepping on.
    """
    def __init__(self, host, port, ext_handler, ext_sock=None):
        asyncore.dispatcher.__init__(self, sock=ext_sock)
        self.send_buffer = []
        self.recv_buffer = []
        self.ext_handler = ext_handler
        if not ext_sock:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect((host, port))

    def output(self, data):
        self.send_buffer.append(data)

    def handle_connect(self):
        self.ext_handler.handle_connect()

    def handle_close(self):
        self.close()
        self.ext_handler.handle_close()

    def handle_read(self):
        data = self.recv(8192)

        # Corner case: the line delimiter may have been split across
        # packet boundaries. If so, we fuse all received data before
        # attempting a split.
        if len(self.recv_buffer) > 1 and data.startswith('\n'):
            self.recv_buffer.append(data)
            data = ''.join(self.recv_buffer)
            self.recv_buffer = []

        # Try to split the incoming data. If it worked, we have at
        # least one full packet.
        lines = data.split('\r\n')
        if len(lines) == 1:
            self.recv_buffer.append(data)
            return

        self.recv_buffer.append(lines[0])
        self.ext_handler.handle_command(''.join(self.recv_buffer))
        for line in lines[1:-1]:
            self.ext_handler.handle_command(line)
        self.recv_buffer = [lines[-1]]

    def writable(self):
        return (len(self.send_buffer) > 0)

    def handle_write(self):
        data = ''.join(self.send_buffer)
        sent = self.send(data)
        data = data[sent:]
        if data:
            self.send_buffer = [data]
        else:
            self.send_buffer = []


class Server(object):
    def __init__(self, host, port, nick, user, realname='nobody',
                 _conn_class=_ConnectionDispatcher):
        self._conn = _conn_class(host, port, self)
        self.nick = nick
        self.user = user
        self.realname = realname

    def handle_connect(self):
        self._conn.output(wireproto.encode('NICK', self.nick))
        self._conn.output(wireproto.encode(
            'USER', self.user, '0', '*', self.realname))

    def handle_command(self, command):
        cmd = wireproto.decode(command)
        print cmd.command, cmd.args
        if cmd.command == 'MODE':
            self._conn.output(wireproto.encode('QUIT'))

    def handle_close(self):
        print "Done!"
