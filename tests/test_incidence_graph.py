#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

from pybgl.incidence_graph import IncidenceGraph, add_vertex, add_edge, edge, in_edges, in_degree, num_edges, num_vertices, out_degree, out_edges, remove_vertex, remove_edge

def test_incidence_graph():
    print("Testing num_vertices")
    g = IncidenceGraph(2)
    u = 0
    v = 1
    assert num_vertices(g) == 2

    print("Testing edge (1)")
    (e1, added1) = add_edge(u, v, g)
    assert added1
    (e, found) = edge(u, v, g)
    assert found
    assert e == e1

    print("Testing *_degree and *_edges (1)")
    assert {e for e in in_edges(v, g)} == {e1}
    assert {e for e in out_edges(u, g)} == {e1}
    assert out_degree(u, g) == 1
    assert in_degree(v, g) == 1
    assert num_edges(g) == 1

    print("Testing edge (2)")
    (e, found) = edge(u, v, g)
    assert found
    assert e == e1

    print("Testing *_degree and *_edges (2)")
    (e2, added2) = add_edge(u, v, g)
    assert added2
    assert {e for e in in_edges(v, g)} == {e1, e2}
    assert {e for e in out_edges(u, g)} == {e1, e2}
    assert out_degree(u, g) == 2
    assert in_degree(v, g) == 2
    assert num_edges(g) == 2

    print("Testing add_vertex")
    w = add_vertex(g)
    assert num_vertices(g) == 3
    (e3, added3) = add_edge(u, w, g)
    (e4, added4) = add_edge(u, w, g)
    assert {e for e in out_edges(u, g)} == {e1, e2, e3, e4}
    assert {e for e in in_edges(w, g)} == {e3, e4}
    assert num_edges(g) == 4

    (e5, added3) = add_edge(w, v, g)
    (e6, added4) = add_edge(w, v, g)
    assert {e for e in out_edges(w, g)} == {e5, e6}
    assert {e for e in in_edges(v, g)} == {e1, e2, e5, e6}
    assert num_edges(g) == 6

    print("Testing remove_edge")
    remove_edge(e1, g)
    assert num_edges(g) == 5
    assert {e for e in out_edges(u, g)} == {e2, e3, e4}
    assert {e for e in in_edges(v, g)} == {e2, e5, e6}
    (e, found) = edge(u, v, g)
    assert found
    assert e == e2

    print("Testing remove_vertex")
    remove_vertex(u, g)
    assert num_vertices(g) == 2
    assert num_edges(g) == 2
    assert {e for e in out_edges(w, g)} == {e5, e6}
    assert {e for e in in_edges(v, g)} == {e5, e6}
