#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.cut import cut
from pybgl.graph import DirectedGraph, add_edge

def test_cut():
    g = DirectedGraph(3)
    (e01, _) = add_edge(0, 1, g)
    (e12, _) = add_edge(1, 2, g)

    obtained = cut(0, g, lambda e, g: e in {e01})
    assert obtained == {1}

    obtained = cut(0, g, lambda e, g: e in {e12})
    assert obtained == {2}

    obtained = cut(0, g, lambda e, g: False)
    assert obtained == {2}

    obtained = cut(0, g, lambda e, g: True)
    assert obtained == {1}

def test_cut_diamond():
    g = DirectedGraph(4)
    (e01, _) = add_edge(0, 1, g)
    (e02, _) = add_edge(0, 2, g)
    (e13, _) = add_edge(1, 3, g)
    (e23, _) = add_edge(2, 3, g)

    obtained = cut(0, g, lambda e, g: e in {e01, e02})
    assert obtained == {1, 2}

    obtained = cut(0, g, lambda e, g: e in {e13, e23})
    assert obtained == {3}

def test_cut_tree():
    g = DirectedGraph(9)
    (e01, _) = add_edge(0, 1, g)
    (e02, _) = add_edge(0, 2, g)
    (e23, _) = add_edge(2, 3, g)
    (e24, _) = add_edge(2, 4, g)

    (e35, _) = add_edge(3, 5, g)
    (e36, _) = add_edge(3, 6, g)
    (e45, _) = add_edge(4, 7, g)
    (e46, _) = add_edge(4, 8, g)
    (e19, _) = add_edge(1, 9, g)

    obtained = cut(0, g, lambda e, g: e in {e01, e02})
    assert obtained == {1, 2}

    obtained = cut(0, g, lambda e, g: False)
    assert obtained == {5, 6, 7, 8, 9}

    obtained = cut(0, g, lambda e, g: e in {e01, e23, e24})
    assert obtained == {1, 3, 4}

    obtained = cut(0, g, lambda e, g: e in {e23, e24})
    assert obtained == {3, 4, 9}
