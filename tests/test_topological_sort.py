#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import DirectedGraph, topological_sort


def test_topological_sort():
    # Example taken from:
    # https://www.boost.org/doc/libs/1_72_0/boost/graph/topological_sort.hpp
    g = DirectedGraph(6)
    for (u, v) in [(0, 1), (2, 4), (2, 5), (0, 3), (1, 4), (4, 3)]:
        g.add_edge(u, v)
    ret = topological_sort(g)
    assert list(ret) == [2, 5, 0, 1, 4, 3]
