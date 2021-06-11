#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2021, Nokia"
__license__    = "BSD-3"

from pybgl.lcs_distance import *

WORDS = [
    "book", "books", "cake",
    "boo", "boon", "cook", "cake", "cape", "cart"
]

def test_lcs_distance_identity():
    for w in ["", "abc"]:
        assert lcs_distance(w, w) == 0

def test_lcs_distance_symmetry():
    w1 = "abcd"
    w2 = "ebgce"
    assert lcs_distance(w1, "") == lcs_distance("", w1)
    assert lcs_distance(w2, "") == lcs_distance("", w2)
    assert lcs_distance(w1, w2) == lcs_distance(w2, w1)

def test_lcs_distance():
    for wi in WORDS:
        for wj in WORDS:
            if wi < wj:
                d1 = lcs_distance_naive(wi, wj)
                d2 = lcs_distance(wi, wj)
                assert d1 == d2

def test_lcs_distance():
    map_xy_expected = {
        ("books", "book")  : 1,
        ("books", "books") : 0,
        ("books", "cake")  : 7,
        ("books", "boo")   : 2,
        ("books", "boon")  : 3,
        ("books", "cook")  : 3,
        ("books", "cake")  : 7,
        ("books", "cape")  : 9,
    }
    for ((x, y), expected) in map_xy_expected.items():
        obtained = lcs_distance(x, y)
        assert obtained == expected
