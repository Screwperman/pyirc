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
            self._chanmodes = dict(enumerate(frozenset(iter(x)) for x in v))
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
                    if prefixes not in types:
                        raise CapabilityLogicError(
                            'Channel types redefined to "%s", but CHANLIMIT '
                            'specifies limits for prefix(es) "%s"' % (types,
                                                                      prefixes))
            self._chantypes = types
        return locals()
