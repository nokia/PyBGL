#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.graphviz import graph_to_html
from pybgl.property_map import make_func_property_map
from pybgl.incidence_automaton import *

G1 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 2, 'a'), (1, 1, 'b'),
        (2, 1, 'a'), (2, 1, 'b'),
    ], 0, make_func_property_map(lambda q: q in {1})
)

G2 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
    ], 0, make_func_property_map(lambda q: q in {1})
)

G3 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
    ], 0, make_func_property_map(lambda q: False)
)

G4 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 1, 'b'), (1, 0, 'a')
    ], 0, make_func_property_map(lambda q: q in {1})
)

G5 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 1, 'b'), (1, 0, 'a')
    ], 0, make_func_property_map(lambda q: False)
)

def test_incidence_automaton_initial():
    assert initial(G1) == 0

def test_incidence_automaton_final():
    assert finals(G1) == {1}

def test_incidence_automaton_is_deterministic():
    assert is_deterministic(G1) is True

def test_incidence_automaton_is_finite():
    assert is_finite(G1) is True

def test_incidence_automaton_is_complete():
    assert is_complete(G1) is True
    assert is_complete(G2) is False
    assert is_complete(G3) is False
    assert is_complete(G4) is True
    assert is_complete(G5) is True

def test_incidence_automaton_accepts():
    assert accepts("", G1) is False
    assert accepts("aaab", G1) is True
    assert accepts("aaaba", G1) is False
    assert accepts("aaabaa", G1) is True
    assert accepts("aaabaabb", G1) is True

def test_incidence_automaton_sigma():
    assert sigma(0, G1) == {"a", "b"}
    assert sigma(1, G3) == set()
    assert sigma(None, G1) == set()

def test_incidence_automaton_alphabet():
    assert alphabet(G1) == {"a", "b"}
    assert alphabet(G2) == {"a", "b"}
    assert alphabet(G3) == {"a", "b"}

def test_incidence_automaton_add_vertex():
    g = IncidenceAutomaton(2)
    assert num_vertices(g) == 2
    assert num_edges(g) == 0
    q = add_vertex(g)
    assert num_vertices(g) == 3
    assert num_edges(g) == 0

def test_incidence_automaton_add_edge():
    g = IncidenceAutomaton(3)
    a = 'a'
    b = 'b'
    c = 'c'
    (u, v, w) = (q for q in vertices(g))
    assert num_vertices(g) == 3
    assert num_edges(g) == 0
    assert delta(u, a, g) == BOTTOM
    assert delta(u, b, g) == BOTTOM
    assert delta(u, c, g) == BOTTOM

    (e, added) = add_edge(u, v, a, g)
    assert added
    assert source(e, g) == u
    assert target(e, g) == v
    assert label(e, g) == a
    assert num_edges(g) == 1
    assert delta(u, a, g) == v
    assert delta(u, b, g) == BOTTOM
    assert delta(u, c, g) == BOTTOM

    (e, added) = add_edge(u, v, b, g)
    assert added
    assert source(e, g) == u
    assert target(e, g) == v
    assert label(e, g) == b
    assert num_edges(g) == 2
    assert delta(u, a, g) == v
    assert delta(u, b, g) == v
    assert delta(u, c, g) == BOTTOM

    (e, added) = add_edge(u, w, c, g)
    assert added
    assert source(e, g) == u
    assert target(e, g) == w
    assert label(e, g) == c
    assert num_edges(g) == 3
    assert delta(u, a, g) == v
    assert delta(u, b, g) == v
    assert delta(u, c, g) == w

def test_remove_edge():
    transitions = [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 2, 'a'), (1, 1, 'b'),
        (2, 1, 'a'), (2, 1, 'b'),
    ]

    g = make_incidence_automaton(transitions, 0, make_func_property_map(lambda q: q in {1}))
    n = num_edges(g)
    assert n == 6
    for (u, v, a) in transitions:
        (e, found) = edge(u, v, a, g)
        assert found
        assert source(e, g) == u
        assert target(e, g) == v
        du = out_degree(u, g)
        assert isinstance(du, int)
        dv = in_degree(v, g)
        assert isinstance(dv, int)
        remove_edge(e, g)
        assert out_degree(u, g) == du - 1
        assert in_degree(v, g) == dv - 1
        n -= 1
        assert num_edges(g) == n

def test_incidence_automaton_remove_vertex():
    g = make_incidence_automaton([
            (0, 0, 'a'), (0, 1, 'b'),
            (1, 2, 'a'), (1, 1, 'b'),
            (2, 1, 'a'), (2, 1, 'b'),
            # Add loop and cycles
            (0, 0, 'c'),
            (1, 0, 'c'),
            (2, 2, 'c')
        ], 0, make_func_property_map(lambda q: q in {1})
    )
    assert num_vertices(g) == 3
    assert num_edges(g) == 9

    print("remove_vertex(0)")
    remove_vertex(0, g)
    assert num_vertices(g) == 2
    assert num_edges(g) == 5

    print("remove_vertex(2)")
    remove_vertex(2, g)
    assert num_vertices(g) == 1
    assert num_edges(g) == 1

    print("remove_vertex(1)")
    remove_vertex(1, g)
    assert num_vertices(g) == 0
    assert num_edges(g) == 0

def test_incidence_automaton_graphviz():
    svg = graph_to_html(G1)

def test_incidence_automaton():
    print("Testing num_vertices")
    g = IncidenceAutomaton(2)
    u = 0
    v = 1
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    assert num_vertices(g) == 2

    # e1: (u, v, a)
    # e2: (u, v, b)
    # e3: (u, w, c)
    # e4: (u, w, d)
    # e5: (w, v, a)
    # e6: (w, v, b)

    print("Testing edge (1)")
    (e1, added1) = add_edge(u, v, a, g)
    assert added1
    (e, found) = edge(u, v, a, g)
    assert found
    assert e == e1

    print("Testing *_degree and *_edges (1)")
    assert {e for e in in_edges(v, g)} == {e1}
    assert {e for e in out_edges(u, g)} == {e1}
    assert out_degree(u, g) == 1
    assert in_degree(v, g) == 1
    assert num_edges(g) == 1

    print("Testing edge (2)")
    (e, found) = edge(u, v, a, g)
    assert found
    assert e == e1

    print("Testing *_degree and *_edges (2)")
    (e2, added2) = add_edge(u, v, b, g)
    assert added2
    assert {e for e in in_edges(v, g)} == {e1, e2}
    assert {e for e in out_edges(u, g)} == {e1, e2}
    assert out_degree(u, g) == 2
    assert in_degree(v, g) == 2
    assert num_edges(g) == 2

    print("Testing add_vertex")
    w = add_vertex(g)
    assert num_vertices(g) == 3
    (e3, added3) = add_edge(u, w, c, g)
    (e4, added4) = add_edge(u, w, d, g)
    assert {e for e in out_edges(u, g)} == {e1, e2, e3, e4}
    assert {e for e in in_edges(w, g)} == {e3, e4}
    assert num_edges(g) == 4

    (e5, added3) = add_edge(w, v, a, g)
    (e6, added4) = add_edge(w, v, b, g)
    assert {e for e in out_edges(w, g)} == {e5, e6}
    assert {e for e in in_edges(v, g)} == {e1, e2, e5, e6}
    assert num_edges(g) == 6

    print("Testing remove_edge(%s)" % e1)
    remove_edge(e1, g)
    assert num_edges(g) == 5
    assert {e for e in out_edges(u, g)} == {e2, e3, e4}
    assert {e for e in in_edges(v, g)} == {e2, e5, e6}
    (e, found) = edge(u, v, a, g)
    assert not found
    (e, found) = edge(u, v, b, g)
    assert found
    assert e == e2

    print("Testing remove_vertex(%s)" % u)
    remove_vertex(u, g)
    assert num_vertices(g) == 2
    assert num_edges(g) == 2
    assert {e for e in out_edges(w, g)} == {e5, e6}
    assert {e for e in in_edges(v, g)} == {e5, e6}
