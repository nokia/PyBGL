#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import cut, DirectedGraph


def test_cut():
    g = DirectedGraph(3)
    (e01, _) = g.add_edge(0, 1)
    (e12, _) = g.add_edge(1, 2)

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
    (e01, _) = g.add_edge(0, 1)
    (e02, _) = g.add_edge(0, 2)
    (e13, _) = g.add_edge(1, 3)
    (e23, _) = g.add_edge(2, 3)

    obtained = cut(0, g, lambda e, g: e in {e01, e02})
    assert obtained == {1, 2}

    obtained = cut(0, g, lambda e, g: e in {e13, e23})
    assert obtained == {3}


def test_cut_tree():
    g = DirectedGraph(9)
    (e01, _) = g.add_edge(0, 1)
    (e02, _) = g.add_edge(0, 2)
    (e23, _) = g.add_edge(2, 3)
    (e24, _) = g.add_edge(2, 4)

    (e35, _) = g.add_edge(3, 5)
    (e36, _) = g.add_edge(3, 6)
    (e45, _) = g.add_edge(4, 7)
    (e46, _) = g.add_edge(4, 8)
    (e19, _) = g.add_edge(1, 9)

    obtained = cut(0, g, lambda e, g: e in {e01, e02})
    assert obtained == {1, 2}

    obtained = cut(0, g, lambda e, g: False)
    assert obtained == {5, 6, 7, 8, 9}

    obtained = cut(0, g, lambda e, g: e in {e01, e23, e24})
    assert obtained == {1, 3, 4}

    obtained = cut(0, g, lambda e, g: e in {e23, e24})
    assert obtained == {3, 4, 9}
