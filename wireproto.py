# Protocol marshalling for IRC
#
# Handles both encoding and decoding of messages in the IRC line-based
# format.

class EncodeArgumentError(Exception):
    """Given arguments cannot be encoded as an IRC message."""

def encode(command, *args):
    command = command.upper()
    if len(args) == 0:
        return '%s\r\n' % command
    else:
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
        message[:1] = message[0].strip().split()
        self.command, self.args = message[0], message[1:]

def decode(message):
    return Message(message)
