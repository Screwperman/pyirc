# -*- coding: utf-8 -*-
#
# Unit tests for ServerCapabilities

import unittest
import server_capabilities as scap

class TestServerCapabilities(unittest.TestCase):
    def testCasemapping(self):
        """CASEMAPPING capability semantics"""
        c = scap.ServerCapabilities()

        # Default value
        self.assertEquals(c.casemapping, 'ascii')

        # Explicitely setting 'ascii'
        c.casemapping = 'ascii'
        self.assertEquals(c.casemapping, 'ascii')

        # Setting other valid values. We don't support them, so check
        # that we do raise the appropriate exception.
        self.assertRaises(
            NotImplementedError, setattr, c, 'casemapping', 'rfc1459')
        self.assertRaises(
            NotImplementedError, setattr, c, 'casemapping', 'strict-rfc1459')

        # Setting invalid values raises a value error.
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'casemapping', 'bleh')
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'casemapping', '')
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'casemapping', None)

        # Deleting resets to the default.
        del c.casemapping
        self.assertEquals(c.casemapping, 'ascii')

    def testChanlimit(self):
        """CHANLIMIT capability semantics"""
        c = scap.ServerCapabilities()

        # No default
        self.assertEquals(c.chanlimit, None)

        # Setting limits for default chantypes should work
        c.chanlimit = '#:5,&:2'
        self.assertEquals(c.chanlimit, {frozenset(['#']): 5,
                                        frozenset(['&']): 2})

        # Multiple prefixes per limit
        c.chanlimit = '#&:10'
        self.assertEquals(c.chanlimit, {frozenset(['#', '&']): 10})

        # Empty chanlimit forbidden
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'chanlimit', '')
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'chanlimit', None)

        # Chanlimit with unknown prefixes forbidden
        self.assertRaises(
            scap.CapabilityLogicError, setattr, c, 'chanlimit', '%:3')

        # Cannot delete chanlimit
        self.assertRaises(AttributeError, delattr, c, 'chanlimit')

    def testChanmodes(self):
        c = scap.ServerCapabilities()

        # No default
        self.assertEquals(c.chanmodes, None)

        # Setting modes works
        c.chanmodes = 'ab,cd,ef,gh'
        self.assertEquals(c.chanmodes,
                          {scap.CHANMODE_LIST: frozenset(['a', 'b']),
                           scap.CHANMODE_PARAM_ALWAYS: frozenset(['c', 'd']),
                           scap.CHANMODE_PARAM_ADDONLY: frozenset(['e', 'f']),
                           scap.CHANMODE_NO_PARAM: frozenset(['g', 'h'])})

        # Setting no flags for certain types is fine
        c.chanmodes = 'ab,,ef,gh'
        self.assertEquals(c.chanmodes,
                          {scap.CHANMODE_LIST: frozenset(['a', 'b']),
                           scap.CHANMODE_PARAM_ALWAYS: frozenset(),
                           scap.CHANMODE_PARAM_ADDONLY: frozenset(['e', 'f']),
                           scap.CHANMODE_NO_PARAM: frozenset(['g', 'h'])})

        # Setting no flags for all types is also fine
        c.chanmodes = ',,,'
        self.assertEquals(c.chanmodes,
                          {scap.CHANMODE_LIST: frozenset(),
                           scap.CHANMODE_PARAM_ALWAYS: frozenset(),
                           scap.CHANMODE_PARAM_ADDONLY: frozenset(),
                           scap.CHANMODE_NO_PARAM: frozenset()})

        # Setting more than 4 channel types is cool, we ignore what is
        # probably a future extension.
        c.chanmodes = 'ab,cd,ef,gh,i,j,klm'
        self.assertEquals(c.chanmodes,
                          {scap.CHANMODE_LIST: frozenset(['a', 'b']),
                           scap.CHANMODE_PARAM_ALWAYS: frozenset(['c', 'd']),
                           scap.CHANMODE_PARAM_ADDONLY: frozenset(['e', 'f']),
                           scap.CHANMODE_NO_PARAM: frozenset(['g', 'h'])})

        # Setting less than 4 is not cool.
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'chanmodes', 'ab,cd')

        # Cannot delete chanmodes
        self.assertRaises(AttributeError, delattr, c, 'chanmodes')

        # Check that all caps that depend on chanmodes values get
        # rechecked on change.
        c.excepts = 'a'
        self.assertRaises(
            scap.CapabilityLogicError, setattr, c, 'chanmodes', ',,,')
        self.assertEquals(c.chanmodes,
                          {scap.CHANMODE_LIST: frozenset(['a', 'b']),
                           scap.CHANMODE_PARAM_ALWAYS: frozenset(['c', 'd']),
                           scap.CHANMODE_PARAM_ADDONLY: frozenset(['e', 'f']),
                           scap.CHANMODE_NO_PARAM: frozenset(['g', 'h'])})
        del c.excepts

        c.invex = 'b'
        self.assertRaises(
            scap.CapabilityLogicError, setattr, c, 'chanmodes', ',,,')
        self.assertEquals(c.chanmodes,
                          {scap.CHANMODE_LIST: frozenset(['a', 'b']),
                           scap.CHANMODE_PARAM_ALWAYS: frozenset(['c', 'd']),
                           scap.CHANMODE_PARAM_ADDONLY: frozenset(['e', 'f']),
                           scap.CHANMODE_NO_PARAM: frozenset(['g', 'h'])})
        del c.invex

        c.maxlist = 'ab:100'
        self.assertRaises(
            scap.CapabilityLogicError, setattr, c, 'chanmodes', ',,,')

    def testChannellen(self):
        c = scap.ServerCapabilities()

        # Default value
        self.assertEquals(c.channellen, 200)

        # Explicitely setting a new value
        c.channellen = 40
        self.assertEquals(c.channellen, 40)

        # Explicitely setting no value
        c.channellen = None
        self.assertEquals(c.channellen, None)

        # Setting a non-int value fails
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'channellen', 'bleh')

        # Deleting resets to the default.
        del c.channellen
        self.assertEquals(c.channellen, 200)

    def testChantypes(self):
        c = scap.ServerCapabilities()

        # Default value
        self.assertEquals(c.chantypes, frozenset(['#', '&']))

        # Explicitely setting a new value
        c.chantypes = '#&!'
        self.assertEquals(c.chantypes, frozenset(['#', '&', '!']))

        # Explicitely setting no value
        c.chantypes = None
        self.assertEquals(c.chantypes, frozenset())
        c.chantypes = ''
        self.assertEquals(c.chantypes, frozenset())

        # Setting channel limits restricts what we can do to this
        # field.
        c.chantypes = '#'
        c.chanlimit = '#:5'
        self.assertRaises(scap.CapabilityLogicError, setattr, c, 'chantypes', '&')

        # Deleting resets to the default.
        del c.chantypes
        self.assertEquals(c.chantypes, frozenset(['#', '&']))

    def testExcepts(self):
        c = scap.ServerCapabilities()

        # No default value
        self.assertEquals(c.excepts, None)

        # Set using the default channel flag
        c.excepts = None
        self.assertEquals(c.excepts, 'e')
        c.excepts = ''
        self.assertEquals(c.excepts, 'e')

        # Set a custom flag
        c.excepts = 'f'
        self.assertEquals(c.excepts, 'f')

        # Set a wonky flag
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'excepts', 'bleh')

        # If chanmodes are set, the excepts flag must be an A type
        # chanmode.
        c.chanmodes = 'abf,,,'
        self.assertRaises(
            scap.CapabilityLogicError, setattr, c, 'excepts', 'e')
        c.excepts = 'a'
        self.assertEquals(c.excepts, 'a')

    def testInvex(self):
        c = scap.ServerCapabilities()

        # No default value
        self.assertEquals(c.invex, None)

        # Set using the default channel flag
        c.invex = None
        self.assertEquals(c.invex, 'I')
        c.invex = ''
        self.assertEquals(c.invex, 'I')

        # Set a custom flag
        c.invex = 'X'
        self.assertEquals(c.invex, 'X')

        # Set a wonky flag
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'invex', 'bleh')

        # If chanmodes are set, the invex flag must be an A type
        # chanmode.
        c.chanmodes = 'abX,,,'
        self.assertRaises(
            scap.CapabilityLogicError, setattr, c, 'invex', 'k')
        c.excepts = 'a'
        self.assertEquals(c.excepts, 'a')

    def testKicklen(self):
        c = scap.ServerCapabilities()

        # No default value
        self.assertEquals(c.kicklen, None)

        # Set using the default value (no limit, same as default)
        c.kicklen = None
        self.assertEquals(c.kicklen, None)
        c.kicklen = ''
        self.assertEquals(c.kicklen, None)

        # Set an explicit value
        c.kicklen = '150'
        self.assertEquals(c.kicklen, 150)

        # Setting an invalid value fails.
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'kicklen', 'bleh')

        # No default value, so no deletion possible.
        self.assertRaises(AttributeError, delattr, c, 'kicklen')

    def testMaxlist(self):
        c = scap.ServerCapabilities()

        # No default value
        self.assertEquals(c.maxlist, None)

        # Set values
        c.maxlist = 'b:100,e:200,I:150'
        self.assertEquals(c.maxlist, {frozenset(['b']): 100,
                                      frozenset(['e']): 200,
                                      frozenset(['I']): 150})
        c.maxlist = 'beI: 42'
        self.assertEquals(c.maxlist, {frozenset(['b', 'e', 'I']): 42})

        # Set incorrect values
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'maxlist', None)
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'maxlist', '')
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'maxlist', 'b:bleh')
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'maxlist', '#$(@*@')

        # Setting chanmodes should restrict the possible values for
        # maxlist.
        c.chanmodes = 'beI,,,'
        self.assertRaises(
            scap.CapabilityLogicError, setattr, c, 'maxlist', 'be:100')
        c.maxlist = 'b:100,eI:42'
        self.assertEquals(c.maxlist, {frozenset(['b']): 100,
                                      frozenset(['e', 'I']): 42})

        # No deletion possible.
        self.assertRaises(AttributeError, delattr, c, 'maxlist')

    def testModes(self):
        c = scap.ServerCapabilities()

        # Default value
        self.assertEquals(c.modes, 3)

        # Setting no value
        c.modes = None
        self.assertEquals(c.modes, None)
        c.modes = ''
        self.assertEquals(c.modes, None)

        # Setting an explicit value
        c.modes = '5'
        self.assertEquals(c.modes, 5)

        # Setting an invalid value
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'modes', 'bleh')

        # Deletion restores default
        del c.modes
        self.assertEquals(c.modes, 3)

    def testNetwork(self):
        c = scap.ServerCapabilities()

        # No default value
        self.assertEquals(c.network, None)

        # Setting no value fails
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'network', '')
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'network', None)

        # Setting values is cool
        c.network = 'bleh'
        self.assertEquals(c.network, 'bleh')
        c.network = 'freenode'
        self.assertEquals(c.network, 'freenode')

        # No deletion
        self.assertRaises(AttributeError, delattr, c, 'network')

    def testNicklen(self):
        c = scap.ServerCapabilities()

        # Default value
        self.assertEquals(c.nicklen, 9)

        # Setting no value fails
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'nicklen', '')
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'nicklen', None)

        # Setting integer values is cool
        c.nicklen = 3
        self.assertEquals(c.nicklen, 3)
        c.nicklen = 32
        self.assertEquals(c.nicklen, 32)

        # Setting garbage values is not cool
        self.assertRaises(
            scap.CapabilityValueError, setattr, c, 'nicklen', 'bleh')

        # Deletion resets default
        del c.nicklen
        self.assertEquals(c.nicklen, 9)
