#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import damerau_levenshtein_distance as dld
from pybgl.damerau_levenshtein_distance import (
    damerau_levenshtein_distance_naive as dld_naive
)


WORDS = [
    "book", "books", "cake",
    "boo", "boon", "cook", "cake", "cape", "cart"
]


def test_damerau_levenshtein_distance_identity():
    for w in ["", "abc"]:
        assert dld(w, w) == 0


def test_damerau_levenshtein_distance_symmetry():
    w1 = "abcd"
    w2 = "ebgce"
    assert dld(w1, "") == dld("", w1)
    assert dld(w2, "") == dld("", w2)
    assert dld(w1, w2) == dld(w2, w1)


def test_damerau_levenshtein_distance():
    for wi in WORDS:
        for wj in WORDS:
            if wi < wj:
                d1 = dld_naive(wi, wj)
                d2 = dld(wi, wj)
                assert d1 == d2


def test_damerau_levenshtein_distance_2():
    map_xy_expected = {
        ("ab", "ba"): 1,
        ("ba", "abc"): 2,
        ('fee', 'deed'): 2,
    }
    for ((x, y), expected) in map_xy_expected.items():
        obtained = dld(x, y)
        assert obtained == expected
