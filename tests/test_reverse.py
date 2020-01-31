#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.incidence_graph  import IncidenceGraph, add_edge, in_edges, out_edges, source, target, num_vertices
from pybgl.reverse          import reverse_dict, reverse_graph

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
