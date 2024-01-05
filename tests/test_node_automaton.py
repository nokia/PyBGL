#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pybgl import (
    BOTTOM, NodeAutomaton,
    graph_to_html,
    make_assoc_property_map,
    make_func_property_map,
    make_node_automaton
)


(u, v, w) = (0, 1, 2)


def make_g1() -> NodeAutomaton:
    g1 = NodeAutomaton()
    g1.add_vertex(None)
    g1.add_vertex("a")
    g1.add_vertex("b")
    return g1


def make_g2() -> NodeAutomaton:
    g2 = make_g1()
    g2.add_edge(u, v)
    g2.add_edge(u, w)
    g2.add_edge(v, w)
    return g2


def test_alphabet():
    g1 = make_g1()
    assert g1.alphabet() == {"a", "b"}
    g2 = make_g2()
    assert g2.alphabet() == {"a", "b"}


def test_sigma():
    g = make_g2()
    assert g.sigma(0) == {"a", "b"}
    assert g.sigma(1) == {"b"}
    assert g.sigma(2) == set()


def test_node_automaton_edge():
    g = make_g1()
    (e, added) = g.add_edge(u, v)
    assert e is not None
    assert added
    assert g.source(e) == u
    assert g.target(e) == v
    assert g.label(e) == "a"
    assert g.symbol(v) == "a"


def test_node_automaton_num_vertices():
    g = make_g2()
    assert g.num_vertices() == 3
    m = 0
    for _ in g.vertices():
        m += 1
    assert m == 3


def test_node_automaton_num_edges():
    g = make_g2()
    assert g.num_edges() == 3
    n = 0
    for _ in g.edges():
        n += 1
    assert n == 3


def test_node_automaton_symbol():
    g1 = make_g1()
    assert g1.symbol(u) is None
    assert g1.symbol(v) == "a"
    assert g1.symbol(w) == "b"


def test_node_automaton_pmap_vlabel():
    map_vlabel = defaultdict(lambda: None, {v: "a", w: "b"})
    g = NodeAutomaton(3, pmap_vsymbol=make_assoc_property_map(map_vlabel))
    assert g.num_vertices() == 3
    # print(g.adjacencies)
    assert g.symbol(u) is None
    assert g.symbol(v) == "a"
    assert g.symbol(w) == "b"
    assert g.num_edges() == 0
    g.add_edge(u, v)
    assert g.num_edges() == 1
    g.add_edge(u, w)
    assert g.num_edges() == 2


def test_node_automaton_add_edge():
    # Make graph
    g = make_g1()
    assert g.out_degree(u) == 0
    assert g.num_edges() == 0

    # Add e1
    (e1, added1) = g.add_edge(u, v)
    assert added1
    (e, found) = g.edge(u, v)
    assert found
    assert e == e1
    assert g.out_degree(u) == 1
    assert g.num_edges() == 1

    # No arc
    (e, found) = g.edge(u, w)
    assert not found
    assert {e for e in g.out_edges(u)} == {e1}

    # Add e2
    (e2, added2) = g.add_edge(u, w)
    assert added2
    assert {e for e in g.out_edges(u)} == {e1, e2}
    assert g.out_degree(u) == 2
    assert g.num_edges() == 2


def test_node_automaton_delta():
    g2 = make_g2()
    assert g2.delta(u, "a") == v
    assert g2.delta(u, "b") == w
    assert g2.delta(v, "a") == BOTTOM
    assert g2.delta(v, "b") == w
    assert g2.delta(w, "a") == BOTTOM
    assert g2.delta(w, "b") == BOTTOM


def test_node_automaton_add_vertex():
    g = make_g2()
    assert g.num_vertices() == 3
    assert g.num_edges() == 3

    # Add node x
    x = g.add_vertex("c")
    assert g.num_vertices() == 4
    assert g.symbol(x) == "c"

    # Add edge (v -> x)
    (e1, found) = g.edge(v, w)
    assert found
    (e2, added) = g.add_edge(v, x)
    assert g.label(e2) == "c"
    assert g.num_edges() == 4
    assert {e for e in g.out_edges(v)} == {e1, e2}


def test_node_automaton_remove_edge():
    g = make_g2()
    (e, found) = g.edge(v, w)
    assert g.num_edges() == 3
    assert g.delta(u, "a") == v
    assert g.delta(u, "b") == w
    assert g.delta(v, "b") == w

    g.remove_edge(e)
    assert g.num_edges() == 2
    assert g.delta(u, "a") == v
    assert g.delta(u, "b") == w
    assert g.delta(v, "b") == BOTTOM


def test_node_automaton_remove_vertex():
    g = make_g2()
    assert g.num_vertices() == 3
    assert g.num_edges() == 3
    assert g.delta(u, "a") == v
    assert g.delta(u, "b") == w
    assert g.delta(v, "b") == w

    g.remove_vertex(v)
    assert g.num_vertices() == 2
    assert g.num_edges() == 1
    assert g.delta(u, "a") == BOTTOM
    assert g.delta(u, "b") == w


def test_node_automaton_graphviz():
    g = make_g2()
    svg = graph_to_html(g)
    assert isinstance(svg, str)


def test_make_node_automaton():
    class MyNodeAutomaton(NodeAutomaton):
        pass
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
    g = make_node_automaton(
        edges,
        pmap_vlabel=make_assoc_property_map(map_vlabel),
        Constructor=MyNodeAutomaton
    )
    assert isinstance(g, MyNodeAutomaton)
    for u in g.vertices():
        assert g.symbol(u) == map_vlabel[u]
    obtained = {
        (g.source(e), g.target(e))
        for e in g.edges()
    }
    assert obtained == set(edges)


def test_make_incidence_node_automaton_finals():
    g = make_node_automaton(
        [(0, 1), (0, 2), (1, 2)],
        q0n=0,
        pmap_vlabel=make_assoc_property_map(
            defaultdict(
                lambda: None,
                {1: "a", 2: "b"}
            )
        ),
        pmap_vfinal=make_func_property_map(lambda u: u in {0, 2})
    )
    assert g.num_vertices() == 3
    assert g.num_edges() == 3
    for u in g.vertices():
        assert g.is_initial(u) == (u == 0)
        assert g.is_final(u) == (u in {0, 2})
    assert g.symbol(0) is None
    assert g.symbol(1) == "a"
    assert g.symbol(2) == "b"


def test_make_node_automaton_constructor():
    class MyAutomaton(NodeAutomaton):
        pass
    g = make_node_automaton([])
    assert isinstance(g, NodeAutomaton)
    assert not isinstance(g, MyAutomaton)
    g = make_node_automaton([], Constructor=MyAutomaton)
    assert isinstance(g, NodeAutomaton)
    assert isinstance(g, MyAutomaton)
