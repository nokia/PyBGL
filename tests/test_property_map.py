#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>
#   Maxime Raynal     <maxime.raynal@nokia.com>

from collections        import defaultdict
from pybgl.property_map import make_func_property_map, make_assoc_property_map, get, put

EXPECTED_RESULT = {
    'a': 'n', 'b': 'o', 'c': 'p', 'd': 'q', 'e': 'r', 'f': 's', 'g': 't', 'h': 'u',
    'i': 'v', 'j': 'w', 'k': 'x', 'l': 'y', 'm': 'z', 'n': 'a', 'o': 'b', 'p': 'c',
    'q': 'd', 'r': 'e', 's': 'f', 't': 'g', 'u': 'h', 'v': 'i', 'w': 'j', 'x': 'k',
    'y': 'l', 'z': 'm'
}

def rot13(c :chr) -> chr:
    return chr((ord(c) - ord('a') + 13) % 26 + ord('a'))

def int2chr(i :int) -> chr:
    return ord('a') + i

def alphabet():
    return (chr(int2chr(i)) for i in range(26))

def check_rot13(pmap_rot13):
    for a in alphabet():
        assert pmap_rot13[a] == get(pmap_rot13, a)
        assert pmap_rot13[a] == rot13(a), "pmap_rot13[%r] = %r != rot13(%r) = %r" % (a, pmap_rot13[a], a, rot13(a))
    assert {a : pmap_rot13[a] for a in alphabet()} == EXPECTED_RESULT

def test_make_func_property_map():
    pmap_rot13 = make_func_property_map(rot13)
    check_rot13(pmap_rot13)

def _test_make_assoc_property_map(with_dict :bool):
    # Build the underlying dictionnary
    d = dict() if with_dict else defaultdict(str) # Here we use str instead of chr, because chr() does not exists!

    # Initialize the property map (and its underlying dict)
    pmap_rot13 = make_assoc_property_map(d)
    for a in alphabet():
        pmap_rot13[a] = rot13(a)

    check_rot13(pmap_rot13)

    # This will not trigger KeyError, because we used defaultdict instead of dict.
    # This is the behavior we expect (std::map<K, V> in C++ ~ defaultdict(V) in python).
    x = pmap_rot13['!']

def test_make_assoc_property_map():
    for b in [False, True]:
        _test_make_assoc_property_map(b)

