#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pybgl.graphviz import graph_to_html
from pybgl.property_map import make_assoc_property_map, make_func_property_map
from pybgl.incidence_node_automaton import *


(u, v, w) = (0, 1, 2)


def make_g1() -> IncidenceNodeAutomaton:
    g1 = IncidenceNodeAutomaton()
    add_vertex(None, g1)
    add_vertex("a", g1)
    add_vertex("b", g1)
    return g1


def make_g2() -> IncidenceNodeAutomaton:
    g2 = make_g1()
    add_edge(u, v, g2)
    add_edge(u, w, g2)
    add_edge(v, w, g2)
    return g2


def test_incidence_node_automaton_in_degree():
    g = make_g2()
    assert in_degree(u, g) == 0
    assert in_degree(v, g) == 1
    assert in_degree(w, g) == 2
    add_edge(u, v, g)
    assert in_degree(u, g) == 0
    assert in_degree(v, g) == 1 # Because NodeAutomaton remains deterministic
    add_edge(u, u, g)
    assert in_degree(u, g) == 1


def test_incidence_node_automaton_determinism():
    g = make_g1()
    (e, added) = add_edge(u, v, g)
    assert added
    (e, added) = add_edge(u, v, g)
    assert not added


def test_incidence_node_automaton_in_edges():
    g = make_g1()
    (e0, added) = add_edge(u, u, g)
    (e1, added) = add_edge(u, v, g)
    (e2, added) = add_edge(u, w, g)
    (e3, added) = add_edge(v, w, g)
    assert {e for e in in_edges(u, g)} == {e0}
    assert {e for e in in_edges(v, g)} == {e1}
    assert {e for e in in_edges(w, g)} == {e2, e3}

def test_incidence_node_automaton_edge():
    g = make_g1()
    (e, added) = add_edge(u, v, g)
    assert e is not None
    assert added
    assert source(e, g) == u
    assert target(e, g) == v
    assert label(e, g) == "a"
    assert symbol(v, g) == "a"


def test_incidence_node_automaton_num_vertices():
    g = make_g2()
    assert num_vertices(g) == 3
    m = 0
    for q in vertices(g):
        m += 1
    assert m == 3


def test_incidence_node_automaton_num_edges():
    g = make_g2()
    assert num_edges(g) == 3
    n = 0
    for e in edges(g):
        n += 1
    assert n == 3


def test_incidence_node_automaton_symbol():
    g1 = make_g1()
    assert symbol(u, g1) is None
    assert symbol(v, g1) == "a"
    assert symbol(w, g1) == "b"


def test_incidence_node_automaton_pmap_vlabel():
    map_vlabel = defaultdict(lambda: None)
    map_vlabel[v] = "a"
    map_vlabel[w] = "b"
    g = IncidenceNodeAutomaton(3, pmap_vsymbol=make_assoc_property_map(map_vlabel))
    assert num_vertices(g) == 3
    print(g.adjacencies)
    assert symbol(u, g) is None, f"Got {symbol(u, g)}"
    assert symbol(v, g) == "a"
    assert symbol(w, g) == "b"
    assert num_edges(g) == 0
    add_edge(u, v, g)
    assert num_edges(g) == 1
    add_edge(u, w, g)
    assert num_edges(g) == 2


def test_incidence_node_automaton_add_edge():
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


def test_incidence_node_automaton_delta():
    g2 = make_g2()
    assert delta(u, "a", g2) == v
    assert delta(u, "b", g2) == w
    assert delta(v, "a", g2) == BOTTOM
    assert delta(v, "b", g2) == w
    assert delta(w, "a", g2) == BOTTOM
    assert delta(w, "b", g2) == BOTTOM


def test_incidence_node_automaton_add_vertex():
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


def test_incidence_node_automaton_remove_edge():
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


def test_incidence_node_automaton_remove_vertex():
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


def test_incidence_node_automaton_graphviz():
    g = make_g2()
    svg = graph_to_html(g)


def test_make_incidence_node_automaton():
    map_vlabel = defaultdict(
        lambda: None,
        {
            0: None,
            1: "c",
            2: "b",
            3: "a",  # Will be aggregated with 5
            4: "b",
            5: "a",  # Will be aggregated with 3
        }
    )
    edges = [
        (0, 1),
        (2, 1),
        (3, 1),
        (4, 1),
        (0, 5)
    ]
    g = make_incidence_node_automaton(
        edges,
        pmap_vlabel=make_assoc_property_map(map_vlabel)
    )
    assert isinstance(g, IncidenceNodeAutomaton)
    for u in g.vertices():
        assert g.symbol(u) == map_vlabel[u]
    obtained = {
        (g.source(e), g.target(e))
        for e in g.edges()
    }
    assert obtained == set(edges)


def test_make_incidence_node_automaton_finals():
    g = make_incidence_node_automaton(
        [(0, 1), (0, 2), (1, 2)],
        q0n = 0,
        pmap_vlabel=make_assoc_property_map(
            defaultdict(
                lambda: None,
                {1: "a", 2: "b"}
            )
        ),
        pmap_vfinal=make_func_property_map(lambda u: u in {0, 2})
    )
    assert num_vertices(g) == 3
    assert num_edges(g) == 3
    for u in vertices(g):
        assert is_initial(u, g) == (u == 0)
        assert is_final(u, g) == (u in {0, 2})
    assert symbol(0, g) is None
    assert symbol(1, g) == "a"
    assert symbol(2, g) == "b"
