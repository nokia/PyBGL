#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2021, Nokia"
__license__    = "BSD-3"

from pybgl.bk_tree import *

WORDS = [
    "book", "books", "cake",
    "boo", "boon", "cook", "cake", "cape", "cart"
]

TREE = make_bk_tree(WORDS)

def test_bk_tree_completeness():
    assert set(WORDS) == {
        TREE.element(u)
        for u in vertices(TREE)
    }

def test_bk_tree_weights():
    for e in edges(TREE):
        u = source(e, TREE)
        v = target(e, TREE)
        d_uv = label(e, TREE)
        w_u = TREE.element(u)
        w_v = TREE.element(v)
        assert d_uv == TREE.distance(w_u, w_v)

def test_bk_tree_exact_match():
    for w in WORDS:
        (w_found, d) = TREE.search(w)
        print(f"Exact match {w} {w_found} {d}")
        assert w == w_found

def test_bk_tree_fuzzy_match():
    assert TREE.search("boy") == ("boo", 1)
    assert TREE.search("card") == ("cart", 1)
    assert TREE.search("curry") == ("cart", 3)

def test_bk_tree_caped_fuzzy_match():
    assert TREE.search("boy", 2) == ("boo", 1)
    assert TREE.search("boy", 1) == ("boo", 1)
    assert TREE.search("curry", 2) is None, TREE.search("curry", 2)

def test_bk_tree_duplicate():
    n = num_vertices(TREE)
    for w in WORDS:
        TREE.insert(w)
        assert num_vertices(TREE) == n

def test_bk_tree_graphviz():
    from pybgl.graphviz import graph_to_html
    s = graph_to_html(TREE)
    assert isinstance(s, str)
