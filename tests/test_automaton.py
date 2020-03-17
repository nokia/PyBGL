#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from pybgl.automaton import \
    BOTTOM, Automaton, accepts, add_edge, add_vertex, alphabet, delta, edge, \
    final, initial, is_complete, is_deterministic, is_final, is_finite, is_initial, \
    is_minimal, label, make_automaton, num_edges, num_vertices, set_initial, set_final, sigma, \
    remove_edge, remove_vertex, source, target, vertices, make_minimal_automaton
from pybgl.graphviz import graph_to_html
from pybgl.property_map import make_func_property_map

G1 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 2, 'a'), (1, 1, 'b'),
        (2, 1, 'a'), (2, 1, 'b'),
    ], 0,
    make_func_property_map(lambda q: q in {1})
)

G2 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
    ], 0,
    make_func_property_map(lambda q: q in {1})
)

G3 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
    ], 0,
    make_func_property_map(lambda q: False)
)

G4 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 1, 'b'), (1, 0, 'a')
    ], 0,
    make_func_property_map(lambda q: q in {1})
)

G5 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 1, 'b'), (1, 0, 'a')
    ], 0,
    make_func_property_map(lambda q: False)
)

G6 = make_automaton(
    [
        (0, 1, 'a'), (0, 2, 'b'),
        (1, 1, 'a'), (1, 3, 'b'),
        (2, 1, 'a'), (2, 2, 'b'),
        (3, 1, 'a'), (3, 4, 'b'),
        (4, 1, 'a'), (4, 2, 'b')
    ], 0,
    make_func_property_map(lambda q: q in {4})
)

G7 = make_automaton(
    [
        (0, 1, 'a'), (0, 2, 'b'),
        (1, 0, 'a'), (1, 3, 'b'),
        (2, 4, 'a'), (2, 5, 'b'),
        (3, 4, 'a'), (3, 5, 'b'),
        (4, 4, 'a'), (4, 5, 'b'),
        (5, 5, 'a'), (5, 5, 'b')
    ], 0, make_func_property_map(lambda q: q in {2, 3, 4})
)

G8 = make_automaton(
    [
        (0, 1, 'a'),
        (1, 2, 'a'),
        (2, 3, 'a'),
        (3, 4, 'a'),
        (4, 5, 'a'),
        (5, 6, 'a'),
        (6, 7, 'a'),
        (7, 8, 'a'),
        (8, 9, 'a'),
        (9, 10, 'a'),
        (10, 11, 'a'),
        (11, 12, 'a'),
        (12, 11, 'a')
    ], 0, make_func_property_map(lambda q: q in {0, 2, 4, 6, 8, 10, 12})
)

G9 = make_automaton(
    [
        (0, 1, 'a'),
        (1, 2, 'a'),
        (2, 3, 'a'),
        (3, 4, 'a'),
        (4, 5, 'a'),
        (5, 6, 'a'),
        (6, 7, 'a'),
        (7, 8, 'a'),
        (8, 9, 'a'),
        (9, 10, 'a'),
        (10, 11, 'a'),
        (11, 12, 'a'),
        (12, 12, 'a')
    ], 0, make_func_property_map(lambda q: q in {0, 2, 4, 6, 8, 10, 12})
)

def test_automaton_initial():
    assert initial(G1) == 0

def test_automaton_final():
    assert final(G1) == {1}

def test_automaton_set_initial():
    g = Automaton()
    q = add_vertex(g)
    assert is_initial(q, g)
    set_initial(q, g)
    assert is_initial(q, g)
    set_initial(q, g, False)
    assert not is_initial(q, g)

def test_automaton_set_final():
    g = Automaton()
    q = add_vertex(g)
    assert not is_final(q, g)
    set_final(q, g)
    assert is_initial(q, g)
    set_final(q, g, False)
    assert not is_final(q, g)

def test_automaton_alphabet():
    assert alphabet(G1) == {"a", "b"}

def test_automaton_is_deterministic():
    assert is_deterministic(G1) == True

def test_automaton_is_finite():
    assert is_finite(G1) == True

def test_automaton_is_complete():
    assert is_complete(G1) == True
    assert is_complete(G2) == False
    assert is_complete(G3) == False
    assert is_complete(G4) == True
    assert is_complete(G5) == True

def test_automaton_accepts():
    assert accepts("", G1) == False
    assert accepts("aaab", G1) == True
    assert accepts("aaaba", G1) == False
    assert accepts("aaabaa", G1) == True
    assert accepts("aaabaabb", G1) == True

def test_automaton_sigma():
    assert sigma(0, G1) == {"a", "b"}
    assert sigma(1, G3) == set()
    assert sigma(None, G1) == set()

def test_automaton_alphabet():
    assert alphabet(G1) == {"a", "b"}
    assert alphabet(G2) == {"a", "b"}
    assert alphabet(G3) == {"a", "b"}

def test_automaton_add_vertex():
    g = Automaton(2)
    assert num_vertices(g) == 2
    assert num_edges(g) == 0
    q = add_vertex(g)
    assert num_vertices(g) == 3
    assert num_edges(g) == 0

def test_automaton_add_edge():
    g = Automaton(3)
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

    g = make_automaton(transitions, 0, make_func_property_map(lambda q: q in {1}))
    n = num_edges(g)
    assert n == 6
    for (u, v, a) in transitions:
        (e, found) = edge(u, v, a, g)
        assert found
        assert source(e, g) == u
        assert target(e, g) == v
        remove_edge(e, g)
        n -= 1
        assert num_edges(g) == n

def test_automaton_remove_vertex():
    g = make_automaton([
            (0, 0, 'a'), (0, 1, 'b'),
            (1, 2, 'a'), (1, 1, 'b'),
            (2, 1, 'a'), (2, 1, 'b'),
            # Add loop and cycles
            (0, 0, 'c'),
            (1, 0, 'c'),
            (2, 2, 'c')
        ], 0,
        make_func_property_map(lambda q: q in {1})
    )
    assert num_vertices(g) == 3
    assert num_edges(g) == 9
    print(g.adjacencies)

    print("remove_vertex(0)")
    remove_vertex(0, g)
    print(g.adjacencies)
    assert num_vertices(g) == 2
    assert num_edges(g) == 5

    print("remove_vertex(2)")
    remove_vertex(2, g)
    print(g.adjacencies)
    assert num_vertices(g) == 1
    assert num_edges(g) == 1

    print("remove_vertex(1)")
    remove_vertex(1, g)
    print(g.adjacencies)
    assert num_vertices(g) == 0
    assert num_edges(g) == 0

def test_automaton_graphviz():
    svg = graph_to_html(G1)

def test_automaton_make_minimal_automaton():
    min_G6 = make_minimal_automaton(G6)
    assert num_vertices(min_G6) == 4
    assert num_edges(min_G6) == 8
    min_G7 = make_minimal_automaton(G7)
    assert num_vertices(min_G7) == 3
    assert num_edges(min_G7) == 6
    min_G8 = make_minimal_automaton(G8)
    assert num_vertices(min_G8) == 2
    assert num_edges(min_G8) == 2
    min_G9 = make_minimal_automaton(G9)
    assert num_vertices(min_G9) == 13
    assert num_edges(min_G9) == 13
