#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import DigitalSequence, Trie, graph_to_html, html, in_ipynb


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
    assert t1.num_vertices() == 17


def make_t2():
    t2 = Trie()
    t2.insert("bonjour")
    t2.insert(DigitalSequence("bonsoir"))
    return t2


def test_trie_digital_sequence():
    t2 = make_t2()
    if in_ipynb():
        html(graph_to_html(t2))
    assert t2.num_vertices() == 12


def test_trie_trie():
    t1 = make_t1()
    t2 = make_t2()
    t1.insert(t2)
    if in_ipynb():
        html(graph_to_html(t1))
    assert t1.num_vertices() == 26
    assert t2.num_vertices() == 12


def test_included_insertions():
    t3 = Trie()
    t3.insert("aaa")
    assert {q for q in t3.finals()} == {3}
    t3.insert("aa")
    assert {q for q in t3.finals()} == {2, 3}
    t3.insert("")
    assert {q for q in t3.finals()} == {0, 2, 3}
