#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.breadth_first_search import (
    DefaultBreadthFirstSearchVisitor,
    breadth_first_search
)
from pybgl.depth_first_search import *
from pybgl.incidence_graph    import *
from pybgl.reverse            import reverse_dict, reverse_graph

def test_revert_dict():
    d = {1: "a", 2 : "b"}
    assert reverse_dict(d) == {"a" : 1, "b" : 2}
    d = {1: "a", 2 : "b", 3 : "b"}
    assert reverse_dict(d) == {"a" : 1, "b" : 3}

def test_reverse_graph():
    g = IncidenceGraph(2)
    (e01, _) = add_edge(0, 1, g)
    assert source(e01, g) == 0
    assert target(e01, g) == 1
    assert [e for e in in_edges(0, g)]  == []
    assert [e for e in out_edges(0, g)] == [e01]
    assert [e for e in in_edges(1, g)]  == [e01]
    assert [e for e in out_edges(1, g)] == []

    reverse_graph(g)
    assert source(e01, g) == 1
    assert target(e01, g) == 0
    assert [e for e in in_edges(1, g)]  == []
    assert [e for e in out_edges(1, g)] == [e01]
    assert [e for e in in_edges(0, g)]  == [e01]
    assert [e for e in out_edges(0, g)] == []

class RecordMixin:
    def __init__(self):
        self.vertices = list()
        self.edges = list()

    def discover_vertex(self, u, g):
        self.vertices.append(u)

    def examine_edge(self, e, g):
        self.edges.append(e)

    def edges_to_pairs(self, g):
        return [(source(e, g), target(e, g)) for e in self.edges]

class RecordDfsVisitor(RecordMixin, DefaultDepthFirstSearchVisitor):
    def __init__(self):
        super().__init__()

class RecordBfsVisitor(RecordMixin, DefaultBreadthFirstSearchVisitor):
    def __init__(self):
        super().__init__()

def test_reverse_traversal():
    g = IncidenceGraph(4)
    add_edge(0, 1, g)
    add_edge(1, 2, g)
    add_edge(2, 3, g)

    for (traversal, Visitor) in [
        (breadth_first_search, RecordBfsVisitor),
        (depth_first_search, RecordDfsVisitor),
    ]:
        # Forward: g is: 0 -> 1 -> 2 -> 3
        fwd_vis = Visitor()
        traversal(0, g, vis = fwd_vis)
        assert fwd_vis.vertices == [0, 1, 2, 3]
        assert fwd_vis.edges_to_pairs(g) == [(0, 1), (1, 2), (2, 3)]

        # Backward: g is: 3 -> 2 -> 1 -> 0
        # By reversing the graph
        reverse_graph(g)
        bwd_vis = Visitor()
        traversal(3, g, vis = bwd_vis)
        assert bwd_vis.vertices == [3, 2, 1, 0]
        assert bwd_vis.edges_to_pairs(g) == [(3, 2), (2, 1), (1, 0)]

        # If we reverse the graph once again, note that source and target
        # are also swapped.
        reverse_graph(g)
        assert bwd_vis.edges_to_pairs(g) == [(2, 3), (1, 2), (0, 1)]
