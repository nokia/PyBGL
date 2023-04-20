#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.html import html
from pybgl.ipynb import in_ipynb
from pybgl.graphviz import graph_to_html
from pybgl.trie import Trie, finals, num_vertices
from pybgl.digital_sequence import DigitalSequence

def make_t1():
    t1 = Trie()
    t1.insert("boxeur")
    t1.insert("bougie")
    t1.insert("ananas")
    return t1

def test_trie_string():
    t1 = make_t1()
    if in_ipynb():
        html(graph_to_html(t1))
    assert num_vertices(t1) == 17

def make_t2():
    t2 = Trie()
    t2.insert("bonjour")
    t2.insert(DigitalSequence("bonsoir"))
    return t2

def test_trie_digital_sequence():
    t2 = make_t2()
    if in_ipynb():
        html(graph_to_html(t2))
    assert num_vertices(t2) == 12

def test_trie_trie():
    t1 = make_t1()
    t2 = make_t2()
    t1.insert(t2)
    if in_ipynb():
        html(graph_to_html(t1))
    assert num_vertices(t1) == 26
    assert num_vertices(t2) == 12

def test_included_insertions():
    t3 = Trie()
    t3.insert("aaa")
    assert {q for q in finals(t3)} == {3}
    t3.insert("aa")
    assert {q for q in finals(t3)} == {2, 3}
    t3.insert("")
    assert {q for q in finals(t3)} == {0, 2, 3}
