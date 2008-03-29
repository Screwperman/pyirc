# -*- coding: utf-8 -*-
#
# Class defining the capabilities of an IRC server, as given by the
# RPL_ISUPPORT message, numeric 005.

def _mkproperty(capname, withdel=False):
    """Decorator function to register a property.

    The contained function should return locals(), after having
    defined doc, fget, fset and fdel.
    """
    def dec(func):
        d = func()
        if not isinstance(d, dict):
            raise RuntimeError('A decorated property is missing '
                               'return locals() !')
        private_var = '_%s' % capname.lower()
        if 'fget' not in d:
            def default_fget(self):
                return getattr(self, private_var)
            d['fget'] = default_fget
        if withdel:
            def default_fdel(self):
                delattr(self, private_var)
            d['fdel'] = default_fdel
        return property(**d)
    return dec

##
# Exception classes
##
class CapabilityError(Exception):
    """Capability error"""

class CapabilityValueError(CapabilityError):
    """Invalid capability value"""
    def __init__(self, cap, value):
        Exception.__init__(self, 'Invalid value "%s" for %s' % (value, cap))

class CapabilityLogicError(CapabilityError):
    """Capability provided makes no sense given existing caps."""

##
# Constants
##

# Enum values for CHANMODE mode kinds
CHANMODE_LIST = 0
CHANMODE_PARAM_ALWAYS = 1
CHANMODE_PARAM_ADDONLY = 2
CHANMODE_NO_PARAM = 3


class ServerCapabilities(object):
    _casemapping = 'ascii' # TODO(dave): Should be rfc1459, see below.
    @_mkproperty('CASEMAPPING')
    def casemapping():
        def fset(self, v):
            if v not in ('ascii', 'rfc1459', 'strict-rfc1459'):
                raise CapabilityValueError('CASEMAPPING', v)
            # TODO(dave): Support other casemappings, if they are
            # still around in the wild.
            if v != 'ascii':
                raise NotImplementedError(
                    'Only CASEMAPPING=ascii is supported')
            self._casemapping = v
        def fdel(self):
            del self._casemapping
        return locals()

    _chanlimit = None
    @_mkproperty('CHANLIMIT')
    def chanlimit():
        def fset(self, v):
            v = v or ''
            try:
                limits = [l.strip().split(':') for l in v.strip().split(',')]
                limits = dict((frozenset(pfx), int(num)) for pfx,num in limits)
                # Empty CHANLIMIT is forbidden
                if len(limits) == 0:
                    raise ValueError
            except ValueError:
                raise CapabilityValueError('CHANLIMIT', v)

            # All specified prefixes have to have been defined by
            # CHANTYPES
            chantypes = self.chantypes
            for prefixes in limits.keys():
                if not prefixes.issubset(chantypes):
                    raise CapabilityLogicError(
                        'Channel prefix(es) %s used in CHANLIMIT, but not '
                        'defined in CHANTYPES %s' % (prefixes, chantypes))

            self._chanlimit = limits
        return locals()

    _chanmodes = None
    @_mkproperty('CHANMODES')
    def chanmodes():
        def fset(self, v):
            v = v.strip().split(',')[:4]
            if not v or len(v) != 4:
                raise CapabilityValueError('CHANMODES', v)
            # TODO(dave): Check that no flags from PREFIXES are here.
            # TODO(dave): Check for duplicates among fields.

            oldmodes = self._chanmodes
            self._chanmodes = dict(enumerate(frozenset(iter(x)) for x in v))

            # Check for broken dependent capabilities
            try:
                if self.excepts:
                    self.excepts = self.excepts
                if self.invex:
                    self.invex = self.invex
                if self.maxlist:
                    self.maxlist = ','.join('%s:%d' % (''.join(k), v)
                                            for k,v in self.maxlist.iteritems())
                if self.prefix:
                    prefix_modes = set(self.prefix.keys())
                    for modes in self._chanmodes.values():
                        if prefix_modes.intersection(modes):
                            raise CapabilityLogicError(
                                'New CHANMODES definition overlaps modes '
                                'defined by PREFIX')
            except CapabilityLogicError:
                self._chanmodes = oldmodes
                raise

        return locals()

    _channellen = 200
    @_mkproperty('CHANNELLEN', withdel=True)
    def channellen():
        def fset(self, v):
            v = v or None
            if v is not None:
                try:
                    v = int(v)
                except ValueError:
                    raise CapabilityValueError('CHANNELLEN', v)
            self._channellen = v
        return locals()

    _chantypes = frozenset(('#', '&'))
    @_mkproperty('CHANTYPES', withdel=True)
    def chantypes():
        def fset(self, v):
            v = v or ''
            types = frozenset(iter(v))

            # CHANTYPES validates the content of CHANLIMIT, so we need
            # to check that the values still make sense.
            chanlimit = self.chanlimit
            if chanlimit:
                for prefixes in chanlimit.keys():
                    if not prefixes.issubset(types):
                        raise CapabilityLogicError(
                            'Channel types redefined to "%s", but CHANLIMIT '
                            'specifies limits for prefix(es) "%s"' % (types,
                                                                      prefixes))
            self._chantypes = types
        return locals()

    _excepts = None
    @_mkproperty('EXCEPTS', withdel=True)
    def excepts():
        def fset(self, v):
            v = v or 'e'
            if len(v) != 1:
                raise CapabilityValueError('EXCEPTS', v)

            # The except flag must be defined as an A type chanmode.
            chanmodes = self.chanmodes
            if chanmodes and v not in chanmodes[CHANMODE_LIST]:
                raise CapabilityLogicError(
                    'Channel flag "%s" defined for EXCEPTS, but not an A type '
                    'channel flag according to CHANMODES' % v)
            self._excepts = v
        return locals()

    # TODO(dave): Possibly implement IDCHAN, if anyone comes across an
    # ircd that actually supports !chans.

    _invex = None
    @_mkproperty('INVEX', withdel=True)
    def invex():
        def fset(self, v):
            v = v or 'I'
            if len(v) != 1:
                raise CapabilityValueError('INVEX', v)

            # The invex flag must be defined as an A type chanmode.
            chanmodes = self.chanmodes
            if chanmodes and v not in chanmodes[CHANMODE_LIST]:
                raise CapabilityLogicError(
                    'Channel flag "%s" defined for INVEX, but not an A type '
                    'channel flag according to CHANMODES' % v)
            self._invex = v
        return locals()

    _kicklen = None
    @_mkproperty('KICKLEN')
    def kicklen():
        def fset(self, v):
            v = v or None
            if v is not None:
                try:
                    v = int(v)
                except ValueError:
                    raise CapabilityValueError('KICKLEN', v)
            self._kicklen = v
        return locals()

    _maxlist = None
    @_mkproperty('MAXLIST')
    def maxlist():
        def fset(self, v):
            if not v:
                raise CapabilityValueError('MAXLIST', v)
            v = [l.split(':') for l in v.split(',')]
            try:
                v = dict((frozenset(iter(f)), int(l)) for f,l in v)
            except ValueError:
                raise CapabilityValueError('MAXLIST', v)

            # If chanmodes has been set, verify that all A type flags
            # are covered here.
            chanmodes = self.chanmodes
            if chanmodes:
                max = set()
                for flags in v.keys():
                    max.update(flags)
                if max != chanmodes[CHANMODE_LIST]:
                    raise CapabilityLogicError(
                        'MAXLIST set for flags "%s", but CHANMODES says '
                        'there should be the following A type flags: "%s"' % (
                        flags, chanmodes[CHANMODE_LIST]))

            self._maxlist = v
        return locals()

    _modes = 3
    @_mkproperty('MODES', withdel=True)
    def modes():
        def fset(self, v):
            v = v or None
            if v is not None:
                try:
                    v = int(v)
                except ValueError:
                    raise CapabilityValueError('MODES', v)
            self._modes = v
        return locals()

    _network = None
    @_mkproperty('NETWORK')
    def network():
        def fset(self, v):
            if not v:
                raise CapabilityValueError('NETWORK', v)
            self._network = v
        return locals()

    _nicklen = 9
    @_mkproperty('NICKLEN', withdel=True)
    def nicklen():
        def fset(self, v):
            try:
                if not v:
                    raise ValueError
                v = int(v)
            except ValueError:
                raise CapabilityValueError('NICKLEN', v)
            self._nicklen = v
        return locals()

    _prefix = {'o': '@', 'v': '+'}
    @_mkproperty('PREFIX', withdel=True)
    def prefix():
        def fset(self, v):
            v = v or {}
            if v:
                mapping = v[1:].split(')')
                if (v[0] != '(' or
                    len(mapping) != 2 or
                    len(mapping[0]) != len(mapping[1])):
                    raise CapabilityValueError('PREFIX', v)
                v = dict(zip(iter(mapping[0]), iter(mapping[1])))

            # Modes defined in PREFIX should not be also defined in
            # CHANMODES.
            chanmodes = self.chanmodes
            if chanmodes:
                prefix_modes = set(v.keys())
                for modes in chanmodes.values():
                    if modes.intersection(prefix_modes):
                        raise CapabilityLogicError(
                            'User modes "%s" defined in PREFIX '
                            'are also defined as CHANMODES' % prefix_modes)

            # Prefixes defined in STATUSMSG have to be present.
            statusmsg = self.statusmsg
            if not statusmsg.issubset(set(v.values())):
                raise CapabilityLogicError(
                    'User prefixes "%s" defined in STATUSMSG '
                    'are not in the new PREFIX prefixes "%s"' % (
                    ''.join(sorted(statusmsg)), ''.join(sorted(v))))

            self._prefix = v
        return locals()

    _safelist = False
    @_mkproperty('SAFELIST', withdel=True)
    def safelist():
        def fset(self, v):
            if v is not None:
                raise CapabilityValueError('SAFELIST', v)

            self._safelist = True
        return locals()

    _statusmsg = frozenset()
    @_mkproperty('STATUSMSG', withdel=True)
    def statusmsg():
        def fset(self, v):
            v = frozenset(iter(v))

            # STATUSMSG modes must match those in prefix
            prefixes = self.prefix
            if not prefixes:
                raise CapabilityLogicError(
                    'STATUSMSG correctness depends on definition of PREFIX, '
                    'but PREFIX not defined')
            prefixes = set(prefixes.values())
            for prefix in v:
                if prefix not in prefixes:
                    raise CapabilityLogicError(
                        'STATUSMSG prefix "%s" is not in PREFIX: "%s"' %(
                        sorted(v), sorted(prefixes)))

            # STATUSMSG prefixes cannot be the same as CHANTYPES prefixes.
            chantypes = self.chantypes
            if chantypes:
                if chantypes.intersection(v):
                    raise CapabilityLogicError(
                        'STATUSMSG prefixes "%s" intersect with '
                        'some prefixes defined by CHANTYPES.' % sorted(v))

            self._statusmsg = v
        return locals()

    # TODO(dave): Maybe implement STD support one day, but it doesn't
    # look like numeric 005 will ever become a standard.

    _targmax = {}
    @_mkproperty('TARGMAX', withdel=True)
    def targmax():
        def fset(self, v):
            if not v:
                self._targmax = {}
                return
            try:
                targmax = (x.split(':') for x in v.split(','))
                # Technically, 1000 is wrong here. The absence of
                # value means infinity, but for all practical purposes
                # 1000 is large enough in this case.
                targmax = dict((x, int(y or 1000)) for x,y in targmax)
            except ValueError:
                raise CapabilityValueError('TARGMAX', v)
            self._targmax = targmax
        return locals()

    _topiclen = None
    @_mkproperty('TOPICLEN', withdel=True)
    def topiclen():
        def fset(self, v):
            v = v or None
            if v is not None:
                try:
                    v = int(v)
                except ValueError:
                    raise CapabilityValueError('KICKLEN', v)
            self._topiclen = v
        return locals()

    #
    # Helpers to set capabilities from an RPL_ISUPPORT formatted
    # string
    #
    def setCapability(self, cap_str):
        """Set a single capability specified in ISUPPORT format.

        Example: TOPICLEN=5
        """
        cap = cap_str.split('=', 1)
        if len(cap) == 1:
            cap.append(None)
        setattr(self, cap[0].lower(), cap[1])

    def setCapabilities(self, caps_str):
        """Set many capabilities specified in ISUPPORT format.

        Example: INVEX KICKLEN=4 TOPICLEN=42
        """
        for cap in caps_str.split(' '):
            self.setCapability(cap)
