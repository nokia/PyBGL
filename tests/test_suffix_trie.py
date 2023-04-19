#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.automaton import Automaton
from pybgl.graphviz import graph_to_html
from pybgl.html import html
from pybgl.ipynb import in_ipynb
from pybgl.trie import is_final, num_vertices, vertices
from pybgl.suffix_trie import BOTTOM, factors, make_suffix_trie

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

def test_make_suffix_tree():
    t = make_suffix_trie("ananas")
    if in_ipynb():
        html(graph_to_html(t))
    assert num_vertices(t) == 16
    for q in vertices(t):
        assert is_final(q, t)
    assert not is_final(BOTTOM, t)

def test_make_suffix_tree_max_len():
    t = make_suffix_trie("ananas", max_len=3)
    if in_ipynb():
        html(graph_to_html(t))
    assert num_vertices(t) == 10
    for q in vertices(t):
        assert is_final(q, t)
    assert not is_final(BOTTOM, t)

def test_max_suffix_tree_g():
    t = make_suffix_trie("ananas")
    if in_ipynb(): html(graph_to_html(t))
    assert num_vertices(t) == 16
    for q in vertices(t):
        assert is_final(q, t)
    assert not is_final(BOTTOM, t)
