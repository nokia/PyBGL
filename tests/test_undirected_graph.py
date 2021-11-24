#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from pybgl.graph import \
    UndirectedGraph, add_vertex, add_edge, edge, edges, num_edges, num_vertices, \
    in_degree, in_edges, out_degree, out_edges, remove_vertex, remove_edge, target

(u, v, w) = (0, 1, 2)

def make_g1() -> UndirectedGraph:
    g1 = UndirectedGraph()
    add_vertex(g1)
    add_vertex(g1)
    add_vertex(g1)
    return g1

def make_g2() -> UndirectedGraph:
    g2 = make_g1()
    add_edge(u, v, g2)
    add_edge(u, v, g2) # parallel edge
    add_edge(u, w, g2)
    add_edge(v, w, g2)
    add_edge(w, w, g2)
    return g2

def test_undirected_graph_num_vertices():
    g1 = make_g1()
    assert num_vertices(g1) == 3

def test_undirected_graph_node_add_edge():
    # Make graph
    g = make_g1()
    assert out_degree(u, g) == 0
    assert num_edges(g) == 0

    # Add e1
    (e1, added1) = add_edge(u, v, g)
    assert added1
    (e, found) = edge(u, v, g)
    assert found
    assert e == e1
    assert out_degree(u, g) == 1
    assert num_edges(g) == 1

    # No arc
    (e, found) = edge(u, w, g)
    assert not found
    assert {e for e in out_edges(u, g)} == {e1}

    # Add e2
    (e2, added2) = add_edge(u, w, g)
    assert added2
    assert {e for e in out_edges(u, g)} == {e1, e2}
    assert out_degree(u, g) == 2
    assert num_edges(g) == 2

def test_undirected_graph_add_vertex():
    g = make_g2()
    assert num_vertices(g) == 3
    assert num_edges(g) == 5

    # Add vertex x
    x = add_vertex(g)
    assert num_vertices(g) == 4

    # Add edge (v -> x)
    add_edge(v, x, g)
    assert num_edges(g) == 6
    assert out_degree(v, g) == 4

def test_undirected_graph_remove_edge():
    g = make_g2()
    assert num_edges(g) == 5

    (e, found) = edge(v, w, g)
    assert found
    remove_edge(e, g)
    assert num_edges(g) == 4

    (e, found) = edge(w, w, g)
    print(g.adjacencies)
    assert found
    remove_edge(e, g)
    assert num_edges(g) == 3

def test_undirected_graph_remove_vertex():
    g = make_g2()
    assert num_vertices(g) == 3
    assert num_edges(g) == 5

    remove_vertex(v, g)
    assert num_vertices(g) == 2
    assert num_edges(g) == 2

    remove_vertex(w, g)
    assert num_vertices(g) == 1
    assert num_edges(g) == 0

    remove_vertex(u, g)
    assert num_vertices(g) == 0
    assert num_edges(g) == 0

def test_undirected_graph():
    g = UndirectedGraph()

    assert num_vertices(g) == 0
    u = add_vertex(g)
    assert num_vertices(g) == 1
    v = add_vertex(g)
    assert num_vertices(g) == 2
    w = add_vertex(g)
    assert num_vertices(g) == 3

    assert num_edges(g) == 0
    e_uv,  _ = add_edge(u, v, g)
    assert num_edges(g) == 1
    e_uv1, _ = add_edge(v, u, g)
    assert num_edges(g) == 2
    e_uw,  _ = add_edge(u, w, g)
    assert num_edges(g) == 3
    e_vw,  _ = add_edge(v, w, g)
    assert num_edges(g) == 4

    print("Edges = %s" % {e for e in edges(g)})

    print("In-edges(%s) = %s" % (u, {e for e in in_edges(u, g)}))
    assert in_degree(u, g) == 3
    assert in_degree(v, g) == 3
    assert in_degree(w, g) == 2, "in_edges(%s) = %s" % (w, {u for u in in_edges(w, g)})

    print("Out-edges(%s) = %s" % (u, {e for e in out_edges(u, g)}))
    assert out_degree(u, g) == 3
    assert out_degree(v, g) == 3
    assert out_degree(w, g) == 2

    print("Removing %s" % e_uv)
    remove_edge(e_uv, g)
    assert num_edges(g) == 3

    print("Removing %s" % e_uv1)
    remove_edge(e_uv1, g)
    assert num_edges(g) == 2

    print("Removing %s" % v)
    remove_vertex(v, g)
    assert num_vertices(g) == 2

    print("Edges = %s" % {e for e in edges(g)})
    assert num_edges(g) == 1

    print("Out-edges(%s) = %s" % (u, {e for e in out_edges(u, g)}))
    assert out_degree(u, g) == 1
    assert out_degree(w, g) == 1
    assert in_degree(u, g) == 1
    assert in_degree(w, g) == 1

