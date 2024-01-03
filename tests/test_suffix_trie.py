#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    BOTTOM,
    Trie,
    make_suffix_trie,
    graph_to_html,
    html,
    in_ipynb,
    factors,
)


def test_factors():
    d = {
        "": {""},
        "ab": {"", "a", "b", "ab"},
        "ananas": {
            "",
            "a", "n", "s",
            "an", "na", "as",
            "ana", "nan", "nas",
            "anan", "nana", "anas",
            "anana", "nanas",
            "ananas"
        }
    }
    for (w, expected) in d.items():
        obtained = {factor for factor in factors(w)}
        assert expected == obtained


def check(word, expected_num_vertices, max_len=None):
    t = make_suffix_trie(word, max_len=max_len)
    if in_ipynb():
        html(graph_to_html(t))
    assert t.num_vertices() == expected_num_vertices
    for q in t.vertices():
        assert t.is_final(q)
    assert not t.is_final(BOTTOM)


def test_make_suffix_tree():
    check("ananas", 16)


def test_make_suffix_tree_max_len():
    check("ananas", 10, max_len=3)


def test_max_suffix_tree_g():
    g = Trie()
    make_suffix_trie("ananas", g=g)
    assert g.num_vertices() == 16
