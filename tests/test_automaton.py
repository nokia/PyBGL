#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.automaton import *
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

def test_automaton_initial():
    assert initial(G1) == 0

def test_automaton_final():
    assert finals(G1) == {1}

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

def test_automaton_is_deterministic():
    assert is_deterministic(G1) is True

def test_automaton_is_finite():
    assert is_finite(G1) is True

def test_automaton_is_complete():
    assert is_complete(G1) is True
    assert is_complete(G2) is False
    assert is_complete(G3) is False
    assert is_complete(G4) is True
    assert is_complete(G5) is True

def test_automaton_accepts():
    assert accepts("", G1) is False
    assert accepts("aaab", G1) is True
    assert accepts("aaaba", G1) is False
    assert accepts("aaabaa", G1) is True
    assert accepts("aaabaabb", G1) is True

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
    assert isinstance(q, int)
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

    remove_vertex(0, g)
    assert num_vertices(g) == 2
    assert num_edges(g) == 5

    remove_vertex(2, g)
    assert num_vertices(g) == 1
    assert num_edges(g) == 1

    remove_vertex(1, g)
    assert num_vertices(g) == 0
    assert num_edges(g) == 0

def test_automaton_graphviz():
    svg = graph_to_html(G1)
    assert isinstance(svg, str)
