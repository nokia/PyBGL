#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
#This file is part of veggie
#Copyright © 2018 Nokia Corporation and/or its subsidiary(-ies). All rights reserved. *
#
#Contact:
#    Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>
#    Anne Bouillard    <anne.bouillard@nokia-bell-labs.com>
#    Achille Salaün    <achille.salaun@nokia.com>
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

from collections           import defaultdict
from pybgl.property_map    import make_assoc_property_map
from pybgl.graph import \
    DirectedGraph, add_vertex, add_edge, edge, edges, num_edges, num_vertices, \
    out_degree, out_edges, remove_vertex, remove_edge, vertices

(u, v, w) = (0, 1, 2)

def make_g1() -> DirectedGraph:
    g1 = DirectedGraph()
    u = add_vertex(g1)
    v = add_vertex(g1)
    w = add_vertex(g1)
    return g1

def make_g2() -> DirectedGraph:
    g2 = make_g1()
    add_edge(u, v, g2)
    add_edge(u, v, g2) # parallel edge
    add_edge(u, w, g2)
    add_edge(v, w, g2)
    add_edge(w, w, g2)
    return g2

def test_directed_graph_num_vertices():
    g1 = make_g1()
    assert num_vertices(g1) == 3

def test_directed_graph_node_add_edge():
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

def test_directed_graph_add_vertex():
    g = make_g2()
    assert num_vertices(g) == 3
    assert num_edges(g) == 5

    # Add vertex x
    x = add_vertex(g)
    assert num_vertices(g) == 4

    # Add edge (v -> x)
    (e1, found) = edge(v, w, g)
    assert found
    (e2, added) = add_edge(v, x, g)
    assert num_edges(g) == 6
    assert {e for e in out_edges(v, g)} == {e1, e2}

def test_directed_graph_remove_edge():
    g = make_g2()
    assert num_edges(g) == 5

    (e, found) = edge(v, w, g)
    remove_edge(e, g)
    assert num_edges(g) == 4

    (e, found) = edge(w, w, g)
    remove_edge(e, g)
    assert num_edges(g) == 3

def test_directed_graph_iterators():
    g = make_g2()

    m = 0
    for u in vertices(g):
        m += 1
    assert m == num_vertices(g)
    assert m == 3

    n = 0
    for u in edges(g):
        n += 1
    assert n == num_edges(g)
    assert n == 5

def test_directed_graph_remove_vertex():
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
