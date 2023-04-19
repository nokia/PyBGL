#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.graph import *
from pybgl.graphviz import graph_to_html

def test_graph_vertex():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G(2)
        assert set(vertices(g)) == {0, 1}
        assert num_vertices(g) == 2
        assert set(edges(g)) == set()
        assert num_edges(g) == 0
        q = add_vertex(g)
        assert num_vertices(g) == 3
        assert num_edges(g) == 0
        assert set(vertices(g)) == {0, 1, 2}

def test_graph_edge():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G(3)
        (u, v, w) = (q for q in vertices(g))
        assert set(edges(g)) == set()
        assert num_edges(g) == 0
        assert out_degree(u, g) == 0
        assert out_degree(v, g) == 0
        assert out_degree(w, g) == 0

        (e1, added) = add_edge(u, v, g)
        assert added
        assert source(e1, g) == u
        assert target(e1, g) == v
        assert set(edges(g)) == {e1}
        assert num_edges(g) == 1
        assert set(out_edges(u, g)) == {e1}
        assert set(out_edges(v, g)) == set() if is_directed(g) else {e1}
        assert set(out_edges(w, g)) == set()
        assert out_degree(u, g) == 1
        assert out_degree(v, g) == 0 if is_directed(g) else 1
        assert out_degree(w, g) == 0

        (e2, added) = add_edge(u, v, g)
        assert added
        assert source(e2, g) == u
        assert target(e2, g) == v
        assert set(edges(g)) == {e1, e2}
        assert num_edges(g) == 2
        assert set(out_edges(u, g)) == {e1, e2}
        assert set(out_edges(v, g)) == set() if is_directed(g) else {e1, e2}
        assert set(out_edges(w, g)) == set()
        assert out_degree(u, g) == 2
        assert out_degree(v, g) == 0 if is_directed(g) else 2
        assert out_degree(w, g) == 0

        (e3, added) = add_edge(u, w, g)
        assert added
        assert source(e3, g) == u
        assert target(e3, g) == w
        assert set(edges(g)) == {e1, e2, e3}
        assert num_edges(g) == 3
        assert set(out_edges(u, g)) == {e1, e2, e3}
        assert set(out_edges(v, g)) == set() if is_directed(g) else {e1, e2}
        assert set(out_edges(w, g)) == set() if is_directed(g) else {e3}
        assert out_degree(u, g) == 3
        assert out_degree(v, g) == 0 if is_directed(g) else 2
        assert out_degree(w, g) == 0 if is_directed(g) else 1
        assert num_vertices(g) == 3

        remove_edge(e2, g)
        assert num_edges(g) == 2
        assert set(edges(g)) == {e1, e3}
        assert out_degree(u, g) == 2

def test_graph_remove_vertex():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G(3)
        (e1, _) = add_edge(0, 1, g)
        (e2, _) = add_edge(0, 1, g)
        (e3, _) = add_edge(0, 2, g)
        (e4, _) = add_edge(0, 2, g)
        (e5, _) = add_edge(1, 2, g)
        (e6, _) = add_edge(2, 2, g)
        assert num_vertices(g) == 3
        assert set(vertices(g)) == {0, 1, 2}
        assert num_edges(g) == 6
        assert set(edges(g)) == {e1, e2, e3, e4, e5, e6}

        remove_vertex(1, g)
        assert num_vertices(g) == 2
        assert set(vertices(g)) == {0, 2}
        assert num_edges(g) == 3
        assert set(edges(g)) == {e3, e4, e6}

        remove_vertex(2, g)
        assert num_vertices(g) == 1
        assert set(vertices(g)) == {0}
        assert num_edges(g) == 0
        assert set(edges(g)) == set()

def test_graph_is_directed():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G()
        assert is_directed(g) == (G is DirectedGraph)

def test_graph_graphviz():
    for G in [DirectedGraph, UndirectedGraph]:
        g = G(3)
        (e1, _) = add_edge(0, 1, g)
        (e2, _) = add_edge(0, 1, g)
        (e3, _) = add_edge(0, 2, g)
        (e4, _) = add_edge(0, 2, g)
        (e5, _) = add_edge(1, 2, g)
        svg = graph_to_html(g)
