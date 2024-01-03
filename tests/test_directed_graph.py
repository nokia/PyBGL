#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.graph import DirectedGraph
(u, v, w) = (0, 1, 2)


def make_g1() -> DirectedGraph:
    g = DirectedGraph()
    g.add_vertex()  # u
    g.add_vertex()  # v
    g.add_vertex()  # w
    return g


def make_g2() -> DirectedGraph:
    g = make_g1()
    g.add_edge(u, v)
    g.add_edge(u, v)  # parallel edge
    g.add_edge(u, w)
    g.add_edge(v, w)
    g.add_edge(w, w)
    return g


def test_directed_graph_num_vertices():
    g = make_g1()
    assert g.num_vertices() == 3


def test_directed_graph_node_add_edge():
    # Make graph
    g = make_g1()
    assert g.out_degree(u) == 0
    assert g.num_edges() == 0

    # Add e1
    (e1, added1) = g.add_edge(u, v)
    assert added1
    (e, found) = g.edge(u, v)
    assert found
    assert e == e1
    assert g.out_degree(u) == 1
    assert g.num_edges() == 1

    # No arc
    (e, found) = g.edge(u, w)
    assert not found
    assert {e for e in g.out_edges(u)} == {e1}

    # Add e2
    (e2, added2) = g.add_edge(u, w)
    assert added2
    assert {e for e in g.out_edges(u)} == {e1, e2}
    assert g.out_degree(u) == 2
    assert g.num_edges() == 2


def test_directed_graph_add_vertex():
    g = make_g2()
    assert g.num_vertices() == 3
    assert g.num_edges() == 5

    # Add vertex x
    x = g.add_vertex()
    assert g.num_vertices() == 4

    # Add edge (v -> x)
    (e1, found) = g.edge(v, w)
    assert found
    (e2, added) = g.add_edge(v, x)
    assert g.num_edges() == 6
    assert {e for e in g.out_edges(v)} == {e1, e2}


def test_directed_graph_remove_edge():
    g = make_g2()
    assert g.num_edges() == 5

    (e, found) = g.edge(v, w)
    g.remove_edge(e)
    assert g.num_edges() == 4

    (e, found) = g.edge(w, w)
    g.remove_edge(e)
    assert g.num_edges() == 3


def test_directed_graph_iterators():
    g = make_g2()

    m = 0
    for _ in g.vertices():
        m += 1
    assert m == g.num_vertices()
    assert m == 3

    n = 0
    for _ in g.edges():
        n += 1
    assert n == g.num_edges()
    assert n == 5


def test_directed_graph_remove_vertex():
    g = make_g2()
    assert g.num_vertices() == 3
    assert g.num_edges() == 5

    g.remove_vertex(v)
    assert g.num_vertices() == 2
    assert g.num_edges() == 2

    g.remove_vertex(w)
    assert g.num_vertices() == 1
    assert g.num_edges() == 0

    g.remove_vertex(u)
    assert g.num_vertices() == 0
    assert g.num_edges() == 0
