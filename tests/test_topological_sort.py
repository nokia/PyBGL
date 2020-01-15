#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

# Example taken from:
# https://www.boost.org/doc/libs/1_72_0/boost/graph/topological_sort.hpp

from pybgl.graph            import DirectedGraph, add_edge
from pybgl.topological_sort import topological_sort

def test_topological_sort():
    g = DirectedGraph(6)
    for (u, v) in [(0,1), (2,4), (2,5), (0,3), (1,4), (4,3)]:
        add_edge(u, v, g)
    l = topological_sort(g)
    assert list(l) == [2, 5, 0, 1, 4, 3]
