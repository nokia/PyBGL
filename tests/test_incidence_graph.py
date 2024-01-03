#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import IncidenceGraph


def test_incidence_graph(debug: bool = False):
    if not debug:
        def print(*args, **kwargs):
            pass

    print("Testing num_vertices")
    g = IncidenceGraph(2)
    u = 0
    v = 1
    assert g.num_vertices() == 2

    print("Testing edge (1)")
    (e1, added1) = g.add_edge(u, v)
    assert added1
    (e, found) = g.edge(u, v)
    assert found
    assert e == e1

    print("Testing *_degree and *_edges (1)")
    assert {e for e in g.in_edges(v)} == {e1}
    assert {e for e in g.out_edges(u)} == {e1}
    assert g.out_degree(u) == 1
    assert g.in_degree(v) == 1
    assert g.num_edges() == 1

    print("Testing edge (2)")
    (e, found) = g.edge(u, v)
    assert found
    assert e == e1

    print("Testing *_degree and *_edges (2)")
    (e2, added2) = g.add_edge(u, v)
    assert added2
    assert {e for e in g.in_edges(v)} == {e1, e2}
    assert {e for e in g.out_edges(u)} == {e1, e2}
    assert g.out_degree(u) == 2
    assert g.in_degree(v) == 2
    assert g.num_edges() == 2

    print("Testing add_vertex")
    w = g.add_vertex()
    assert g.num_vertices() == 3
    (e3, added3) = g.add_edge(u, w)
    (e4, added4) = g.add_edge(u, w)
    assert {e for e in g.out_edges(u)} == {e1, e2, e3, e4}
    assert {e for e in g.in_edges(w)} == {e3, e4}
    assert g.num_edges() == 4

    (e5, added3) = g.add_edge(w, v)
    (e6, added4) = g.add_edge(w, v)
    assert {e for e in g.out_edges(w)} == {e5, e6}
    assert {e for e in g.in_edges(v)} == {e1, e2, e5, e6}
    assert g.num_edges() == 6

    print("Testing remove_edge")
    g.remove_edge(e1)
    assert g.num_edges() == 5
    assert {e for e in g.out_edges(u)} == {e2, e3, e4}
    assert {e for e in g.in_edges(v)} == {e2, e5, e6}
    (e, found) = g.edge(u, v)
    assert found
    assert e == e2

    print("Testing remove_vertex")
    g.remove_vertex(u)
    assert g.num_vertices() == 2
    assert g.num_edges() == 2
    assert {e for e in g.out_edges(w)} == {e5, e6}
    assert {e for e in g.in_edges(v)} == {e5, e6}
