#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    DirectedGraph,
    UndirectedGraph,
    graph_to_html,
)


def test_graph_vertex():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G(2)
        assert set(g.vertices()) == {0, 1}
        assert g.num_vertices() == 2
        assert set(g.edges()) == set()
        assert g.num_edges() == 0
        _ = g.add_vertex()
        assert g.num_vertices() == 3
        assert g.num_edges() == 0
        assert set(g.vertices()) == {0, 1, 2}


def test_graph_edge():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G(3)
        (u, v, w) = (q for q in g.vertices())
        assert set(g.edges()) == set()
        assert g.num_edges() == 0
        assert g.out_degree(u) == 0
        assert g.out_degree(v) == 0
        assert g.out_degree(w) == 0

        (e1, added) = g.add_edge(u, v)
        assert added
        assert g.source(e1) == u
        assert g.target(e1) == v
        assert set(g.edges()) == {e1}
        assert g.num_edges() == 1
        assert set(g.out_edges(u)) == {e1}
        assert set(g.out_edges(v)) == set() if g.directed else {e1}
        assert set(g.out_edges(w)) == set()
        assert g.out_degree(u) == 1
        assert g.out_degree(v) == 0 if g.directed else 1
        assert g.out_degree(w) == 0

        (e2, added) = g.add_edge(u, v)
        assert added
        assert g.source(e2) == u
        assert g.target(e2) == v
        assert set(g.edges()) == {e1, e2}
        assert g.num_edges() == 2
        assert set(g.out_edges(u)) == {e1, e2}
        assert set(g.out_edges(v)) == set() if g.directed else {e1, e2}
        assert set(g.out_edges(w)) == set()
        assert g.out_degree(u) == 2
        assert g.out_degree(v) == 0 if g.directed else 2
        assert g.out_degree(w) == 0

        (e3, added) = g.add_edge(u, w)
        assert added
        assert g.source(e3) == u
        assert g.target(e3) == w
        assert set(g.edges()) == {e1, e2, e3}
        assert g.num_edges() == 3
        assert set(g.out_edges(u)) == {e1, e2, e3}
        assert set(g.out_edges(v)) == set() if g.directed else {e1, e2}
        assert set(g.out_edges(w)) == set() if g.directed else {e3}
        assert g.out_degree(u) == 3
        assert g.out_degree(v) == 0 if g.directed else 2
        assert g.out_degree(w) == 0 if g.directed else 1
        assert g.num_vertices() == 3

        g.remove_edge(e2)
        assert g.num_edges() == 2
        assert set(g.edges()) == {e1, e3}
        assert g.out_degree(u) == 2


def test_graph_remove_vertex():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G(3)
        (e1, _) = g.add_edge(0, 1)
        (e2, _) = g.add_edge(0, 1)
        (e3, _) = g.add_edge(0, 2)
        (e4, _) = g.add_edge(0, 2)
        (e5, _) = g.add_edge(1, 2)
        (e6, _) = g.add_edge(2, 2)
        assert g.num_vertices() == 3
        assert set(g.vertices()) == {0, 1, 2}
        assert g.num_edges() == 6
        assert set(g.edges()) == {e1, e2, e3, e4, e5, e6}

        g.remove_vertex(1)
        assert g.num_vertices() == 2
        assert set(g.vertices()) == {0, 2}
        assert g.num_edges() == 3
        assert set(g.edges()) == {e3, e4, e6}

        g.remove_vertex(2)
        assert g.num_vertices() == 1
        assert set(g.vertices()) == {0}
        assert g.num_edges() == 0
        assert set(g.edges()) == set()


def test_graph_clear():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G(3)
        (e1, _) = g.add_edge(0, 1)
        (e2, _) = g.add_edge(0, 1)
        (e3, _) = g.add_edge(0, 2)
        (e4, _) = g.add_edge(0, 2)
        g.clear()
        assert set(g.edges()) == set()
        assert set(g.vertices()) == set()


def test_graph_g_directed():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G()
        assert g.directed == (G is DirectedGraph)


def test_graph_graphviz():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G(3)
        (e1, _) = g.add_edge(0, 1)
        (e2, _) = g.add_edge(0, 1)
        (e3, _) = g.add_edge(0, 2)
        (e4, _) = g.add_edge(0, 2)
        (e5, _) = g.add_edge(1, 2)
        s = graph_to_html(g)
        assert isinstance(s, str)
