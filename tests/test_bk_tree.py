#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import graph_to_html, make_bk_tree


WORDS = [
    "book", "books", "cake",
    "boo", "boon", "cook", "cake", "cape", "cart"
]

TREE = make_bk_tree(WORDS)


def test_bk_tree_completeness():
    assert set(WORDS) == {
        TREE.element(u)
        for u in TREE.vertices()
    }


def test_bk_tree_weights():
    for e in TREE.edges():
        u = TREE.source(e)
        v = TREE.target(e)
        d_uv = TREE.label(e)
        w_u = TREE.element(u)
        w_v = TREE.element(v)
        assert d_uv == TREE.distance(w_u, w_v)


def test_bk_tree_exact_match(debug=False):
    for w in WORDS:
        (w_found, d) = TREE.search(w)
        if debug:
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
    n = TREE.num_vertices()
    for w in WORDS:
        TREE.insert(w)
        assert TREE.num_vertices() == n


def test_bk_tree_graphviz():
    s = graph_to_html(TREE)
    assert isinstance(s, str)
