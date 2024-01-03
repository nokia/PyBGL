#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import DigitalSequence


def test_num_vertices():
    for w in ("", "a", "hello"):
        assert DigitalSequence(w).num_vertices() == len(w) + 1


def test_num_edges():
    for w in ("", "a", "hello"):
        assert DigitalSequence(w).num_edges() == len(w)


def test_degree():
    for w in ["", "a", "hello"]:
        g = DigitalSequence(w)
        for q in g.vertices():
            if g.is_initial(q):
                assert g.in_degree(q) == 0
            else:
                assert g.in_degree(q) == 1
            if g.is_final(q):
                assert g.out_degree(q) == 0
            else:
                assert g.out_degree(q) == 1


def test_sigma():
    w = "hello"
    g = DigitalSequence(w)
    for q in g.vertices():
        if g.is_final(q):
            assert g.sigma(q) == set()
        else:
            assert g.sigma(q) == {w[q]}


def test_to_dot():
    for w in ["", "a", "hello"]:
        DigitalSequence(w).to_dot()
