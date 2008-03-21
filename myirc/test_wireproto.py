# Unit tests for wireproto

import unittest
from myirc import wireproto

class TestWireproto(unittest.TestCase):
    def testEncoding(self):
        self.assertEquals(
            wireproto.encode('notice'), 'NOTICE\r\n')
        # Single argument commands end up having two spaces between
        # command and arguments. According to the IRC protocol, this is
        # fine, so it's just a little oddity of our encoder.
        self.assertEquals(
            wireproto.encode('join', '#bleh'), 'JOIN  :#bleh\r\n')
        self.assertEquals(
            wireproto.encode('privmsg', 'arg1', 'arg2'),
            'PRIVMSG arg1 :arg2\r\n')
        self.assertEquals(
            wireproto.encode('privmsg', 'arg1', 'arg2 with spaces'),
            'PRIVMSG arg1 :arg2 with spaces\r\n')
        self.assertRaises(wireproto.EncodeArgumentError, wireproto.encode,
                          'privmsg', 'arg1 with spaces', 'arg2')

    def checkMessage(self, message, hostmask=None, nick=None, user=None,
                     host=None, command=None, args=None):
        self.assert_(isinstance(message, wireproto.Message))
        self.assertEquals(message.hostmask, hostmask)
        self.assertEquals(message.nick, nick)
        self.assertEquals(message.user, user)
        self.assertEquals(message.host, host)
        self.assertEquals(message.command, command)
        self.assertEquals(message.args, args)

    def testDecoding(self):
        self.checkMessage(
            wireproto.decode('PRIVMSG foo bar'),
            command='PRIVMSG', args=['foo', 'bar'])
        self.checkMessage(
            wireproto.decode('PRIVMSG foo :bar baz'),
            command='PRIVMSG', args=['foo', 'bar baz'])
        self.checkMessage(
            wireproto.decode(':irc.server.com 353 foo :bar baz'),
            hostmask='irc.server.com', host='irc.server.com',
            command='353', args=['foo', 'bar baz'])
        self.checkMessage(
            wireproto.decode(':Dave`!dave@natulte.net PRIVMSG #foo :Hi !'),
            hostmask='Dave`!dave@natulte.net', nick='Dave`', user='dave',
            host='natulte.net', command='PRIVMSG', args=['#foo', 'Hi !'])


if __name__ == '__main__':
    unittest.main()
