#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from pybgl.graph import DirectedGraph, add_edge
from pybgl.cut   import bfs_cut, dfs_cut

def check_cut(g, map_cut_expected, sources = None):
    if not sources:
        sources = {0}
    for (cut, expected) in map_cut_expected.items():
        for traversal_cut in (dfs_cut, bfs_cut):
            print(f"cut = {cut} traversal_cut = {traversal_cut}")
            obtained = traversal_cut(
                g,
                sources = sources,
                if_push = lambda e, g: e not in cut
            )
            assert obtained == expected, f"obtained = f{obtained}, expected = {expected}"

def test_cut_branch():
    g = DirectedGraph(4)
    (e01, _) = add_edge(0, 1, g)
    (e12, _) = add_edge(1, 2, g)
    (e23, _) = add_edge(2, 3, g)

    map_cut_expected = {
        tuple() : {3},
        (e01, ) : {0},
        (e12, ) : {1},
        (e23, ) : {2},
        (e12, e23) : {1},
    }
    check_cut(g, map_cut_expected)

def test_cut_diamond():
    g = DirectedGraph(4)
    (e01, _) = add_edge(0, 1, g)
    (e13, _) = add_edge(1, 3, g)
    (e02, _) = add_edge(0, 2, g)
    (e23, _) = add_edge(2, 3, g)

    map_cut_expected = {
        tuple() : {3},
        (e01, ) : {3},
        (e13, ) : {1, 3},
        (e01, e02) : {0},
        (e23, ) : {2, 3},
        (e13, e23) : {1, 2},
    }
    check_cut(g, map_cut_expected)

def test_cut_loop():
    g = DirectedGraph(3)
    (e01, _) = add_edge(0, 1, g)
    (e11, _) = add_edge(1, 1, g)
    (e12, _) = add_edge(1, 2, g)

    map_cut_expected = {
        tuple() : {2},
        (e01, ) : {0},
        (e12, ) : {1},
        (e11, e12) : {1},
        (e11, ) : {2},
    }
    check_cut(g, map_cut_expected)

def test_disconnected():
    g = DirectedGraph(6)
    (e01, _) = add_edge(0, 1, g)
    (e12, _) = add_edge(1, 2, g)
    (e34, _) = add_edge(3, 4, g)
    (e45, _) = add_edge(4, 5, g)

    map_cut_expected = {tuple() : {2}}
    check_cut(g, map_cut_expected, sources = {0})
    check_cut(g, map_cut_expected, sources = {1})
    check_cut(g, map_cut_expected, sources = {2})

    map_cut_expected = {tuple() : {5}}
    check_cut(g, map_cut_expected, sources = {3})
    check_cut(g, map_cut_expected, sources = {4})
    check_cut(g, map_cut_expected, sources = {5})

    map_cut_expected = {tuple() : {2, 5}}
    check_cut(g, map_cut_expected, sources = {0, 3})
