#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.digital_sequence import *

def test_num_vertices():
    assert num_vertices(DigitalSequence("")) == 1
    assert num_vertices(DigitalSequence("a")) == 2
    assert num_vertices(DigitalSequence("hello")) == 6

def test_num_edges():
    assert num_edges(DigitalSequence("")) == 0
    assert num_edges(DigitalSequence("a")) == 1
    assert num_edges(DigitalSequence("hello")) == 5

def test_degree():
    for w in ["", "a", "hello"]:
        g = DigitalSequence(w)
        for q in vertices(g):
            if is_initial(q, g):
                assert in_degree(q, g) == 0
            else:
                assert in_degree(q, g) == 1
            if is_final(q, g):
                assert out_degree(q, g) == 0
            else:
                assert out_degree(q, g) == 1

def test_sigma():
    w = "hello"
    g = DigitalSequence(w)
    for q in vertices(g):
        if is_final(q, g):
            assert sigma(q, g) == set()
        else:
            assert sigma(q, g) == {w[q]}

def test_to_dot():
    for w in ["", "a", "hello"]:
        DigitalSequence(w).to_dot()
