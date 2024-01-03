#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    BOTTOM,
    IncidenceAutomaton,
    graph_to_html,
    make_func_property_map,
    make_incidence_automaton,
)

G1 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 2, 'a'), (1, 1, 'b'),
        (2, 1, 'a'), (2, 1, 'b'),
    ],
    0,
    make_func_property_map(lambda q: q in {1})
)

G2 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
    ],
    0,
    make_func_property_map(lambda q: q in {1})
)

G3 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
    ],
    0,
    make_func_property_map(lambda q: False)
)

G4 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 1, 'b'), (1, 0, 'a')
    ],
    0,
    make_func_property_map(lambda q: q in {1})
)

G5 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 1, 'b'), (1, 0, 'a')
    ],
    0,
    make_func_property_map(lambda q: False)
)


def test_incidence_automaton_initial():
    assert G1.initial() == 0


def test_incidence_automaton_final():
    assert G1.finals() == {1}


def test_incidence_automaton_is_deterministic():
    assert G1.is_deterministic() is True


def test_incidence_automaton_is_finite():
    assert G1.is_finite() is True


def test_incidence_automaton_is_complete():
    assert G1.is_complete() is True
    assert G2.is_complete() is False
    assert G3.is_complete() is False
    assert G4.is_complete() is True
    assert G5.is_complete() is True


def test_incidence_automaton_accepts():
    assert G1.accepts("") is False
    assert G1.accepts("aaab") is True
    assert G1.accepts("aaaba") is False
    assert G1.accepts("aaabaa") is True
    assert G1.accepts("aaabaabb") is True


def test_incidence_automaton_sigma():
    assert G1.sigma(0) == {"a", "b"}
    assert G3.sigma(1) == set()
    assert G1.sigma(None) == set()


def test_incidence_automaton_alphabet():
    assert G1.alphabet() == {"a", "b"}
    assert G2.alphabet() == {"a", "b"}
    assert G3.alphabet() == {"a", "b"}


def test_incidence_automaton_add_vertex():
    g = IncidenceAutomaton(2)
    assert g.num_vertices() == 2
    assert g.num_edges() == 0
    _ = g.add_vertex()
    assert g.num_vertices() == 3
    assert g.num_edges() == 0


def test_incidence_automaton_add_edge():
    g = IncidenceAutomaton(3)
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

    g = make_incidence_automaton(
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
        du = g.out_degree(u)
        assert isinstance(du, int)
        dv = g.in_degree(v)
        assert isinstance(dv, int)
        g.remove_edge(e)
        assert g.out_degree(u) == du - 1
        assert g.in_degree(v) == dv - 1
        n -= 1
        assert g.num_edges() == n


def test_incidence_automaton_remove_vertex(debug: bool = False):
    if not debug:
        def print(*args, **kwargs):
            pass
    g = make_incidence_automaton([
            (0, 0, 'a'), (0, 1, 'b'),
            (1, 2, 'a'), (1, 1, 'b'),
            (2, 1, 'a'), (2, 1, 'b'),
            # Add loop and cycles
            (0, 0, 'c'),
            (1, 0, 'c'),
            (2, 2, 'c')
        ],
        0,
        make_func_property_map(lambda q: q in {1})
    )
    assert g.num_vertices() == 3
    assert g.num_edges() == 9

    print("remove_vertex(0)")
    g.remove_vertex(0)
    assert g.num_vertices() == 2
    assert g.num_edges() == 5

    print("remove_vertex(2)")
    g.remove_vertex(2)
    assert g.num_vertices() == 1
    assert g.num_edges() == 1

    print("remove_vertex(1)")
    g.remove_vertex(1)
    assert g.num_vertices() == 0
    assert g.num_edges() == 0


def test_incidence_automaton_graphviz():
    _ = graph_to_html(G1)


def test_incidence_automaton(debug: bool = False):
    if not debug:
        def print(*args, **kwargs):
            pass

    print("Testing num_vertices")
    g = IncidenceAutomaton(2)
    u = 0
    v = 1
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    assert g.num_vertices() == 2

    # e1: (u, v, a)
    # e2: (u, v, b)
    # e3: (u, w, c)
    # e4: (u, w, d)
    # e5: (w, v, a)
    # e6: (w, v, b)

    print("Testing edge (1)")
    (e1, added1) = g.add_edge(u, v, a)
    assert added1
    (e, found) = g.edge(u, v, a)
    assert found
    assert e == e1

    print("Testing *_degree and *_edges (1)")
    assert {e for e in g.in_edges(v)} == {e1}
    assert {e for e in g.out_edges(u)} == {e1}
    assert g.out_degree(u) == 1
    assert g.in_degree(v) == 1
    assert g.num_edges() == 1

    print("Testing edge (2)")
    (e, found) = g.edge(u, v, a)
    assert found
    assert e == e1

    print("Testing *_degree and *_edges (2)")
    (e2, added2) = g.add_edge(u, v, b)
    assert added2
    assert {e for e in g.in_edges(v)} == {e1, e2}
    assert {e for e in g.out_edges(u)} == {e1, e2}
    assert g.out_degree(u) == 2
    assert g.in_degree(v) == 2
    assert g.num_edges() == 2

    print("Testing add_vertex")
    w = g.add_vertex()
    assert g.num_vertices() == 3
    (e3, added3) = g.add_edge(u, w, c)
    (e4, added4) = g.add_edge(u, w, d)
    assert {e for e in g.out_edges(u)} == {e1, e2, e3, e4}
    assert {e for e in g.in_edges(w)} == {e3, e4}
    assert g.num_edges() == 4

    (e5, added3) = g.add_edge(w, v, a)
    (e6, added4) = g.add_edge(w, v, b)
    assert {e for e in g.out_edges(w)} == {e5, e6}
    assert {e for e in g.in_edges(v)} == {e1, e2, e5, e6}
    assert g.num_edges() == 6

    print("Testing remove_edge(%s)" % e1)
    g.remove_edge(e1)
    assert g.num_edges() == 5
    assert {e for e in g.out_edges(u)} == {e2, e3, e4}
    assert {e for e in g.in_edges(v)} == {e2, e5, e6}
    (e, found) = g.edge(u, v, a)
    assert not found
    (e, found) = g.edge(u, v, b)
    assert found
    assert e == e2

    print("Testing remove_vertex(%s)" % u)
    g.remove_vertex(u)
    assert g.num_vertices() == 2
    assert g.num_edges() == 2
    assert {e for e in g.out_edges(w)} == {e5, e6}
    assert {e for e in g.in_edges(v)} == {e5, e6}
