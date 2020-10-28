#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from pybgl.graphviz        import graph_to_html
from pybgl.property_map    import make_assoc_property_map
from pybgl.node_automaton  import *

(u, v, w) = (0, 1, 2)

def make_g1() -> NodeAutomaton:
    g1 = NodeAutomaton()
    u = add_vertex(None, g1)
    v = add_vertex("a", g1)
    w = add_vertex("b", g1)
    return g1

def make_g2() -> NodeAutomaton:
    g2 = make_g1()
    add_edge(u, v, g2)
    add_edge(u, w, g2)
    add_edge(v, w, g2)
    return g2

def test_alphabet():
    g1 = make_g1()
    assert alphabet(g1) == {"a", "b"}
    g2 = make_g2()
    assert alphabet(g2) == {"a", "b"}

def test_sigma():
    g = make_g2()
    assert sigma(0, g) == {"a", "b"}
    assert sigma(1, g) == {"b"}
    assert sigma(2, g) == set()

def test_node_automaton_edge():
    g = make_g1()
    (e, added) = add_edge(u, v, g)
    assert e is not None
    assert added
    assert source(e, g) == u
    assert target(e, g) == v
    assert label(e, g) == "a"
    assert symbol(v, g) == "a"

def test_node_automaton_num_vertices():
    g = make_g2()
    assert num_vertices(g) == 3
    m = 0
    for q in vertices(g):
        m += 1
    assert m == 3

def test_node_automaton_num_edges():
    g = make_g2()
    assert num_edges(g) == 3
    n = 0
    for e in edges(g):
        n += 1
    assert n == 3

def test_node_automaton_symbol():
    g1 = make_g1()
    assert symbol(u, g1) == None
    assert symbol(v, g1) == "a"
    assert symbol(w, g1) == "b"

def test_node_automaton_pmap_vlabel():
    map_vlabel = {u : None, v : "a", w : "b"}
    g = NodeAutomaton(3, pmap_vsymbol = make_assoc_property_map(map_vlabel))
    assert num_vertices(g) == 3
    print(g.adjacencies)
    assert symbol(u, g) == None
    assert symbol(v, g) == "a"
    assert symbol(w, g) == "b"
    assert num_edges(g) == 0
    add_edge(u, v, g)
    assert num_edges(g) == 1
    add_edge(u, w, g)
    assert num_edges(g) == 2

def test_node_automaton_add_edge():
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

def test_node_automaton_delta():
    g2 = make_g2()
    assert delta(u, "a", g2) == v
    assert delta(u, "b", g2) == w
    assert delta(v, "a", g2) == BOTTOM
    assert delta(v, "b", g2) == w
    assert delta(w, "a", g2) == BOTTOM
    assert delta(w, "b", g2) == BOTTOM

def test_node_automaton_add_vertex():
    g = make_g2()
    assert num_vertices(g) == 3
    assert num_edges(g) == 3

    # Add node x
    x = add_vertex("c", g)
    assert num_vertices(g) == 4
    assert symbol(x, g) == "c"

    # Add edge (v -> x)
    (e1, found) = edge(v, w, g)
    assert found
    (e2, added) = add_edge(v, x, g)
    assert label(e2, g) == "c"
    assert num_edges(g) == 4
    assert {e for e in out_edges(v, g)} == {e1, e2}

def test_node_automaton_remove_edge():
    g = make_g2()
    (e, found) = edge(v, w, g)
    assert num_edges(g) == 3
    assert delta(u, "a", g) == v
    assert delta(u, "b", g) == w
    assert delta(v, "b", g) == w

    remove_edge(e, g)
    assert num_edges(g) == 2
    assert delta(u, "a", g) == v
    assert delta(u, "b", g) == w
    assert delta(v, "b", g) == BOTTOM

def test_node_automaton_remove_vertex():
    g = make_g2()
    assert num_vertices(g) == 3
    assert num_edges(g) == 3
    assert delta(u, "a", g) == v
    assert delta(u, "b", g) == w
    assert delta(v, "b", g) == w

    remove_vertex(v, g)
    assert num_vertices(g) == 2
    assert num_edges(g) == 1
    assert delta(u, "a", g) == BOTTOM
    assert delta(u, "b", g) == w

def test_node_automaton_graphviz():
    g = make_g2()
    svg = graph_to_html(g)
