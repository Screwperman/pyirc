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
