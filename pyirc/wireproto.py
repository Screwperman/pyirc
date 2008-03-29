# Protocol marshalling for IRC
#
# Handles both encoding and decoding of messages in the IRC line-based
# format.

class EncodeArgumentError(Exception):
    """Given arguments cannot be encoded as an IRC message."""

def _utf8ize(data):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    else:
        return data

def encode(command, *args):
    command = command.upper()
    if len(args) == 0:
        return '%s\r\n' % command
    else:
        args = [_utf8ize(x) for x in args]
        for arg in args[:-1]:
            if ' ' in arg:
                raise EncodeArgumentError
        return '%s %s :%s\r\n' % (command.upper(),
                                  ' '.join(args[:-1]),
                                  args[-1])

class Message(object):
    hostmask = None
    nick = None
    user = None
    host = None

    command = None
    args = None
    colon_arg = False

    def __init__(self, message):
        # Process the message prefix
        if message.startswith(':'):
            hostmask, message = message.split(None, 1)
            hostmask = hostmask[1:]
            self.hostmask = hostmask
            if '!' in hostmask:
                self.nick, hostmask = hostmask.split('!', 1)
            if '@' in hostmask:
                self.user, hostmask = hostmask.split('@', 1)
            self.host = hostmask

        # Locate the start of the final argument, if any, and split it
        # off. It is multispace and is annoying to process otherwise.
        message = message.split(' :', 1)
        self.colon_arg = (len(message) > 1)
        message[:1] = message[0].strip().split()
        self.command, self.args = message[0].upper(), message[1:]

def decode(message):
    return Message(message)
