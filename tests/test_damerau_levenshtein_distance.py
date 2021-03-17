#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2021, Nokia"
__license__    = "BSD-3"

from pybgl.damerau_levenshtein_distance import *

WORDS = [
    "book", "books", "cake",
    "boo", "boon", "cook", "cake", "cape", "cart"
]

def test_damerau_levenshtein_identity():
    for w in ["", "abc"]:
        assert damerau_levenshtein_distance(w, w) == 0

def test_levenshtein_symmetry():
    w1 = "abcd"
    w2 = "ebgce"
    assert damerau_levenshtein_distance(w1, "") == damerau_levenshtein_distance("", w1)
    assert damerau_levenshtein_distance(w2, "") == damerau_levenshtein_distance("", w2)
    assert damerau_levenshtein_distance(w1, w2) == damerau_levenshtein_distance(w2, w1)

def test_damerau_levenshtein_distance():
    for wi in WORDS:
        for wj in WORDS:
            if wi < wj:
                d1 = damerau_levenshtein_distance_naive(wi, wj)
                d2 = damerau_levenshtein_distance(wi, wj)
                assert d1 == d2

def test_damerau_levenshtein_distance():
    map_xy_expected = {
        ("ab", "ba")    : 1,
        ("ba", "abc")   : 2,
        ('fee', 'deed') : 2,
    }
    for ((x, y), expected) in map_xy_expected.items():
        obtained = damerau_levenshtein_distance(x, y)
        assert obtained == expected
