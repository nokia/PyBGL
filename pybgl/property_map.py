#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Property maps are abstraction offering get() and eventually put() primitives
# on top of dict, vector, or functions. They are useful to design algorithms
# without constraints regarding how the mapping taken in parameter are realized.
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from collections import defaultdict

class PropertyMap:
    pass

def get(pmap, k):
    return pmap.get(k)

def put(pmap, k, v):
    pmap.put(k, v)

class ReadPropertyMap(PropertyMap):
    def get(self, k): pass
    def put(self, k, v): raise RuntimeError("Cannot call put on a ReadPropertyMap")

    def __getitem__(self, k): return self.get(k)
    def __setitem__(self, k, v): self.put(k, v)

class FuncPropertyMap(ReadPropertyMap):
    def __init__(self, f):
        self.m_f = f

    def get(self, k):
        return self.m_f(k)

def make_func_property_map(f):
    return FuncPropertyMap(f)

class ReadWritePropertyMap(PropertyMap):
    def get(self, k): pass
    def put(self, k, v): pass

    def __getitem__(self, k): return self.get(k)
    def __setitem__(self, k, v): self.put(k, v)

class AssocPropertyMap(ReadWritePropertyMap):
    """
    AssocPropertyMap is a ReadWritePropertyMap wrapping a dict, or rather a defaultdict.
    Hence it behaves like in libboost.

    Example:
        from collections import defaultdict
        d = defaultdict(int)
        d['a'] = 7
        pmap = make_assoc_property_map(d)
        print(pmap['a']) # Returns 7
        pmap['a'] = 8
        print(pmap['a']) # Returns 8
        print(pmap['b']) # Returns 0, like in C++ (no KeyError)
    """
    def __init__(self, d :defaultdict, default = None):
        assert isinstance(d, (defaultdict, dict)), "Invalid parameter: d = %s (%s) must be a defaultdict" % (d, type(d))
        self.m_d = d
        self.m_default = default

    def get(self, k):
        # The following test ensures compatibility with normal dict.
        # Since defaultdict inherits dict, the following test is a little bit weird...
        if not isinstance(self.m_d, defaultdict) and isinstance(self.m_d, dict):
            return self.m_d.get(k, self.m_default)
        else:
            return self.m_d[k]

    def put(self, k, v):
        self.m_d[k] = v

    def __delitem__(self, k):
        print("/!\\ WARNING: You're not supposed to delete keys in property maps /!\\")
        del self.m_d[k]

def make_assoc_property_map(d :defaultdict, default = None):
    return AssocPropertyMap(d, default)

class IdentityPropertyMap(ReadPropertyMap):
    def get(self, k): return k

def identity_property_map():
    return IdentityPropertyMap()

class ConstantPropertyMap(ReadWritePropertyMap):
    def __init__(self, value):
        self.m_value = value
    def get(self, key):
        return self.m_value
    def set(self, key, value):
        pass

def make_constant_property_map(value) -> ConstantPropertyMap:
    return ConstantPropertyMap(value)
