#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.breadth_first_search import (
    DefaultBreadthFirstSearchVisitor,
    breadth_first_search
)
from pybgl.depth_first_search import (
    DefaultDepthFirstSearchVisitor,
    depth_first_search
)
from pybgl.incidence_graph import IncidenceGraph
from pybgl.reverse import reverse_dict, reverse_graph

def test_revert_dict():
    d = {1: "a", 2: "b"}
    assert reverse_dict(d) == {"a": 1, "b": 2}
    d = {1: "a", 2: "b", 3: "b"}
    assert reverse_dict(d) == {"a": 1, "b": 3}

def test_reverse_graph():
    g = IncidenceGraph(2)
    (e01, _) = g.add_edge(0, 1)
    assert g.source(e01) == 0
    assert g.target(e01) == 1
    assert [e for e in g.in_edges(0)] == []
    assert [e for e in g.out_edges(0)] == [e01]
    assert [e for e in g.in_edges(1)] == [e01]
    assert [e for e in g.out_edges(1)] == []

    reverse_graph(g)
    assert g.source(e01) == 1
    assert g.target(e01) == 0
    assert [e for e in g.in_edges(1)] == []
    assert [e for e in g.out_edges(1)] == [e01]
    assert [e for e in g.in_edges(0)] == [e01]
    assert [e for e in g.out_edges(0)] == []

class RecordMixin:
    def __init__(self):
        self.vertices = list()
        self.edges = list()

    def discover_vertex(self, u, g):
        self.vertices.append(u)

    def examine_edge(self, e, g):
        self.edges.append(e)

    def edges_to_pairs(self, g):
        return [(g.source(e), g.target(e)) for e in self.edges]

class RecordDfsVisitor(RecordMixin, DefaultDepthFirstSearchVisitor):
    def __init__(self):
        super().__init__()

class RecordBfsVisitor(RecordMixin, DefaultBreadthFirstSearchVisitor):
    def __init__(self):
        super().__init__()

def test_reverse_traversal():
    g = IncidenceGraph(4)
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(2, 3)

    for (traversal, Visitor) in [
        (breadth_first_search, RecordBfsVisitor),
        (depth_first_search, RecordDfsVisitor),
    ]:
        # Forward: g is: 0 -> 1 -> 2 -> 3
        fwd_vis = Visitor()
        traversal(0, g, vis=fwd_vis)
        assert fwd_vis.vertices == [0, 1, 2, 3]
        assert fwd_vis.edges_to_pairs(g) == [(0, 1), (1, 2), (2, 3)]

        # Backward: g is: 3 -> 2 -> 1 -> 0
        # By reversing the graph
        reverse_graph(g)
        bwd_vis = Visitor()
        traversal(3, g, vis=bwd_vis)
        assert bwd_vis.vertices == [3, 2, 1, 0]
        assert bwd_vis.edges_to_pairs(g) == [(3, 2), (2, 1), (1, 0)]

        # If we reverse the graph once again, note that source and target
        # are also swapped.
        reverse_graph(g)
        assert bwd_vis.edges_to_pairs(g) == [(2, 3), (1, 2), (0, 1)]
