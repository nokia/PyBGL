#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    BOTTOM, Automaton,
    graph_to_html,
    make_automaton,
    make_func_property_map
)


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
    assert G1.initial() == 0


def test_automaton_final():
    assert G1.finals() == {1}


def test_automaton_set_initial():
    g = Automaton()
    q = g.add_vertex()
    assert g.is_initial(q)
    g.set_initial(q)
    assert g.is_initial(q)
    g.set_initial(q, False)
    assert not g.is_initial(q)


def test_automaton_set_final():
    g = Automaton()
    q = g.add_vertex()
    assert not g.is_final(q)
    g.set_final(q)
    assert g.is_initial(q)
    g.set_final(q, False)
    assert not g.is_final(q)


def test_automaton_is_deterministic():
    assert G1.is_deterministic() is True


def test_automaton_is_finite():
    assert G1.is_finite() is True


def test_automaton_is_complete():
    assert G1.is_complete() is True
    assert G2.is_complete() is False
    assert G3.is_complete() is False
    assert G4.is_complete() is True
    assert G5.is_complete() is True


def test_automaton_accepts():
    assert G1.accepts("") is False
    assert G1.accepts("aaab") is True
    assert G1.accepts("aaaba") is False
    assert G1.accepts("aaabaa") is True
    assert G1.accepts("aaabaabb") is True


def test_automaton_sigma():
    assert G1.sigma(0) == {"a", "b"}
    assert G3.sigma(1) == set()
    assert G1.sigma(None) == set()


def test_automaton_alphabet():
    assert G1.alphabet() == {"a", "b"}
    assert G2.alphabet() == {"a", "b"}
    assert G3.alphabet() == {"a", "b"}


def test_automaton_add_vertex():
    g = Automaton(2)
    assert g.num_vertices() == 2
    assert g.num_edges() == 0
    q = g.add_vertex()
    assert isinstance(q, int)
    assert g.num_vertices() == 3
    assert g.num_edges() == 0


def test_automaton_add_edge():
    g = Automaton(3)
    a = 'a'
    b = 'b'
    c = 'c'
    (u, v, w) = (q for q in g.vertices())
    assert g.num_vertices() == 3
    assert g.num_edges() == 0
    assert g.delta(u, a) == BOTTOM
    assert g.delta(u, b) == BOTTOM
    assert g.delta(u, c) == BOTTOM

    (e, added) = g.add_edge(u, v, a)
    assert added
    assert g.source(e) == u
    assert g.target(e) == v
    assert g.label(e) == a
    assert g.num_edges() == 1
    assert g.delta(u, a) == v
    assert g.delta(u, b) == BOTTOM
    assert g.delta(u, c) == BOTTOM

    (e, added) = g.add_edge(u, v, b)
    assert added
    assert g.source(e) == u
    assert g.target(e) == v
    assert g.label(e) == b
    assert g.num_edges() == 2
    assert g.delta(u, a) == v
    assert g.delta(u, b) == v
    assert g.delta(u, c) == BOTTOM

    (e, added) = g.add_edge(u, w, c)
    assert added
    assert g.source(e) == u
    assert g.target(e) == w
    assert g.label(e) == c
    assert g.num_edges() == 3
    assert g.delta(u, a) == v
    assert g.delta(u, b) == v
    assert g.delta(u, c) == w


def test_remove_edge():
    transitions = [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 2, 'a'), (1, 1, 'b'),
        (2, 1, 'a'), (2, 1, 'b'),
    ]

    g = make_automaton(
        transitions, 0,
        make_func_property_map(lambda q: q in {1})
    )
    n = g.num_edges()
    assert n == 6
    for (u, v, a) in transitions:
        (e, found) = g.edge(u, v, a)
        assert found
        assert g.source(e) == u
        assert g.target(e) == v
        g.remove_edge(e)
        n -= 1
        assert g.num_edges() == n


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
    assert g.num_vertices() == 3
    assert g.num_edges() == 9

    g.remove_vertex(0)
    assert g.num_vertices() == 2
    assert g.num_edges() == 5

    g.remove_vertex(2)
    assert g.num_vertices() == 1
    assert g.num_edges() == 1

    g.remove_vertex(1)
    assert g.num_vertices() == 0
    assert g.num_edges() == 0


def test_automaton_graphviz():
    svg = graph_to_html(G1)
    assert isinstance(svg, str)


def test_make_automaton_constructor():
    class MyAutomaton(Automaton):
        pass
    g = make_automaton([])
    assert isinstance(g, Automaton)
    assert not isinstance(g, MyAutomaton)
    g = make_automaton([], Constructor=MyAutomaton)
    assert isinstance(g, Automaton)
    assert isinstance(g, MyAutomaton)
