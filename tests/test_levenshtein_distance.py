#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import levenshtein_distance
from pybgl.levenshtein_distance import (
    levenshtein_distance_naive
)


WORDS = [
    "book", "books", "cake",
    "boo", "boon", "cook", "cake", "cape", "cart"
]


def test_levenshtein_distance_identity():
    for w in ["", "abc"]:
        assert levenshtein_distance(w, w) == 0


def test_levenshtein_distance_symmetry():
    w1 = "abcd"
    w2 = "ebgce"
    assert levenshtein_distance(w1, "") == levenshtein_distance("", w1)
    assert levenshtein_distance(w2, "") == levenshtein_distance("", w2)
    assert levenshtein_distance(w1, w2) == levenshtein_distance(w2, w1)


def test_levenshtein_distance():
    for wi in WORDS:
        for wj in WORDS:
            if wi < wj:
                d1 = levenshtein_distance_naive(wi, wj)
                d2 = levenshtein_distance(wi, wj)
                assert d1 == d2


def test_levenshtein_distance_explicit():
    map_xy_expected = {
        ("books", "book"): 1,
        ("books", "books"): 0,
        ("books", "cake"): 4,
        ("books", "boo"): 2,
        ("books", "boon"): 2,
        ("books", "cook"): 2,
        ("books", "cake"): 4,
        ("books", "cape"): 5,
    }
    for ((x, y), expected) in map_xy_expected.items():
        obtained = levenshtein_distance(x, y)
        assert obtained == expected
